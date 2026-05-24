"""Pydantic schemas for Enseignant, ChargeHoraire, Enseignement."""

from pydantic import BaseModel, ConfigDict, Field


class EnseignantBase(BaseModel):
    nom: str = Field(min_length=1, max_length=60)
    prenom: str = Field(min_length=1, max_length=60)
    grade: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=20)
    departement_id: int | None = None


class EnseignantCreate(EnseignantBase):
    pass


class EnseignantUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=60)
    prenom: str | None = Field(default=None, min_length=1, max_length=60)
    grade: str | None = None
    email: str | None = None
    telephone: str | None = None
    departement_id: int | None = None


class EnseignantOut(EnseignantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ChargeHoraireBase(BaseModel):
    enseignant_id: int = Field(ge=1)
    annee_univ: str = Field(min_length=1, max_length=10)
    volume_horaire: float = Field(ge=0.0, default=0.0)


class ChargeHoraireCreate(ChargeHoraireBase):
    pass


class ChargeHoraireOut(ChargeHoraireBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class EnseignementBase(BaseModel):
    enseignant_id: int = Field(ge=1)
    matiere_id: int = Field(ge=1)
    type_enseignement: str = Field(min_length=1, max_length=50)
    nb_heures: float = Field(ge=0.0, default=0.0)
    annee_sem: str | None = Field(default=None, max_length=20)


class EnseignementCreate(EnseignementBase):
    pass


class EnseignementOut(EnseignementBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
