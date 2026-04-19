"""Planification endpoints. Keep business logic in services."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.planification import (
    GenerationRequest,
    GenerationResult,
    PlanifSalleAssign,
    PlanificationCreate,
    PlanificationOut,
    PlanificationUpdate,
)
from app.services.planif_service import (
    ConstraintViolationError,
    PlanifService,
    PlanificationNotFoundError,
)

router = APIRouter()


def _to_out(item) -> PlanificationOut:
    return PlanificationOut(
        id=item.id,
        session_id=item.session_id,
        section_id=item.section_id,
        section_matiere_id=item.section_matiere_id,
        matiere=item.matiere,
        type_epreuve=item.type_epreuve,
        mode_affectation=item.mode_affectation,
        statut=item.statut,
        date_examen=item.date_examen,
        heure_debut=item.heure_debut,
        heure_fin=item.heure_fin,
        session_date_debut=item.session_date_debut,
        session_date_fin=item.session_date_fin,
        session_statut=item.session_statut,
        duree=item.duree,
        coefficient=item.coefficient,
        section_nb_etudiants=item.section_nb_etudiants,
        nb_groupes=item.nb_groupes,
        nb_surveillants_requis=item.nb_surveillants_requis,
        created_at=item.created_at,
        updated_at=item.updated_at,
        salles=item.salles_affectees,
    )


@router.get("/planifications", response_model=list[PlanificationOut])
@router.get("/planifications/", response_model=list[PlanificationOut])
def get_planifications(
    session_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    date_examen: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[PlanificationOut]:
    service = PlanifService(db)
    return [
        _to_out(x)
        for x in service.get_all(
            session_id=session_id,
            section_id=section_id,
            date_examen=date_examen,
            skip=skip,
            limit=limit,
        )
    ]


@router.get("/planifications/{planif_id}", response_model=PlanificationOut)
def get_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        return _to_out(service.get_by_id(planif_id))
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/planifications", response_model=PlanificationOut, status_code=status.HTTP_201_CREATED)
def create_planification(
    payload: PlanificationCreate,
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        created, _warnings = service.create(payload)
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(created)


@router.put("/planifications/{planif_id}", response_model=PlanificationOut)
def update_planification(
    planif_id: int,
    payload: PlanificationUpdate,
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated, _warnings = service.update(planif_id, payload)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(updated)


@router.delete("/planifications/{planif_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planification(planif_id: int, db: Session = Depends(get_db)) -> Response:
    service = PlanifService(db)
    try:
        service.delete(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/generer", response_model=GenerationResult)
def generer_planifications(
    session_id: int,
    payload: GenerationRequest,
    db: Session = Depends(get_db),
) -> GenerationResult:
    service = PlanifService(db)
    request = payload.model_copy(update={"session_id": session_id})
    return service.generer_planifications(request)


@router.post("/planifications/{planif_id}/salles", response_model=PlanificationOut)
def affecter_salles_manuel(
    planif_id: int,
    salles: list[PlanifSalleAssign],
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated, _warnings = service.affecter_salles_manuel(planif_id, salles)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(updated)


@router.get("/sessions/{session_id}/emploi-du-temps", response_model=list[PlanificationOut])
def get_emploi_du_temps(session_id: int, db: Session = Depends(get_db)) -> list[PlanificationOut]:
    service = PlanifService(db)
    return [_to_out(x) for x in service.get_emploi_du_temps(session_id)]


@router.post("/planifications/{planif_id}/valider", response_model=PlanificationOut)
def valider_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.valider_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)


@router.post("/planifications/{planif_id}/publier", response_model=PlanificationOut)
def publier_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.publier_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)
