"""Planification endpoints. Keep business logic in services."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.planification import PlanificationCreate, PlanificationRead
from app.services.planif_service import PlanifService

router = APIRouter()


@router.get("/", response_model=list[PlanificationRead])
def get_planifications(db: Session = Depends(get_db)) -> list[PlanificationRead]:
    service = PlanifService(db)
    return service.get_all()


@router.post("/", response_model=PlanificationRead)
def create_planification(
    payload: PlanificationCreate,
    db: Session = Depends(get_db),
) -> PlanificationRead:
    service = PlanifService(db)
    return service.create(payload)


@router.post("/auto", response_model=PlanificationRead)
def create_planification_auto(
    payload: PlanificationCreate,
    db: Session = Depends(get_db),
) -> PlanificationRead:
    service = PlanifService(db)
    return service.create_auto(payload)
