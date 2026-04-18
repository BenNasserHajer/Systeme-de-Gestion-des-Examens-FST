"""Automatic surveillance algorithms."""

from app.schemas.surveillance import SurveillanceCreate


def build_auto_surveillance(payload: SurveillanceCreate) -> SurveillanceCreate:
    """Return adjusted surveillance payload based on assignment rules."""
    return SurveillanceCreate(
        planification_id=payload.planification_id,
        enseignant=payload.enseignant,
        charge=payload.charge,
    )
