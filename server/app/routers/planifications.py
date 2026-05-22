"""Planification endpoints. Keep business logic in services."""

from datetime import date, timedelta, time as dtime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.salle import Salle
from app.schemas.planification import (
    GenerationCreneau,
    GenerationRequest,
    GenerationResult,
    GenerationSalle,
    GenerationTask,
    ModeAffectation,
    PlanifSalleAssign,
    PlanificationCreate,
    PlanificationOut,
    PlanificationUpdate,
    StatutSession,
    TypeEpreuve,
)
from app.services.planif_service import (
    ConstraintViolationError,
    PlanifService,
    PlanificationNotFoundError,
)

router = APIRouter()


def _to_out(item) -> PlanificationOut:
    return PlanificationOut(
        id=item.id,
        session_id=item.session_id,
        section_id=item.section_id,
        section_matiere_id=item.section_matiere_id,
        matiere=item.matiere,
        type_epreuve=item.type_epreuve,
        mode_affectation=item.mode_affectation,
        statut=item.statut,
        date_examen=item.date_examen,
        heure_debut=item.heure_debut,
        heure_fin=item.heure_fin,
        session_date_debut=item.session_date_debut,
        session_date_fin=item.session_date_fin,
        session_statut=item.session_statut,
        duree=item.duree,
        coefficient=item.coefficient,
        section_nb_etudiants=item.section_nb_etudiants,
        nb_groupes=item.nb_groupes,
        nb_surveillants_requis=item.nb_surveillants_requis,
        created_at=item.created_at,
        updated_at=item.updated_at,
        salles=item.salles_affectees,
    )


@router.post("/sessions/{session_id}/generer-auto", response_model=GenerationResult)
def generer_auto(
    session_id: int,
    section_nom: str = Query(...),
    annee: str = Query(default="2025/2026"),
    db: Session = Depends(get_db),
) -> GenerationResult:
    """
    Génère automatiquement l'emploi du temps pour une section
    """
    
    # 1. Récupérer la session
    session = db.execute(
        text("SELECT * FROM session WHERE id = :id"),
        {"id": session_id}
    ).fetchone()

    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")

    # 2. Récupérer la section par son NOM
    section = db.execute(
        text("""
            SELECT id, nom, nb_etudiants
            FROM section
            WHERE UPPER(nom) = UPPER(:nom)
        """),
        {"nom": section_nom}
    ).fetchone()

    if not section:
        raise HTTPException(
            status_code=404, 
            detail=f"Section '{section_nom}' introuvable"
        )

    # 3. Récupérer l'effectif depuis la table groupe (colonne 'effectif')
    effectif = db.execute(
        text("""
            SELECT COALESCE(SUM(g.effectif), 0) as total
            FROM groupe g
            WHERE g.section_id = :id
        """),
        {"id": section.id}
    ).scalar() or 0

    # Si aucun groupe trouvé, utiliser nb_etudiants de la section
    if effectif == 0:
        effectif = section.nb_etudiants or 30
        print(f"⚠️ Aucun groupe trouvé pour section {section_nom}, utilisation nb_etudiants={effectif}")

    print(f"📊 Effectif pour {section_nom}: {effectif} étudiants")

    # 4. Récupérer les matières de la section
    section_matieres = db.execute(
        text("""
            SELECT sm.id, sm.matiere_id, m.intitule, m.coefficient,
                COALESCE(sm.duree_examen, m.duree_examen, 120) as duree_examen,
                m.duree_ds,
                sm.a_examen_final, sm.a_ds
            FROM section_matiere sm
            JOIN matiere m ON m.id = sm.matiere_id
            WHERE sm.section_id = :sid
        """),
        {"sid": section.id}
    ).fetchall()

    if not section_matieres:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune matière pour la section '{section_nom}'"
        )

    # 5. Créer les tâches
    tasks = []
    for sm in section_matieres:
        if sm.a_examen_final:
            tasks.append(GenerationTask(
                section_id=section.id,
                section_matiere_id=sm.id,
                matiere=sm.intitule,
                type_epreuve=TypeEpreuve.EXAMEN_FINAL,
                duree=sm.duree_examen or 120,
                section_nb_etudiants=int(effectif),
                coefficient=float(sm.coefficient or 1),
                a_examen_final=True,
                a_ds=sm.a_ds,
            ))

    # 6. Créer les créneaux (matin et après-midi, sauf dimanche)
    creneaux = []
    current_date = session.date_debut

    while current_date <= session.date_fin:
        if current_date.weekday() != 6:  # pas dimanche (6 = dimanche)
            # Créneau matin
            creneaux.append(GenerationCreneau(
                date_examen=current_date,
                heure_debut=dtime(8, 0),
                heure_fin=dtime(12, 0)
            ))
            # Créneau après-midi
            creneaux.append(GenerationCreneau(
                date_examen=current_date,
                heure_debut=dtime(14, 0),
                heure_fin=dtime(18, 0)
            ))
        current_date += timedelta(days=1)

    # 7. Récupérer les salles disponibles
    salles_db = db.query(Salle).all()

    salles = [
        GenerationSalle(
            salle_id=s.id,
            capacite=s.capacite or 30,
            batiment=s.batiment,
        )
        for s in salles_db
        if s.capacite and s.capacite > 0
    ]

    if not salles:
        raise HTTPException(status_code=404, detail="Aucune salle disponible")

    # 8. Construire la requête
    request = GenerationRequest(
        session_id=session_id,
        session_date_debut=session.date_debut,
        session_date_fin=session.date_fin,
        session_statut=StatutSession(session.statut),
        mode=ModeAffectation.AUTO,
        tasks=tasks,
        creneaux=creneaux,
        salles=salles,
    )

    # 9. Appeler le service
    service = PlanifService(db)
    return service.generer_planifications(request)


@router.get("/sessions/{session_id}/emploi-du-temps", response_model=list[PlanificationOut])
def get_emploi_du_temps(
    session_id: int, 
    section_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
) -> list[PlanificationOut]:
    """
    Récupère l'emploi du temps pour une session
    Optionnellement filtré par section_id
    """
    service = PlanifService(db)
    
    if section_id:
        # Filtrer par section
        result = service.get_emploi_du_temps_by_section(session_id, section_id)
    else:
        # Toutes les planifications de la session
        result = service.get_emploi_du_temps(session_id)
    
    return [_to_out(x) for x in result]


@router.post("/planifications", response_model=PlanificationOut, status_code=status.HTTP_201_CREATED)
def create_planification(
    payload: PlanificationCreate,
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        created, _warnings = service.create(payload)
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(created)


@router.get("/planifications/{planif_id}", response_model=PlanificationOut)
def get_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        return _to_out(service.get_by_id(planif_id))
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/planifications/{planif_id}", response_model=PlanificationOut)
def update_planification(
    planif_id: int,
    payload: PlanificationUpdate,
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated, _warnings = service.update(planif_id, payload)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(updated)


@router.delete("/planifications/{planif_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planification(planif_id: int, db: Session = Depends(get_db)) -> Response:
    service = PlanifService(db)
    try:
        service.delete(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/generer", response_model=GenerationResult)
def generer_planifications(
    session_id: int,
    payload: GenerationRequest,
    db: Session = Depends(get_db),
) -> GenerationResult:
    service = PlanifService(db)
    request = payload.model_copy(update={"session_id": session_id})
    return service.generer_planifications(request)


@router.post("/planifications/{planif_id}/salles", response_model=PlanificationOut)
def affecter_salles_manuel(
    planif_id: int,
    salles: list[PlanifSalleAssign],
    db: Session = Depends(get_db),
) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated, _warnings = service.affecter_salles_manuel(planif_id, salles)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _to_out(updated)


@router.post("/planifications/{planif_id}/valider", response_model=PlanificationOut)
def valider_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.valider_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)


@router.post("/planifications/{planif_id}/publier", response_model=PlanificationOut)
def publier_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.publier_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)