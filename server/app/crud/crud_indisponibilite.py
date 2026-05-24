"""
crud/crud_indisponibilite.py
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.disponibilite import DisponibiliteEnseignant
from app.schemas.indisponibilite_schema import IndisponibiliteCreate, IndisponibiliteUpdate


# ─────────────────────────────────────────────────────────────
# READ
# ─────────────────────────────────────────────────────────────

def get_all_for_enseignant(
    db: Session,
    enseignant_id: int,
) -> list[DisponibiliteEnseignant]:
    return (
        db.query(DisponibiliteEnseignant)
        .filter(DisponibiliteEnseignant.enseignant_id == enseignant_id)
        .order_by(DisponibiliteEnseignant.date, DisponibiliteEnseignant.heure_debut)
        .all()
    )


def get_by_id(db: Session, indispo_id: int) -> DisponibiliteEnseignant | None:
    return db.query(DisponibiliteEnseignant).filter(
        DisponibiliteEnseignant.id == indispo_id
    ).first()


def get_by_id_or_404(db: Session, indispo_id: int) -> DisponibiliteEnseignant:
    obj = get_by_id(db, indispo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Indisponibilité introuvable")
    return obj


# ─────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────

def create_indisponibilite(
    db: Session,
    payload: IndisponibiliteCreate,
) -> DisponibiliteEnseignant:
    # Vérifier chevauchement
    overlap = (
        db.query(DisponibiliteEnseignant)
        .filter(
            DisponibiliteEnseignant.enseignant_id == payload.enseignant_id,
            DisponibiliteEnseignant.date          == payload.date,
            DisponibiliteEnseignant.heure_debut   < payload.heure_fin,
            DisponibiliteEnseignant.heure_fin     > payload.heure_debut,
        )
        .first()
    )
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un créneau d'indisponibilité existe déjà sur cette plage horaire",
        )

    obj = DisponibiliteEnseignant(
        enseignant_id=payload.enseignant_id,
        date=payload.date,
        heure_debut=payload.heure_debut,
        heure_fin=payload.heure_fin,
        type_dispo=payload.type_dispo,
        motif=payload.motif,
        confirme=payload.confirme,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─────────────────────────────────────────────────────────────
# UPDATE
# ─────────────────────────────────────────────────────────────

def update_indisponibilite(
    db: Session,
    indispo_id: int,
    payload: IndisponibiliteUpdate,
    enseignant_id: int,          # pour vérifier que c'est bien le sien
) -> DisponibiliteEnseignant:
    obj = get_by_id_or_404(db, indispo_id)

    if obj.enseignant_id != enseignant_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    if payload.date        is not None: obj.date        = payload.date
    if payload.heure_debut is not None: obj.heure_debut = payload.heure_debut
    if payload.heure_fin   is not None: obj.heure_fin   = payload.heure_fin
    if payload.type_dispo  is not None: obj.type_dispo  = payload.type_dispo
    if payload.motif       is not None: obj.motif       = payload.motif
    if payload.confirme    is not None: obj.confirme    = payload.confirme

    db.commit()
    db.refresh(obj)
    return obj


# ─────────────────────────────────────────────────────────────
# DELETE
# ─────────────────────────────────────────────────────────────

def delete_indisponibilite(
    db: Session,
    indispo_id: int,
    enseignant_id: int,          # pour vérifier que c'est bien le sien
) -> None:
    obj = get_by_id_or_404(db, indispo_id)

    if obj.enseignant_id != enseignant_id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(obj)
    db.commit()