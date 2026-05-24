"""Pydantic schemas for Matiere & SectionMatiere."""

from pydantic import BaseModel, ConfigDict, Field


class MatiereBase(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    intitule: str = Field(min_length=1, max_length=150)
    coefficient: float = Field(gt=0, default=1.0)
    credit: int = Field(ge=1, default=1)
    a_examen_final: bool = True
    a_ds: bool = True
    duree_examen: int | None = Field(default=120, ge=1)
    duree_ds: int | None = Field(default=60, ge=1)


class MatiereCreate(MatiereBase):
    pass


class MatiereUpdate(BaseModel):
    coefficient: float | None = Field(default=None, gt=0)
    credit: int | None = Field(default=None, ge=1)
    a_examen_final: bool | None = None
    a_ds: bool | None = None
    duree_examen: int | None = Field(default=None, ge=1)
    duree_ds: int | None = Field(default=None, ge=1)


class MatiereOut(MatiereBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SectionMatiereBase(BaseModel):
    section_id: int = Field(ge=1)
    matiere_id: int = Field(ge=1)
    a_examen_final: bool = True
    a_ds: bool = True
    duree_examen: int | None = Field(default=120, ge=1)
    duree_ds: int | None = Field(default=60, ge=1)


class SectionMatiereCreate(SectionMatiereBase):
    pass


class SectionMatiereOut(SectionMatiereBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
