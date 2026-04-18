"""Automatic planification algorithms."""

from app.schemas.planification import PlanificationCreate


def build_auto_planification(payload: PlanificationCreate) -> PlanificationCreate:
    """Return an adjusted payload for auto-generated draft planifications."""
    return PlanificationCreate(
        matiere=payload.matiere,
        salle=payload.salle,
        date_examen=payload.date_examen,
    )
