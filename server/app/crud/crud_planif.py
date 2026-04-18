"""Data-access functions for planification."""

from sqlalchemy.orm import Session

from app.models.planification import Planification
from app.schemas.planification import PlanificationCreate


def list_planifications(db: Session) -> list[Planification]:
    return db.query(Planification).order_by(Planification.id.desc()).all()


def create_planification(db: Session, payload: PlanificationCreate) -> Planification:
    db_item = Planification(
        matiere=payload.matiere,
        salle=payload.salle,
        date_examen=payload.date_examen,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
