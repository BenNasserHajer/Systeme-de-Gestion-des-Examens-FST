"""Data-access functions for salle (rooms)."""

from sqlalchemy.orm import Session

from app.models.salle_session import Salle
from app.schemas.salle_session_schema import SalleCreate, SalleUpdate


def list_salles(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
) -> list[Salle]:
    """List all salles with pagination."""
    return db.query(Salle).order_by(Salle.code.asc()).offset(skip).limit(limit).all()


def get_salle(db: Session, salle_id: int) -> Salle | None:
    """Get a single salle by ID."""
    return db.query(Salle).filter(Salle.id == salle_id).first()


def get_salle_by_code(db: Session, code: str) -> Salle | None:
    """Get a single salle by code."""
    return db.query(Salle).filter(Salle.code == code).first()


def create_salle(db: Session, payload: SalleCreate) -> Salle:
    """Create a new salle."""
    db_item = Salle(
        code=payload.code,
        designation=payload.designation,
        capacite=payload.capacite,
        batiment=payload.batiment,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_salle(db: Session, salle: Salle, payload: SalleUpdate) -> Salle:
    """Update an existing salle."""
    if payload.code is not None:
        salle.code = payload.code
    if payload.designation is not None:
        salle.designation = payload.designation
    if payload.capacite is not None:
        salle.capacite = payload.capacite
    if payload.batiment is not None:
        salle.batiment = payload.batiment
    
    db.commit()
    db.refresh(salle)
    return salle


def delete_salle(db: Session, salle: Salle) -> None:
    """Delete a salle."""
    db.delete(salle)
    db.commit()
