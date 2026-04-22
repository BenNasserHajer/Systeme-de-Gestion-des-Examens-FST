"""CRUD operations for surveillance module."""

from datetime import datetime
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, selectinload

from app.models.surveillance import Surveillance
from app.models.enseignant import Enseignant
from app.models.planification_examen import PlanificationExamen
from app.schemas.surveillance_schema import (
    SurveillanceCreate,
    SurveillanceUpdate,
)


def _query_surveillance_base(db: Session):
    """Base query with relationships."""
    return db.query(Surveillance).options(
        selectinload(Surveillance.enseignant)
    )


# ============================================================================
# LIST & GET OPERATIONS
# ============================================================================


def list_surveillances(
    db: Session,
    *,
    planification_id: int | None = None,
    enseignant_id: int | None = None,
    session_id: int | None = None,
    est_externe: bool | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Surveillance]:
    """List surveillances with optional filters."""
    query = _query_surveillance_base(db)

    if planification_id is not None:
        query = query.filter(Surveillance.planification_id == planification_id)

    if enseignant_id is not None:
        query = query.filter(Surveillance.enseignant_id == enseignant_id)

    if est_externe is not None:
        query = query.filter(Surveillance.est_externe == est_externe)

    if session_id is not None:
        # Join with planification to filter by session
        from app.models.planification import Planification as Planif
        query = query.join(Planif).filter(Planif.session_id == session_id)

    return query.offset(skip).limit(limit).all()


def get_surveillance(db: Session, surveillance_id: int) -> Surveillance | None:
    """Get a single surveillance by ID."""
    return _query_surveillance_base(db).filter(Surveillance.id == surveillance_id).first()


def get_surveillances_for_planification(
    db: Session, planification_id: int
) -> list[Surveillance]:
    """Get all surveillances for a specific planification."""
    return (
        _query_surveillance_base(db)
        .filter(Surveillance.planification_id == planification_id)
        .all()
    )


def get_surveillances_for_enseignant(
    db: Session, 
    enseignant_id: int, 
    annee_universitaire: str | None = None
) -> list[Surveillance]:
    """Get all surveillances for a specific enseignant."""
    query = _query_surveillance_base(db).filter(
        Surveillance.enseignant_id == enseignant_id
    )
    
    # If academic year is specified, filter by session's academic year
    if annee_universitaire:
        from app.models.session import Session as SessionModel
        from app.models.planification import Planification as PlanifModel
        query = query.join(PlanifModel).join(SessionModel).filter(
            SessionModel.annee_universitaire == annee_universitaire
        )
    
    return query.all()


def get_surveillance_by_planif_and_enseignant(
    db: Session, planification_id: int, enseignant_id: int
) -> Surveillance | None:
    """Get surveillance by both planification and enseignant."""
    return (
        _query_surveillance_base(db)
        .filter(
            and_(
                Surveillance.planification_id == planification_id,
                Surveillance.enseignant_id == enseignant_id,
            )
        )
        .first()
    )


# ============================================================================
# CREATE OPERATIONS
# ============================================================================


def create_surveillance(db: Session, payload: SurveillanceCreate) -> Surveillance:
    """Create a new surveillance entry."""
    db_item = Surveillance(
        planification_id=payload.planification_id,
        enseignant_id=payload.enseignant_id,
        charge=payload.charge,
        mode_affectation=payload.mode_affectation.value,
        statut_surveillance=payload.statut_surveillance.value,
        est_externe=payload.est_externe,
        motif_externe=payload.motif_externe,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return get_surveillance(db, db_item.id) or db_item


def create_surveillances_batch(
    db: Session, 
    payloads: list[SurveillanceCreate]
) -> list[Surveillance]:
    """Create multiple surveillance entries in a transaction."""
    db_items = [
        Surveillance(
            planification_id=payload.planification_id,
            enseignant_id=payload.enseignant_id,
            charge=payload.charge,
            mode_affectation=payload.mode_affectation.value,
            statut_surveillance=payload.statut_surveillance.value,
            est_externe=payload.est_externe,
            motif_externe=payload.motif_externe,
        )
        for payload in payloads
    ]
    db.add_all(db_items)
    db.commit()
    
    # Refresh all items
    result = []
    for item in db_items:
        db.refresh(item)
        result.append(get_surveillance(db, item.id) or item)
    
    return result


# ============================================================================
# UPDATE OPERATIONS
# ============================================================================


def update_surveillance(
    db: Session, 
    surveillance: Surveillance, 
    payload: SurveillanceUpdate
) -> Surveillance:
    """Update a surveillance entry."""
    if payload.presence is not None:
        surveillance.presence = payload.presence

    if payload.statut_surveillance is not None:
        surveillance.statut_surveillance = payload.statut_surveillance.value

    if payload.charge is not None:
        surveillance.charge = payload.charge

    if payload.motif_externe is not None:
        surveillance.motif_externe = payload.motif_externe

    surveillance.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(surveillance)
    return get_surveillance(db, surveillance.id) or surveillance


# ============================================================================
# DELETE OPERATIONS
# ============================================================================


def delete_surveillance(db: Session, surveillance: Surveillance) -> None:
    """Delete a surveillance entry."""
    db.delete(surveillance)
    db.commit()


def delete_surveillance_by_id(db: Session, surveillance_id: int) -> bool:
    """Delete a surveillance entry by ID."""
    surveillance = get_surveillance(db, surveillance_id)
    if surveillance:
        delete_surveillance(db, surveillance)
        return True
    return False


def delete_surveillances_for_planification(
    db: Session, planification_id: int
) -> int:
    """Delete all surveillances for a planification and return count."""
    count = db.query(Surveillance).filter(
        Surveillance.planification_id == planification_id
    ).delete()
    db.commit()
    return count


# ============================================================================
# REPLACEMENT OPERATIONS
# ============================================================================


def replace_surveillance(
    db: Session,
    old_surveillance: Surveillance,
    new_enseignant_id: int,
    motif: str,
) -> tuple[Surveillance, Surveillance]:
    """Replace an enseignant on a surveillance."""
    # Store old surveillance details
    old_id = old_surveillance.id
    planification_id = old_surveillance.planification_id
    old_charge = old_surveillance.charge
    
    # Create new surveillance
    new_payload = SurveillanceCreate(
        planification_id=planification_id,
        enseignant_id=new_enseignant_id,
        charge=old_charge,
        mode_affectation=old_surveillance.mode_affectation,
        statut_surveillance=old_surveillance.statut_surveillance,
        est_externe=old_surveillance.est_externe,
        motif_externe=f"Remplacement: {motif}" if motif else old_surveillance.motif_externe,
    )
    
    new_surveillance = create_surveillance(db, new_payload)
    
    # Delete old surveillance
    delete_surveillance(db, old_surveillance)
    
    return (old_surveillance, new_surveillance)


# ============================================================================
# ANALYTICS & REPORTS
# ============================================================================


def get_surveillance_stats_for_session(
    db: Session, session_id: int
) -> dict:
    """Get surveillance statistics for a session."""
    from app.models.session import Session as SessionModel
    from app.models.planification import Planification as PlanifModel
    
    stats = db.query(
        func.count(Surveillance.id).label("total_surveillances"),
        func.sum(Surveillance.charge).label("total_hours"),
        func.count(func.distinct(Surveillance.enseignant_id)).label("unique_enseignants"),
        func.sum(func.cast(Surveillance.est_externe, db.Integer)).label("count_externes"),
    ).join(PlanifModel).join(SessionModel).filter(
        SessionModel.id == session_id
    ).first()

    return {
        "total_surveillances": stats.total_surveillances or 0,
        "total_hours": float(stats.total_hours or 0),
        "unique_enseignants": stats.unique_enseignants or 0,
        "count_externes": stats.count_externes or 0,
    }


def get_enseignant_charge_for_year(
    db: Session,
    enseignant_id: int,
    annee_universitaire: str,
) -> float:
    """Get total charge for an enseignant in a given academic year."""
    from app.models.session import Session as SessionModel
    from app.models.planification import Planification as PlanifModel
    
    result = db.query(func.coalesce(func.sum(Surveillance.charge), 0)).filter(
        Surveillance.enseignant_id == enseignant_id,
        Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
    ).join(PlanifModel).join(SessionModel).filter(
        SessionModel.annee_universitaire == annee_universitaire
    ).scalar()

    return float(result)


def count_surveillances_for_enseignant(
    db: Session,
    enseignant_id: int,
    annee_universitaire: str | None = None,
) -> int:
    """Count surveillances for an enseignant."""
    query = db.query(func.count(Surveillance.id)).filter(
        Surveillance.enseignant_id == enseignant_id,
        Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
    )

    if annee_universitaire:
        from app.models.session import Session as SessionModel
        from app.models.planification import Planification as PlanifModel
        query = query.join(PlanifModel).join(SessionModel).filter(
            SessionModel.annee_universitaire == annee_universitaire
        )

    return query.scalar() or 0


def get_conflicting_surveillances(
    db: Session,
    enseignant_id: int,
    date: str,
    heure_debut: str,
    heure_fin: str,
) -> list[Surveillance]:
    """Get surveillances that conflict with given time."""
    from app.models.creneau import Creneau
    from app.models.planification import Planification as PlanifModel
    
    return (
        _query_surveillance_base(db)
        .join(PlanifModel)
        .join(Creneau)
        .filter(
            Surveillance.enseignant_id == enseignant_id,
            Creneau.date == date,
            Creneau.heure_debut < heure_fin,
            Creneau.heure_fin > heure_debut,
        )
        .all()
    )
