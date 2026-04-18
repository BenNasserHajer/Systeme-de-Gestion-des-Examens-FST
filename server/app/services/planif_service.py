"""Business logic for planification module."""

from sqlalchemy.orm import Session

from app.algorithms.contraintes import validate_planification_constraints
from app.algorithms.planif_auto import build_auto_planification
from app.crud.crud_planif import create_planification, list_planifications
from app.models.planification import Planification
from app.schemas.planification import PlanificationCreate


class PlanifService:
    """Contains all planification business rules."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Planification]:
        return list_planifications(self.db)

    def create(self, payload: PlanificationCreate) -> Planification:
        validate_planification_constraints(payload)
        return create_planification(self.db, payload)

    def create_auto(self, payload: PlanificationCreate) -> Planification:
        auto_payload = build_auto_planification(payload)
        validate_planification_constraints(auto_payload)
        return create_planification(self.db, auto_payload)
