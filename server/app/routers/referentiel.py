"""Reference-data endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.catalogue_service import load_catalogue

router = APIRouter()


@router.get("/salles", response_model=list[str])
def list_salles(db: Session = Depends(get_db)) -> list[str]:
    catalogue = load_catalogue(db)
    return [s["salle_id"] for s in catalogue.get("salles", [])]


@router.get("/matieres", response_model=list[str])
def list_matieres(db: Session = Depends(get_db)) -> list[str]:
    catalogue = load_catalogue(db)
    matieres: set[str] = set()
    for section_matieres in catalogue.get("matieres_by_section", {}).values():
        for mat in section_matieres:
            matieres.add(mat["matiere"])
    return sorted(matieres)


@router.get("/catalogue")
def get_catalogue(db: Session = Depends(get_db)) -> dict:
    """Full referentiel for planification form (niveaux, sections, sessions, salles, creneaux)."""
    return load_catalogue(db)
