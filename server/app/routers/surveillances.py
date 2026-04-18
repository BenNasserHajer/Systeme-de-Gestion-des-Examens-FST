"""Surveillance endpoints. Keep business logic in services."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.surveillance import SurveillanceCreate, SurveillanceRead
from app.services.charge_service import ChargeService
from app.services.surv_service import SurvService

router = APIRouter()


@router.get("/", response_model=list[SurveillanceRead])
def get_surveillances(db: Session = Depends(get_db)) -> list[SurveillanceRead]:
    service = SurvService(db)
    return service.get_all()


@router.post("/", response_model=SurveillanceRead)
def create_surveillance(
    payload: SurveillanceCreate,
    db: Session = Depends(get_db),
) -> SurveillanceRead:
    service = SurvService(db)
    return service.create(payload)


@router.post("/auto", response_model=SurveillanceRead)
def create_surveillance_auto(
    payload: SurveillanceCreate,
    db: Session = Depends(get_db),
) -> SurveillanceRead:
    service = SurvService(db)
    return service.create_auto(payload)


@router.get("/charges", response_model=dict[str, float])
def get_charges(db: Session = Depends(get_db)) -> dict[str, float]:
    service = ChargeService(db)
    return service.compute_by_teacher()
