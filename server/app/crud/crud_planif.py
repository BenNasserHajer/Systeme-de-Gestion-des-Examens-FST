"""Data-access functions for planification."""

from datetime import date, time

from sqlalchemy.orm import Session, selectinload

from app.models.planification import PlanifSalle, Planification
from app.models.salle_session import Creneau
from app.schemas.planification import PlanifSalleAssign, PlanificationCreate, PlanificationUpdate
from app.services.catalogue_service import SAMPLE_SALLES, list_salles_referentiel


def _query_planification_base(db: Session):
    return db.query(Planification).options(selectinload(Planification.salles_affectees))


def list_planifications(
    db: Session,
    *,
    session_id: int | None = None,
    section_id: int | None = None,
    date_examen: date | None = None,
    type_epreuve: str | None = None,
    statut: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Planification]:
    query = _query_planification_base(db)
    if session_id is not None:
        query = query.filter(Planification.session_id == session_id)
    if section_id is not None:
        query = query.filter(Planification.section_id == section_id)
    if date_examen is not None:
        query = query.filter(Planification.date_examen == date_examen)
    if type_epreuve is not None:
        query = query.filter(Planification.type_epreuve == type_epreuve)
    if statut is not None:
        query = query.filter(Planification.statut == statut)

    return (
        query.order_by(Planification.date_examen.asc(), Planification.heure_debut.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_planification(db: Session, planif_id: int) -> Planification | None:
    return _query_planification_base(db).filter(Planification.id == planif_id).first()


def list_existing_for_session(db: Session, session_id: int) -> list[Planification]:
    return _query_planification_base(db).filter(Planification.session_id == session_id).all()


def _find_or_create_creneau(
    db: Session,
    date_examen: date,
    heure_debut: time,
    heure_fin: time,
) -> int:
    """
    Find existing creneau by (date, heure_debut) — matches DB unique key — or create one.
    Updates heure_fin when an existing row is reused.
    """
    existing = (
        db.query(Creneau)
        .filter(
            Creneau.date == date_examen,
            Creneau.heure_debut == heure_debut,
        )
        .first()
    )

    if existing:
        if existing.heure_fin != heure_fin:
            existing.heure_fin = heure_fin
            db.flush()
        return existing.id

    new_creneau = Creneau(
        date=date_examen,
        heure_debut=heure_debut,
        heure_fin=heure_fin,
        libelle=None,
    )
    db.add(new_creneau)
    db.flush()
    return new_creneau.id


def ensure_planif_creneau(db: Session, planif: Planification) -> None:
    """Backfill creneau_id when missing (legacy rows or validate-only updates)."""
    if planif.creneau_id is not None:
        return
    planif.creneau_id = _find_or_create_creneau(
        db,
        planif.date_examen,
        planif.heure_debut,
        planif.heure_fin,
    )


def _build_planif_salle_rows(
    planif: Planification,
    salles: list[PlanifSalleAssign],
) -> list[PlanifSalle]:
    return [
        PlanifSalle(
            planification_id=planif.id,
            salle_id=item.salle_id,
            salle_capacite=item.salle_capacite,
            salle_batiment=item.salle_batiment,
            salle_departement_id=item.salle_departement_id,
            groupe_id=item.groupe_id,
            groupe_effectif=item.groupe_effectif,
            creneau_date=planif.date_examen,
            heure_debut=planif.heure_debut,
        )
        for item in salles
    ]


def create_planification(db: Session, payload: PlanificationCreate) -> Planification:
    # Convert semestre string to integer (S1 -> 1, S2 -> 2)
    semestre_int = 1 if payload.semestre.upper() in ("S1", "1") else 2
    
    # Find or create matching creneau
    creneau_id = _find_or_create_creneau(
        db,
        payload.date_examen,
        payload.heure_debut,
        payload.heure_fin,
    )
    
    db_item = Planification(
        session_id=payload.session_id,
        section_id=payload.section_id,
        section_matiere_id=payload.section_matiere_id,
        section_departement_id=payload.section_departement_id,
        matiere=payload.matiere,
        type_epreuve=payload.type_epreuve.value,
        semestre=semestre_int,
        creneau_id=creneau_id,  # Set the creneau_id
        date_examen=payload.date_examen,
        heure_debut=payload.heure_debut,
        heure_fin=payload.heure_fin,
        session_date_debut=payload.session_date_debut,
        session_date_fin=payload.session_date_fin,
        session_statut=payload.session_statut.value,
        duree=payload.duree,
        coefficient=payload.coefficient,
        section_nb_etudiants=payload.section_nb_etudiants,
        mode_affectation=payload.mode_affectation.value,
        statut=payload.statut.value,
        nb_groupes=payload.nb_groupes,
        nb_surveillants_requis=payload.nb_surveillants_requis,
        a_examen_final=payload.a_examen_final,
        a_ds=payload.a_ds,
    )
    db.add(db_item)
    db.flush()

    if payload.salles:
        db.add_all(_build_planif_salle_rows(db_item, payload.salles))

    db.commit()
    db.refresh(db_item)
    return get_planification(db, db_item.id) or db_item


def update_planification(db: Session, planif: Planification, payload: PlanificationUpdate) -> Planification:
    if payload.date_examen is not None or payload.heure_debut is not None or payload.heure_fin is not None:
        new_date = payload.date_examen if payload.date_examen is not None else planif.date_examen
        new_heure_debut = payload.heure_debut if payload.heure_debut is not None else planif.heure_debut
        new_heure_fin = payload.heure_fin if payload.heure_fin is not None else planif.heure_fin

        planif.creneau_id = _find_or_create_creneau(db, new_date, new_heure_debut, new_heure_fin)
    else:
        ensure_planif_creneau(db, planif)
    
    if payload.date_examen is not None:
        planif.date_examen = payload.date_examen
    if payload.heure_debut is not None:
        planif.heure_debut = payload.heure_debut
    if payload.heure_fin is not None:
        planif.heure_fin = payload.heure_fin
    if payload.statut is not None:
        planif.statut = payload.statut.value
    if payload.mode_affectation is not None:
        planif.mode_affectation = payload.mode_affectation.value
    if payload.duree is not None:
        planif.duree = payload.duree
    if payload.nb_groupes is not None:
        planif.nb_groupes = payload.nb_groupes
    if payload.nb_surveillants_requis is not None:
        planif.nb_surveillants_requis = payload.nb_surveillants_requis

    if payload.salles is not None:
        db.query(PlanifSalle).filter(PlanifSalle.planification_id == planif.id).delete()
        db.flush()
        if payload.salles:
            db.add_all(_build_planif_salle_rows(planif, payload.salles))

    db.commit()
    db.refresh(planif)
    return get_planification(db, planif.id) or planif


def replace_planif_salles(db: Session, planif: Planification, salles: list[PlanifSalleAssign]) -> Planification:
    db.query(PlanifSalle).filter(PlanifSalle.planification_id == planif.id).delete()
    db.flush()
    if salles:
        db.add_all(_build_planif_salle_rows(planif, salles))
        planif.nb_groupes = len(salles)
    db.commit()
    db.refresh(planif)
    return get_planification(db, planif.id) or planif


def delete_planification(db: Session, planif: Planification) -> None:
    db.delete(planif)
    db.commit()


def get_emploi_du_temps(db: Session, session_id: int) -> list[Planification]:
    return get_emploi_du_temps_filtre(db, session_id=session_id)


def get_emploi_du_temps_filtre(
    db: Session,
    *,
    session_id: int,
    section_id: int | None = None,
    type_epreuve: str | None = None,
    statut: str | None = None,
) -> list[Planification]:
    query = _query_planification_base(db).filter(Planification.session_id == session_id)

    if section_id is not None:
        query = query.filter(Planification.section_id == section_id)
    if type_epreuve is not None:
        query = query.filter(Planification.type_epreuve == type_epreuve)
    if statut is not None:
        query = query.filter(Planification.statut == statut)

    return query.order_by(Planification.date_examen.asc(), Planification.heure_debut.asc(), Planification.id.asc()).all()


def get_salles_disponibles(
    db: Session,
    *,
    date_examen: date,
    heure_debut: time,
    capacite_min: int = 1,
    exclude_planif_id: int | None = None,
    toutes_les_salles: bool = True,
) -> list[dict[str, object]]:
    """
    Liste les salles du referentiel avec statut de disponibilite sur le creneau.
    Si toutes_les_salles=True, retourne aussi les salles occupees (disponible=False).
    capacite_min ne filtre que lorsque toutes_les_salles=False.
    """
    all_salles = list_salles_referentiel(db)
    if not all_salles:
        all_salles = list(SAMPLE_SALLES)

    occupied_query = db.query(PlanifSalle.salle_id).filter(
        PlanifSalle.creneau_date == date_examen,
        PlanifSalle.heure_debut == heure_debut,
    )
    if exclude_planif_id is not None:
        occupied_query = occupied_query.filter(
            PlanifSalle.planification_id != exclude_planif_id,
        )
    occupied = {row[0] for row in occupied_query.distinct().all()}

    result: list[dict[str, object]] = []
    for salle in all_salles:
        capacite = int(salle.get("capacite", 0))
        salle_id = str(salle["salle_id"])
        is_occupied = salle_id in occupied
        libre = not is_occupied

        if not toutes_les_salles:
            if not libre or capacite < capacite_min:
                continue
        elif not libre:
            result.append(
                {
                    "salle_id": salle_id,
                    "capacite": capacite,
                    "batiment": salle.get("batiment") or None,
                    "disponible": False,
                    "motif_indisponible": "Occupee sur ce creneau",
                }
            )
            continue

        result.append(
            {
                "salle_id": salle_id,
                "capacite": capacite,
                "batiment": salle.get("batiment") or None,
                "disponible": True,
                "motif_indisponible": None,
            }
        )

    result.sort(
        key=lambda item: (
            0 if item.get("disponible") else 1,
            -int(item["capacite"]),
            str(item["salle_id"]),
        )
    )
    return result
