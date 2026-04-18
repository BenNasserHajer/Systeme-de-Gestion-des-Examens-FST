"""Business logic for surveillance module."""

from sqlalchemy.orm import Session

from app.algorithms.surv_auto import build_auto_surveillance
from app.crud.crud_surv import create_surveillance, list_surveillances
from app.models.surveillance import Surveillance
from app.schemas.surveillance import SurveillanceCreate


class SurvService:
    """Contains all surveillance business rules."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Surveillance]:
        return list_surveillances(self.db)

    def create(self, payload: SurveillanceCreate) -> Surveillance:
        return create_surveillance(self.db, payload)

    def create_auto(self, payload: SurveillanceCreate) -> Surveillance:
        auto_payload = build_auto_surveillance(payload)
        return create_surveillance(self.db, auto_payload)
