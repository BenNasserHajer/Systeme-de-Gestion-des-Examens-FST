"""Reference-data endpoints."""

from datetime import date, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.crud.crud_planif import get_salles_disponibles
from app.database import get_db
from app.schemas.planification import SalleDisponibleOut
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


@router.get("/salles-disponibles", response_model=list[SalleDisponibleOut])
def list_salles_disponibles(
    date_examen: date = Query(..., description="Date de l'examen (YYYY-MM-DD)"),
    heure_debut: time = Query(..., description="Heure de debut (HH:MM ou HH:MM:SS)"),
    capacite_min: int = Query(default=1, ge=1),
    exclude_planif_id: int | None = Query(default=None, ge=1),
    toutes_les_salles: bool = Query(
        default=True,
        description="Inclure toutes les salles du referentiel (occupees marquees indisponibles)",
    ),
    db: Session = Depends(get_db),
) -> list[SalleDisponibleOut]:
    """Salles du referentiel avec indicateur de disponibilite sur le creneau."""
    rows = get_salles_disponibles(
        db,
        date_examen=date_examen,
        heure_debut=heure_debut,
        capacite_min=capacite_min,
        exclude_planif_id=exclude_planif_id,
        toutes_les_salles=toutes_les_salles,
    )
    return [SalleDisponibleOut.model_validate(row) for row in rows]
