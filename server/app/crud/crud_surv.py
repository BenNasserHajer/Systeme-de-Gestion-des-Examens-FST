"""Data-access functions for surveillance."""

from sqlalchemy.orm import Session

from app.models.surveillance import Surveillance
from app.schemas.surveillance import SurveillanceCreate


def list_surveillances(db: Session) -> list[Surveillance]:
    return db.query(Surveillance).order_by(Surveillance.id.desc()).all()


def create_surveillance(db: Session, payload: SurveillanceCreate) -> Surveillance:
    db_item = Surveillance(
        planification_id=payload.planification_id,
        enseignant=payload.enseignant,
        charge=payload.charge,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
