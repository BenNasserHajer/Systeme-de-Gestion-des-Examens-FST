from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionOut

router = APIRouter(prefix="/sessions", tags=["Sessions"])


# ✅ FIX: GET /sessions/ ajouté
@router.get("/", response_model=list[SessionOut])
def list_sessions(db: Session = Depends(get_db)):
    """Retourne toutes les sessions."""
    return db.query(SessionModel).order_by(SessionModel.id.desc()).all()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Retourne une session par son ID."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session introuvable")
    return session


@router.post("/", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(data: SessionCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle session."""
    session = SessionModel(**data.dict())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session