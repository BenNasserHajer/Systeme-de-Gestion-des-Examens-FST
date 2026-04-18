"""Pydantic schemas for planification endpoints."""

from datetime import date, datetime
from pydantic import BaseModel, Field


class PlanificationBase(BaseModel):
    matiere: str = Field(min_length=2, max_length=120)
    salle: str = Field(min_length=1, max_length=80)
    date_examen: date


class PlanificationCreate(PlanificationBase):
    pass


class PlanificationRead(PlanificationBase):
    id: int
    statut: str
    created_at: datetime

    class Config:
        orm_mode = True
