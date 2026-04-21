"""Pydantic schemas for surveillance endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SurveillanceBase(BaseModel):
    planification_id: int = Field(ge=1)
    enseignant_id: int = Field(ge=1)
    charge: float = Field(default=1.0, gt=0)
    presence: bool = False
    mode_affectation: str = Field(default="AUTOMATIQUE", max_length=24)


class SurveillanceCreate(SurveillanceBase):
    pass


class SurveillanceUpdate(BaseModel):
    charge: float | None = Field(default=None, gt=0)
    presence: bool | None = None
    mode_affectation: str | None = None


class SurveillanceRead(SurveillanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
