from datetime import date, time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import decouper_en_groupes, generer
from app.crud.crud_planif import (
    create_planification,
    ensure_planif_creneau,
    get_emploi_du_temps,
    get_salles_disponibles,
)
from app.models.salle_session import Creneau
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


def test_generation_filtre_semestre_scope_et_pref_departement() -> None:
    db = _db_session()
    try:
        req = GenerationRequest(
            session_id=10,
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            semestre="S1",
            scope_section_ids=[1],
            mode=ModeAffectation.AUTO,
            tasks=[
                GenerationTask(
                    section_id=1,
                    section_matiere_id=300,
                    matiere_id=30,
                    matiere="Mat-S1",
                    semestre="S1",
                    section_departement_id=1,
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=20,
                    coefficient=2.0,
                ),
                GenerationTask(
                    section_id=2,
                    section_matiere_id=301,
                    matiere_id=31,
                    matiere="Mat-S2",
                    semestre="S2",
                    section_departement_id=2,
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=20,
                    coefficient=1.0,
                ),
            ],
            creneaux=[
                GenerationCreneau(
                    date_examen=date(2026, 6, 2),
                    heure_debut=time(8, 30),
                    heure_fin=time(10, 30),
                )
            ],
            salles=[
                GenerationSalle(salle_id="D2", capacite=30, batiment="B", departement_id=2),
                GenerationSalle(salle_id="SH", capacite=30, batiment="B", departement_id=None),
                GenerationSalle(salle_id="D1", capacite=30, batiment="B", departement_id=1),
            ],
        )

        creates, result = generer(req, build_default_engine(), [], db)

        assert result.nb_conflits == 0
        assert len(creates) == 1
        assert creates[0].section_id == 1
        assert creates[0].section_matiere_id == 300
        assert creates[0].salles[0].salle_id == "D1"
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


def test_salles_disponibles_exclut_salle_occupee() -> None:
    db = _db_session()
    try:
        slot_date = date(2026, 6, 12)
        slot_time = time(9, 0)
        base = dict(
            session_id=1,
            section_id=1,
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=slot_date,
            heure_debut=slot_time,
            heure_fin=time(11, 0),
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            duree=120,
            section_nb_etudiants=20,
            nb_groupes=1,
        )
        create_planification(
            db,
            PlanificationCreate(
                **base,
                section_matiere_id=10,
                matiere="Algo",
                salles=[
                    PlanifSalleAssign(
                        salle_id="INF-15",
                        salle_capacite=30,
                        salle_batiment="B",
                        groupe_id=1,
                        groupe_effectif=20,
                    )
                ],
            ),
        )

        from app.services.catalogue_service import SAMPLE_SALLES

        all_ids = {str(s["salle_id"]) for s in SAMPLE_SALLES}
        disponibles = get_salles_disponibles(
            db,
            date_examen=slot_date,
            heure_debut=slot_time,
            capacite_min=1,
        )
        libres = [s for s in disponibles if s.get("disponible")]
        occupees = [s for s in disponibles if not s.get("disponible")]
        libre_ids = {str(s["salle_id"]) for s in libres}
        assert "INF-15" not in libre_ids
        assert any(str(s["salle_id"]) == "INF-15" for s in occupees)
        assert len(libre_ids) >= len(all_ids) - 1
    finally:
        db.close()


def test_ensure_creneau_id_on_validate() -> None:
    db = _db_session()
    try:
        payload = PlanificationCreate(
            session_id=1,
            section_id=1,
            section_matiere_id=10,
            matiere="Algo",
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=date(2026, 6, 10),
            heure_debut=time(8, 0),
            heure_fin=time(10, 0),
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
        planif = create_planification(db, payload)
        assert planif.creneau_id is not None

        planif.creneau_id = None
        db.commit()
        db.refresh(planif)
        assert planif.creneau_id is None

        ensure_planif_creneau(db, planif)
        db.commit()
        db.refresh(planif)
        assert planif.creneau_id is not None
        assert db.query(Creneau).filter(Creneau.id == planif.creneau_id).count() == 1
    finally:
        db.close()


def test_max_deux_examens_par_jour_section() -> None:
    """A section cannot have more than 2 exams on the same day (default)."""
    db = _db_session()
    try:
        same_day = date(2026, 6, 10)
        base_kwargs = dict(
            session_id=1,
            section_id=1,
            type_epreuve=TypeEpreuve.EXAMEN_FINAL,
            mode_affectation=ModeAffectation.MANUEL,
            date_examen=same_day,
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

        create_planification(
            db,
            PlanificationCreate(
                **base_kwargs,
                section_matiere_id=10,
                matiere="Algo",
                heure_debut=time(8, 0),
                heure_fin=time(10, 0),
            ),
        )
        create_planification(
            db,
            PlanificationCreate(
                **base_kwargs,
                section_matiere_id=11,
                matiere="BDD",
                heure_debut=time(11, 0),
                heure_fin=time(13, 0),
            ),
        )

        third = PlanificationCreate(
            **base_kwargs,
            section_matiere_id=12,
            matiere="Reseaux",
            heure_debut=time(14, 0),
            heure_fin=time(16, 0),
        )
        errors, _warnings = build_default_engine().verifier_toutes(
            third,
            {
                "existing_planifs": db.query(Planification).all(),
                "max_examens_par_jour": 2,
            },
            db,
        )
        assert any("2 examens" in item for item in errors)

        other_day = date(2026, 6, 11)
        req = GenerationRequest(
            session_id=5,
            session_date_debut=date(2026, 6, 1),
            session_date_fin=date(2026, 6, 30),
            session_statut=StatutSession.BROUILLON,
            semestre="S1",
            mode=ModeAffectation.AUTO,
            tasks=[
                GenerationTask(
                    section_id=1,
                    section_matiere_id=100 + i,
                    matiere_id=i,
                    matiere=f"Mat-{i}",
                    semestre="S1",
                    type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                    duree=120,
                    section_nb_etudiants=20,
                    coefficient=1.0,
                    a_examen_final=True,
                    a_ds=True,
                )
                for i in range(1, 4)
            ],
            creneaux=[
                GenerationCreneau(
                    date_examen=same_day,
                    heure_debut=time(8, 0),
                    heure_fin=time(10, 0),
                ),
                GenerationCreneau(
                    date_examen=same_day,
                    heure_debut=time(11, 0),
                    heure_fin=time(13, 0),
                ),
                GenerationCreneau(
                    date_examen=other_day,
                    heure_debut=time(8, 0),
                    heure_fin=time(10, 0),
                ),
            ],
            salles=[GenerationSalle(salle_id="S30", capacite=30, batiment="A")],
        )
        creates, result = generer(
            req,
            build_default_engine(),
            [],
            db,
            known_section_matiere_ids={101, 102, 103},
        )
        dates = [c.date_examen for c in creates]
        assert len(creates) == 3
        assert dates.count(same_day) == 2
        assert dates.count(other_day) == 1
    finally:
        db.close()
