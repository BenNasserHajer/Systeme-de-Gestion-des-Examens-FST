from datetime import date, time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import decouper_en_groupes, generer
from app.crud.crud_planif import create_planification, get_emploi_du_temps
from app.database import Base
from app.models.planification import Planification
from app.schemas.planification import (
    GenerationCreneau,
    GenerationRequest,
    GenerationSalle,
    GenerationTask,
    ModeAffectation,
    PlanifSalleAssign,
    PlanificationCreate,
    StatutSession,
    TypeEpreuve,
)


def _db_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return LocalSession()


def test_decoupage_groupes_equilibre() -> None:
    groupes = decouper_en_groupes(effectif_total=35, capacite_cible=20)
    assert groupes == [18, 17]
    assert max(groupes) - min(groupes) <= 1


def test_contrainte_salle_occupee_detectee() -> None:
    db = _db_session()
    try:
        base = PlanificationCreate(
            session_id=1,
            section_id=1,
            section_matiere_id=10,
            matiere="Algo",
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=date(2026, 6, 2),
            heure_debut=time(8, 30),
            heure_fin=time(10, 30),
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            duree=120,
            section_nb_etudiants=20,
            nb_groupes=1,
            salles=[
                PlanifSalleAssign(
                    salle_id="S22",
                    salle_capacite=30,
                    salle_batiment="A",
                    groupe_id=1,
                    groupe_effectif=20,
                )
            ],
        )
        create_planification(db, base)

        conflict = PlanificationCreate(
            session_id=1,
            section_id=2,
            section_matiere_id=11,
            matiere="BDD",
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=date(2026, 6, 2),
            heure_debut=time(8, 30),
            heure_fin=time(10, 30),
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            duree=120,
            section_nb_etudiants=18,
            nb_groupes=1,
            salles=[
                PlanifSalleAssign(
                    salle_id="S22",
                    salle_capacite=30,
                    salle_batiment="A",
                    groupe_id=1,
                    groupe_effectif=18,
                )
            ],
        )

        errors, _warnings = build_default_engine().verifier_toutes(
            conflict,
            {"existing_planifs": db.query(Planification).all()},
            db,
        )
        assert any("C1" in item for item in errors)
    finally:
        db.close()


def test_generation_simple_et_split_best_effort() -> None:
    db = _db_session()
    try:
        req = GenerationRequest(
            session_id=1,
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            mode=ModeAffectation.AUTO,
            tasks=[
                GenerationTask(
                    section_id=1,
                    section_matiere_id=100,
                    matiere="Mat-Grand",
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=35,
                    coefficient=2.0,
                ),
                GenerationTask(
                    section_id=2,
                    section_matiere_id=101,
                    matiere="Mat-Petite",
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=15,
                    coefficient=1.0,
                ),
                GenerationTask(
                    section_id=3,
                    section_matiere_id=102,
                    matiere="Mat-Impossible",
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=80,
                    coefficient=3.0,
                ),
            ],
            creneaux=[
                GenerationCreneau(date_examen=date(2026, 6, 2), heure_debut=time(8, 30), heure_fin=time(10, 30)),
                GenerationCreneau(date_examen=date(2026, 6, 2), heure_debut=time(11, 0), heure_fin=time(13, 0)),
            ],
            salles=[
                GenerationSalle(salle_id="S20A", capacite=20, batiment="A"),
                GenerationSalle(salle_id="S20B", capacite=20, batiment="A"),
                GenerationSalle(salle_id="S30", capacite=30, batiment="B"),
            ],
        )

        creates, result = generer(req, build_default_engine(), [], db)
        assert result.nb_crees == 2
        assert result.nb_conflits >= 1

        grande = next(c for c in creates if c.matiere == "Mat-Grand")
        assert grande.nb_groupes == 2
        assert len(grande.salles) == 2

        for payload in creates:
            create_planification(db, payload)

        rows = db.query(Planification).all()
        assert len(rows) == 2
    finally:
        db.close()


def test_emploi_du_temps_trie() -> None:
    db = _db_session()
    try:
        p1 = PlanificationCreate(
            session_id=2,
            section_id=1,
            section_matiere_id=200,
            matiere="Algo",
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=date(2026, 6, 4),
            heure_debut=time(11, 0),
            heure_fin=time(13, 0),
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            duree=120,
            section_nb_etudiants=20,
            salles=[
                PlanifSalleAssign(
                    salle_id="S22",
                    salle_capacite=30,
                    groupe_id=1,
                    groupe_effectif=20,
                )
            ],
        )
        p2 = PlanificationCreate(
            session_id=2,
            section_id=1,
            section_matiere_id=201,
            matiere="BDD",
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=date(2026, 6, 3),
            heure_debut=time(8, 30),
            heure_fin=time(10, 30),
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            duree=120,
            section_nb_etudiants=20,
            salles=[
                PlanifSalleAssign(
                    salle_id="S31",
                    salle_capacite=30,
                    groupe_id=1,
                    groupe_effectif=20,
                )
            ],
        )
        create_planification(db, p1)
        create_planification(db, p2)

        emploi = get_emploi_du_temps(db, session_id=2)
        assert len(emploi) == 2
        assert emploi[0].date_examen <= emploi[1].date_examen
    finally:
        db.close()
