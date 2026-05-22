from pydantic import BaseModel
from datetime import date
from enum import Enum


class TypeSession(str, Enum):
    PRINCIPALE = "PRINCIPALE"
    RATTRAPAGE = "RATTRAPAGE"


class StatutPlanif(str, Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    PUBLIEE = "PUBLIEE"


# 🔹 Base
class SessionBase(BaseModel):
    type_session: TypeSession
    annee_universitaire: str
    date_debut: date
    date_fin: date
    statut: StatutPlanif = StatutPlanif.BROUILLON


# 🔹 Create
class SessionCreate(SessionBase):
    pass


# 🔹 Update
class SessionUpdate(BaseModel):
    type_session: TypeSession | None = None
    annee_universitaire: str | None = None
    date_debut: date | None = None
    date_fin: date | None = None
    statut: StatutPlanif | None = None


# 🔹 Response
class SessionOut(SessionBase):
    id: int

    class Config:
        from_attributes = True