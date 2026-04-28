"""Pydantic schemas for Departement, Niveau, Section, Groupe."""

from pydantic import BaseModel, ConfigDict, Field


class DepartementBase(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=20)


class DepartementCreate(DepartementBase):
    pass


class DepartementOut(DepartementBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class NiveauBase(BaseModel):
    libelle: str = Field(min_length=1, max_length=50)
    annee: int = Field(ge=1)
    type_formation: str = Field(min_length=1, max_length=50)
    departement_id: int = Field(ge=1)


class NiveauCreate(NiveauBase):
    pass


class NiveauOut(NiveauBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SectionBase(BaseModel):
    nom: str = Field(min_length=1, max_length=20)
    nb_etudiants: int = Field(ge=0, default=0)
    niveau_id: int = Field(ge=1)


class SectionCreate(SectionBase):
    pass


class SectionOut(SectionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GroupeBase(BaseModel):
    numero: int = Field(ge=1)
    effectif: int = Field(ge=0, default=0)
    section_id: int = Field(ge=1)


class GroupeCreate(GroupeBase):
    pass


class GroupeOut(GroupeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
