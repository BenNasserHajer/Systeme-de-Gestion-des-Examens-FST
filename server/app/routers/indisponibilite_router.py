"""
routers/indisponibilite_router.py
Routes pour la gestion des indisponibilités enseignant.
Accès réservé aux enseignants authentifiés.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.crud import crud_indisponibilite
from app.schemas.indisponibilite_schema import (
    IndisponibiliteCreate,
    IndisponibiliteUpdate,
    IndisponibiliteRead,
)
from app.utils.jwt_handler import get_current_user

router = APIRouter(prefix="/indisponibilites", tags=["Indisponibilités"])


def _get_enseignant_user(request: Request) -> dict:
    """
    Dépendance : vérifie que l'utilisateur est un ENSEIGNANT.
    Lève 403 sinon.
    """
    from fastapi import HTTPException, status
    user = get_current_user(request)
    if user.get("type") != "ENSEIGNANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux enseignants",
        )
    return user


# ─────────────────────────────────────────────────────────────
# GET /indisponibilites/enseignant/{enseignant_id}
# L'enseignant ne peut voir QUE ses propres indisponibilités
# ─────────────────────────────────────────────────────────────
@router.get("/enseignant/{enseignant_id}", response_model=list[IndisponibiliteRead])
def list_indisponibilites(
    enseignant_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    from fastapi import HTTPException, status
    user = _get_enseignant_user(request)

    # Un enseignant ne peut consulter que ses propres données
    if user.get("enseignant_id") != enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez consulter que vos propres indisponibilités",
        )

    return crud_indisponibilite.get_all_for_enseignant(db, enseignant_id)


# ─────────────────────────────────────────────────────────────
# POST /indisponibilites/
# ─────────────────────────────────────────────────────────────
@router.post("/", response_model=IndisponibiliteRead, status_code=201)
def create_indisponibilite(
    payload: IndisponibiliteCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    from fastapi import HTTPException, status
    user = _get_enseignant_user(request)

    # L'enseignant ne peut créer que pour lui-même
    if user.get("enseignant_id") != payload.enseignant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez déclarer que vos propres indisponibilités",
        )

    return crud_indisponibilite.create_indisponibilite(db, payload)


# ─────────────────────────────────────────────────────────────
# PUT /indisponibilites/{id}
# ─────────────────────────────────────────────────────────────
@router.put("/{indispo_id}", response_model=IndisponibiliteRead)
def update_indisponibilite(
    indispo_id: int,
    payload: IndisponibiliteUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _get_enseignant_user(request)
    return crud_indisponibilite.update_indisponibilite(
        db, indispo_id, payload, user["enseignant_id"]
    )


# ─────────────────────────────────────────────────────────────
# DELETE /indisponibilites/{id}
# ─────────────────────────────────────────────────────────────
@router.delete("/{indispo_id}", status_code=204)
def delete_indisponibilite(
    indispo_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user = _get_enseignant_user(request)
    crud_indisponibilite.delete_indisponibilite(db, indispo_id, user["enseignant_id"])