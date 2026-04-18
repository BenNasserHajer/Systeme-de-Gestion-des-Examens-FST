"""Constraint helpers for automatic planning routines."""

from app.schemas.planification import PlanificationCreate


def validate_planification_constraints(payload: PlanificationCreate) -> None:
    """Raise ValueError when basic planning constraints are violated."""
    if payload.matiere.strip() == "":
        raise ValueError("matiere is required")
    if payload.salle.strip() == "":
        raise ValueError("salle is required")
