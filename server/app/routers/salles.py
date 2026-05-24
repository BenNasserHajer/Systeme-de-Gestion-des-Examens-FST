"""Salles (rooms) CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import crud_salle
from app.database import get_db
from app.schemas.salle_session_schema import SalleCreate, SalleOut, SalleUpdate

router = APIRouter()


@router.get("/salles", response_model=list[SalleOut])
def get_salles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[SalleOut]:
    """List all salles with pagination."""
    salles = crud_salle.list_salles(db, skip=skip, limit=limit)
    return [SalleOut.model_validate(s) for s in salles]


@router.get("/salles/{salle_id}", response_model=SalleOut)
def get_salle(
    salle_id: int,
    db: Session = Depends(get_db),
) -> SalleOut:
    """Get a single salle by ID."""
    salle = crud_salle.get_salle(db, salle_id)
    if not salle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salle with id {salle_id} not found",
        )
    return SalleOut.model_validate(salle)


@router.post("/salles", response_model=SalleOut, status_code=status.HTTP_201_CREATED)
def create_salle(
    payload: SalleCreate,
    db: Session = Depends(get_db),
) -> SalleOut:
    """Create a new salle."""
    # Check if code already exists
    existing = crud_salle.get_salle_by_code(db, payload.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Salle with code '{payload.code}' already exists",
        )
    
    try:
        salle = crud_salle.create_salle(db, payload)
        return SalleOut.model_validate(salle)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database constraint violation: {exc.orig}",
        ) from exc


@router.put("/salles/{salle_id}", response_model=SalleOut)
def update_salle(
    salle_id: int,
    payload: SalleUpdate,
    db: Session = Depends(get_db),
) -> SalleOut:
    """Update an existing salle."""
    salle = crud_salle.get_salle(db, salle_id)
    if not salle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salle with id {salle_id} not found",
        )
    
    # Check if new code conflicts with existing salle
    if payload.code and payload.code != salle.code:
        existing = crud_salle.get_salle_by_code(db, payload.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Salle with code '{payload.code}' already exists",
            )
    
    try:
        updated = crud_salle.update_salle(db, salle, payload)
        return SalleOut.model_validate(updated)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database constraint violation: {exc.orig}",
        ) from exc


@router.delete("/salles/{salle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salle(
    salle_id: int,
    db: Session = Depends(get_db),
) -> Response:
    """Delete a salle."""
    salle = crud_salle.get_salle(db, salle_id)
    if not salle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Salle with id {salle_id} not found",
        )
    
    try:
        crud_salle.delete_salle(db, salle)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete salle: it is referenced by other records. {exc.orig}",
        ) from exc
