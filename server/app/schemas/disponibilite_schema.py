"""Pydantic schemas for DisponibiliteEnseignant."""

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class DisponibiliteEnseignantBase(BaseModel):
    enseignant_id: int = Field(ge=1)
    date: date
    heure_debut: time
    heure_fin: time
    type_dispo: str = Field(min_length=1, max_length=50, default="INDISPONIBLE")
    motif: str | None = Field(default=None, max_length=200)
    confirme: bool = True


class DisponibiliteEnseignantCreate(DisponibiliteEnseignantBase):
    pass


class DisponibiliteEnseignantOut(DisponibiliteEnseignantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
