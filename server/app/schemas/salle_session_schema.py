"""Pydantic schemas for Salle, Creneau, Session."""

from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class SalleBase(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    designation: str | None = Field(default=None, max_length=100)
    capacite: int = Field(ge=1)
    batiment: str | None = Field(default=None, max_length=50)


class SalleCreate(SalleBase):
    pass


class SalleUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=30)
    designation: str | None = None
    capacite: int | None = Field(default=None, ge=1)
    batiment: str | None = None


class SalleOut(SalleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class CreneauBase(BaseModel):
    date: date
    heure_debut: time
    heure_fin: time
    libelle: str | None = Field(default=None, max_length=50)


class CreneauCreate(CreneauBase):
    pass


class CreneauOut(CreneauBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SessionBase(BaseModel):
    type_session: str = Field(min_length=1, max_length=50)
    annee_universitaire: str = Field(min_length=1, max_length=10)
    date_debut: date
    date_fin: date
    statut: str = Field(default="BROUILLON", max_length=24)


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    type_session: str | None = Field(default=None, min_length=1, max_length=50)
    annee_universitaire: str | None = Field(default=None, min_length=1, max_length=10)
    date_debut: date | None = None
    date_fin: date | None = None
    statut: str | None = Field(default=None, max_length=24)


class SessionOut(SessionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
