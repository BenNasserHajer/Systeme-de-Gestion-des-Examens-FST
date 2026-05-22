from sqlalchemy import Column, Integer, String, Date, Enum
from app.database import Base
import enum

# Enum Python (doit matcher PostgreSQL)
class TypeSession(str, enum.Enum):
    PRINCIPALE = "PRINCIPALE"
    RATTRAPAGE = "RATTRAPAGE"

class StatutPlanif(str, enum.Enum):
    BROUILLON = "BROUILLON"
    VALIDEE = "VALIDEE"
    PUBLIEE = "PUBLIEE"


class Session(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, index=True)
    type_session = Column(Enum(TypeSession), nullable=False)
    annee_universitaire = Column(String(10), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    statut = Column(Enum(StatutPlanif), default=StatutPlanif.BROUILLON)