"""Pydantic schemas for surveillance endpoints."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SurveillanceBase(BaseModel):
    planification_id: int
    enseignant: str = Field(min_length=2, max_length=120)
    charge: float = Field(default=1.0, gt=0)


class SurveillanceCreate(SurveillanceBase):
    pass


class SurveillanceRead(SurveillanceBase):
    id: int
    statut: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
