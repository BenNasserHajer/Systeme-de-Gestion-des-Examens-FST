from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.salle import Salle
from app.schemas.salle import SalleCreate, SalleUpdate, SalleOut

router = APIRouter(prefix="/salles", tags=["salles"])

@router.get("/", response_model=list[SalleOut])
def list_salles(db: Session = Depends(get_db)):
    return db.query(Salle).all()

@router.get("/{salle_id}", response_model=SalleOut)
def get_salle(salle_id: int, db: Session = Depends(get_db)):
    salle = db.query(Salle).filter(Salle.id == salle_id).first()
    if not salle:
        raise HTTPException(status_code=404, detail="Salle non trouvée")
    return salle

from sqlalchemy.exc import IntegrityError

@router.post("/", response_model=SalleOut, status_code=201)
def create_salle(salle: SalleCreate, db: Session = Depends(get_db)):
    db_salle = Salle(**salle.model_dump())
    db.add(db_salle)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Une salle avec ce nom existe déjà"
        )

    db.refresh(db_salle)
    return db_salle

@router.put("/{salle_id}", response_model=SalleOut)
def update_salle(salle_id: int, salle: SalleUpdate, db: Session = Depends(get_db)):
    db_salle = db.query(Salle).filter(Salle.id == salle_id).first()
    if not db_salle:
        raise HTTPException(status_code=404, detail="Salle non trouvée")
    for key, value in salle.model_dump(exclude_unset=True).items():
        setattr(db_salle, key, value)
    db.commit()
    db.refresh(db_salle)
    return db_salle

@router.delete("/{salle_id}", status_code=204)
def delete_salle(salle_id: int, db: Session = Depends(get_db)):
    db_salle = db.query(Salle).filter(Salle.id == salle_id).first()
    if not db_salle:
        raise HTTPException(status_code=404, detail="Salle non trouvée")
    db.delete(db_salle)
    db.commit()