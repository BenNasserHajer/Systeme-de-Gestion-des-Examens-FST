"""
schemas/indisponibilite_schema.py
"""
from pydantic import BaseModel, model_validator
from typing import Literal, Optional
from datetime import date as DateType, time as TimeType  # ← RENOMMER ICI


TypeDispo = Literal["DISPONIBLE", "INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]


class IndisponibiliteCreate(BaseModel):
    enseignant_id: int
    date:          DateType
    heure_debut:   TimeType
    heure_fin:     TimeType
    type_dispo:    TypeDispo = "INDISPONIBLE"
    motif:         Optional[str] = None
    confirme:      bool = True

    @model_validator(mode="after")
    def check_heures(self):
        if self.heure_fin <= self.heure_debut:
            raise ValueError("heure_fin doit être supérieure à heure_debut")
        return self

    model_config = {"from_attributes": True}


class IndisponibiliteUpdate(BaseModel):
    date:        Optional[DateType] = None   # ← UTILISER DateType
    heure_debut: Optional[TimeType] = None   # ← UTILISER TimeType
    heure_fin:   Optional[TimeType] = None
    type_dispo:  Optional[TypeDispo] = None
    motif:       Optional[str] = None
    confirme:    Optional[bool] = None

    model_config = {"from_attributes": True}


class IndisponibiliteRead(BaseModel):
    id:            int
    enseignant_id: int
    date:          DateType
    heure_debut:   TimeType
    heure_fin:     TimeType
    type_dispo:    str
    motif:         Optional[str] = None
    confirme:      bool

    model_config = {"from_attributes": True}