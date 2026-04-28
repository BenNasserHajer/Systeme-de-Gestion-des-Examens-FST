"""Reference-data endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/salles", response_model=list[str])
def list_salles() -> list[str]:
    return ["S22", "AMPHI INFO", "S31"]


@router.get("/matieres", response_model=list[str])
def list_matieres() -> list[str]:
    return ["Optimisation Combinatoire", "Big Data", "Securite IOT"]
