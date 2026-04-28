"""
routers/session.py
Endpoints pour la gestion des sessions d'examens
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.salle_session import Session as SessionModel
from app.schemas.session_schema import SessionOut 

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=List[SessionOut]) 
def get_all_sessions(db: Session = Depends(get_db)):
    """Retourne toutes les sessions d'examens."""
    sessions = db.query(SessionModel).all()
    return sessions 