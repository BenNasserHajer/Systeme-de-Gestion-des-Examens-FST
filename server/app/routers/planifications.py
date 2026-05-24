"""Planification endpoints. Keep business logic in services."""

from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.planification import (
    GenerationRequest,
    GenerationResult,
    GenerationSimpleRequest,
    PlanifSalleAssign,
    PlanifSalleOut,
    PlanificationCreate,
    PlanificationOut,
    PlanificationUpdate,
    StatutPlanification,
    TypeEpreuve,
    ValiderSessionRequest,
)
from app.services.planif_service import (
    ConstraintViolationError,
    PlanifService,
    PlanificationNotFoundError,
)

router = APIRouter()


def _normalize_mode(value: str) -> str:
    upper = value.upper()
    if upper in {"AUTO", "AUTOMATIQUE"}:
        return "AUTO"
    if upper in {"MANUEL", "MANUELLE"}:
        return "MANUEL"
    return value


def _normalize_semestre(value) -> str:
    if isinstance(value, int):
        return f"S{value}"
    if isinstance(value, str) and value.upper().startswith("S"):
        return value.upper()
    return "S1"


def _salle_to_out(salle) -> PlanifSalleOut:
    return PlanifSalleOut(
        id=hash((salle.planification_id, salle.groupe_id)) % 1_000_000_000,
        salle_id=salle.salle_id,
        salle_capacite=salle.salle_capacite,
        salle_batiment=salle.salle_batiment,
        salle_departement_id=salle.salle_departement_id,
        groupe_id=salle.groupe_id,
        groupe_effectif=salle.groupe_effectif,
        creneau_date=salle.creneau_date,
        heure_debut=salle.heure_debut,
    )


def _to_out(item) -> PlanificationOut:
    return PlanificationOut(
        id=item.id,
        session_id=item.session_id,
        section_id=item.section_id,
        section_matiere_id=item.section_matiere_id,
        section_departement_id=getattr(item, "section_departement_id", None),
        matiere=item.matiere,
        semestre=_normalize_semestre(getattr(item, "semestre", "S1")),
        type_epreuve=item.type_epreuve,
        mode_affectation=_normalize_mode(item.mode_affectation),
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
        a_examen_final=getattr(item, "a_examen_final", True),
        a_ds=getattr(item, "a_ds", True),
        created_at=item.created_at,
        updated_at=item.updated_at,
        salles=[_salle_to_out(s) for s in item.salles_affectees],
    )


@router.get("/planifications", response_model=list[PlanificationOut])
@router.get("/planifications/", response_model=list[PlanificationOut])
@router.get("/planification_examen", response_model=list[PlanificationOut], deprecated=True)
@router.get("/planification_examen/", response_model=list[PlanificationOut], deprecated=True)
def get_planifications(
    session_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    date_examen: date | None = Query(default=None),
    type_epreuve: TypeEpreuve | None = Query(default=None),
    statut: StatutPlanification | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[PlanificationOut]:
    service = PlanifService(db)
    return [
        _to_out(x)
        for x in service.get_all(
            session_id=session_id,
            section_id=section_id,
            date_examen=date_examen,
            type_epreuve=type_epreuve,
            statut=statut,
            skip=skip,
            limit=limit,
        )
    ]


@router.get("/planifications/{planif_id}", response_model=PlanificationOut)
@router.get("/planification_examen/{planif_id}", response_model=PlanificationOut, deprecated=True)
def get_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        return _to_out(service.get_by_id(planif_id))
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/planifications", response_model=PlanificationOut, status_code=status.HTTP_201_CREATED)
@router.post("/planification_examen", response_model=PlanificationOut, status_code=status.HTTP_201_CREATED, deprecated=True)
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


@router.put("/planifications/{planif_id}", response_model=PlanificationOut)
@router.put("/planification_examen/{planif_id}", response_model=PlanificationOut, deprecated=True)
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
@router.delete("/planification_examen/{planif_id}", status_code=status.HTTP_204_NO_CONTENT, deprecated=True)
def delete_planification(planif_id: int, db: Session = Depends(get_db)) -> Response:
    service = PlanifService(db)
    try:
        service.delete(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/generer-simple", response_model=GenerationResult)
def generer_planifications_simple(
    session_id: int,
    payload: GenerationSimpleRequest,
    db: Session = Depends(get_db),
) -> GenerationResult:
    """Generate exam schedule from admin form fields (section, session, type, niveau)."""
    service = PlanifService(db)
    return service.generer_from_form(
        session_id=session_id,
        section_label=payload.section_label,
        niveau=payload.niveau,
        type_epreuve_label=payload.type_epreuve_label,
    )


@router.post("/sessions/{session_id}/generer", response_model=GenerationResult)
@router.post("/sessions/{session_id}/planification_examen/generer", response_model=GenerationResult, deprecated=True)
def generer_planifications(
    session_id: int,
    payload: GenerationRequest,
    db: Session = Depends(get_db),
) -> GenerationResult:
    service = PlanifService(db)
    request = payload.model_copy(update={"session_id": session_id})
    return service.generer_planifications(request)


@router.post("/planifications/{planif_id}/salles", response_model=PlanificationOut)
@router.post("/planification_examen/{planif_id}/salles", response_model=PlanificationOut, deprecated=True)
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


@router.get("/sessions/{session_id}/emploi-du-temps", response_model=list[PlanificationOut])
@router.get(
    "/sessions/{session_id}/planification_examen/emploi-du-temps",
    response_model=list[PlanificationOut],
    deprecated=True,
)
def get_emploi_du_temps(
    session_id: int,
    section_id: int | None = Query(default=None),
    type_epreuve: TypeEpreuve | None = Query(default=None),
    statut: StatutPlanification | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PlanificationOut]:
    service = PlanifService(db)
    return [
        _to_out(x)
        for x in service.get_emploi_du_temps(
            session_id,
            section_id=section_id,
            type_epreuve=type_epreuve,
            statut=statut,
        )
    ]


@router.post("/sessions/{session_id}/valider", response_model=list[PlanificationOut])
def valider_session_planifications(
    session_id: int,
    payload: ValiderSessionRequest | None = Body(default=None),
    db: Session = Depends(get_db),
) -> list[PlanificationOut]:
    """Validate all draft planifications for a session (optionally filtered by section)."""
    service = PlanifService(db)
    section_id = payload.section_id if payload else None
    updated = service.valider_session(session_id, section_id=section_id)
    return [_to_out(x) for x in updated]


@router.post("/planifications/{planif_id}/valider", response_model=PlanificationOut)
@router.post("/planification_examen/{planif_id}/valider", response_model=PlanificationOut, deprecated=True)
def valider_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.valider_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)


@router.post("/planifications/{planif_id}/publier", response_model=PlanificationOut)
@router.post("/planification_examen/{planif_id}/publier", response_model=PlanificationOut, deprecated=True)
def publier_planification(planif_id: int, db: Session = Depends(get_db)) -> PlanificationOut:
    service = PlanifService(db)
    try:
        updated = service.publier_planification(planif_id)
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(updated)
