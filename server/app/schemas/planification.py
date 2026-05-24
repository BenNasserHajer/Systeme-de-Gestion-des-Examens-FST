"""Pydantic schemas for the P1 planification module."""

from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TypeEpreuve(str, Enum):
    EXAMEN_FINAL = "EXAMEN_FINAL"
    DS = "DS"


class ModeAffectation(str, Enum):
    AUTO = "AUTO"
    MANUEL = "MANUEL"


class StatutPlanification(str, Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    PUBLIEE = "PUBLIEE"


class StatutSession(str, Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    PUBLIEE = "PUBLIEE"


class PlanifSalleBase(BaseModel):
    salle_id: str = Field(min_length=1, max_length=80)
    salle_capacite: int = Field(ge=1)
    salle_batiment: str | None = Field(default=None, max_length=64)
    salle_departement_id: int | None = Field(default=None, ge=1)
    groupe_id: int = Field(ge=1)
    groupe_effectif: int = Field(ge=1)


class PlanifSalleAssign(PlanifSalleBase):
    pass


class PlanifSalleOut(PlanifSalleBase):
    id: int | None = None
    creneau_date: date
    heure_debut: time

    model_config = ConfigDict(from_attributes=True)


class GenerationSimpleRequest(BaseModel):
    """Simplified generation payload from admin form (section, session, type, niveau)."""

    session_id: int = Field(ge=1)
    section_label: str = Field(min_length=1, max_length=120)
    niveau: str = Field(min_length=1, max_length=20)
    type_epreuve_label: str = Field(min_length=1, max_length=40)


class ValiderSessionRequest(BaseModel):
    section_id: int | None = Field(default=None, ge=1)


class PlanificationBase(BaseModel):
    session_id: int = Field(ge=1)
    section_id: int = Field(ge=1)
    section_matiere_id: int = Field(ge=1)
    section_departement_id: int | None = Field(default=None, ge=1)
    matiere: str = Field(min_length=2, max_length=120)
    semestre: str = Field(default="S1", min_length=1, max_length=10)

    type_epreuve: TypeEpreuve = TypeEpreuve.EXAMEN_FINAL
    mode_affectation: ModeAffectation = ModeAffectation.MANUEL
    statut: StatutPlanification = StatutPlanification.BROUILLON

    date_examen: date
    heure_debut: time
    heure_fin: time
    session_date_debut: date
    session_date_fin: date
    session_statut: StatutSession = StatutSession.BROUILLON

    duree: int = Field(default=120, ge=1)
    coefficient: float = Field(default=1.0, gt=0)
    section_nb_etudiants: int = Field(ge=1)
    nb_groupes: int = Field(default=1, ge=1)
    nb_surveillants_requis: int = Field(default=1, ge=1)

    a_examen_final: bool = True
    a_ds: bool = True

    @model_validator(mode="after")
    def validate_dates(self) -> "PlanificationBase":
        if self.heure_fin <= self.heure_debut:
            raise ValueError("heure_fin doit etre strictement superieure a heure_debut")
        if self.session_date_debut > self.session_date_fin:
            raise ValueError("session_date_debut doit etre <= session_date_fin")
        return self


class PlanificationCreate(PlanificationBase):
    salles: list[PlanifSalleAssign] = Field(default_factory=list)


class PlanificationUpdate(BaseModel):
    date_examen: date | None = None
    heure_debut: time | None = None
    heure_fin: time | None = None
    statut: StatutPlanification | None = None
    mode_affectation: ModeAffectation | None = None
    duree: int | None = Field(default=None, ge=1)
    nb_groupes: int | None = Field(default=None, ge=1)
    nb_surveillants_requis: int | None = Field(default=None, ge=1)
    salles: list[PlanifSalleAssign] | None = None


class PlanificationOut(PlanificationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    salles: list[PlanifSalleOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GenerationTask(BaseModel):
    section_id: int = Field(ge=1)
    section_matiere_id: int = Field(ge=1)
    matiere_id: int | None = Field(default=None, ge=1)
    matiere: str = Field(min_length=2, max_length=120)
    semestre: str = Field(default="S1", min_length=1, max_length=10)
    section_departement_id: int | None = Field(default=None, ge=1)
    type_epreuve: TypeEpreuve
    duree: int = Field(ge=1)
    section_nb_etudiants: int = Field(ge=1)
    coefficient: float = Field(default=1.0, gt=0)
    nb_surveillants_requis: int = Field(default=1, ge=1)
    a_examen_final: bool = True
    a_ds: bool = True


class GenerationCreneau(BaseModel):
    date_examen: date
    heure_debut: time
    heure_fin: time


class GenerationSalle(BaseModel):
    salle_id: str = Field(min_length=1, max_length=80)
    capacite: int = Field(ge=1)
    batiment: str | None = Field(default=None, max_length=64)
    departement_id: int | None = Field(default=None, ge=1)


class GenerationRequest(BaseModel):
    session_id: int = Field(ge=1)
    annee_universitaire: str | None = Field(default=None, max_length=10)
    session_date_debut: date
    session_date_fin: date
    session_statut: StatutSession = StatutSession.BROUILLON
    semestre: str = Field(default="S1", min_length=1, max_length=10)
    scope_section_ids: list[int] = Field(default_factory=list)
    mode: ModeAffectation = ModeAffectation.AUTO
    tasks: list[GenerationTask] = Field(default_factory=list)
    creneaux: list[GenerationCreneau] = Field(default_factory=list)
    salles: list[GenerationSalle] = Field(default_factory=list)


class GenerationResult(BaseModel):
    nb_crees: int
    nb_conflits: int
    conflits: list[str]


PlanificationRead = PlanificationOut
