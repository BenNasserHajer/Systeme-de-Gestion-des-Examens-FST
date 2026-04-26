from typing import Optional
from pydantic import BaseModel


class SessionOut(BaseModel):
    """Schéma de sortie pour une session."""
    id: int
    type_session: str
    annee_universitaire: str
    date_debut: Optional[str] = None
    date_fin: Optional[str] = None
    statut: str

    class Config:
        from_attributes = True