"""Workflow endpoints per WORKFLOW_PLANIFICATION.md."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers.planifications import _to_out
from app.schemas.planification import (
    ChangerSalleRequest,
    ChangerSalleResponse,
    ConflitDetail,
    DeplacerRequest,
    DeplacerResponse,
    GenerationAutoRequest,
    GenerationAutoResponse,
    PlanificationUpdate,
    StatutPlanification,
    ValiderSessionResponse,
    ValiderSessionWorkflowRequest,
)
from app.services.planif_service import (
    ConstraintViolationError,
    PlanifService,
    PlanificationNotFoundError,
)

router = APIRouter(prefix="/planification", tags=["Planification Workflow"])


def _parse_conflits(conflits: list[str]) -> list[ConflitDetail | str]:
    parsed: list[ConflitDetail | str] = []
    for msg in conflits:
        if "[" in msg and "]" in msg:
            start = msg.index("[") + 1
            end = msg.index("]")
            parsed.append(
                ConflitDetail(
                    matiere="",
                    contrainte=msg[start:end],
                    message=msg,
                    suggestion="Deplacez l'examen ou changez la salle.",
                )
            )
        else:
            parsed.append(msg)
    return parsed


@router.post("/generer-auto", response_model=GenerationAutoResponse)
def generer_auto(payload: GenerationAutoRequest, db: Session = Depends(get_db)) -> GenerationAutoResponse:
    service = PlanifService(db)
    try:
        result, planifs = service.generer_auto(
            section_id=payload.section_id,
            session_id=payload.session_id,
            type_epreuve=payload.type_epreuve.value,
            semestre=payload.semestre,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return GenerationAutoResponse(
        success=result.nb_crees > 0,
        nb_crees=result.nb_crees,
        nb_conflits=result.nb_conflits,
        planifications=[_to_out(p) for p in planifs],
        conflits=_parse_conflits(result.conflits),
    )


@router.patch("/{planif_id}/deplacer", response_model=DeplacerResponse)
def deplacer_planification(
    planif_id: int,
    payload: DeplacerRequest,
    db: Session = Depends(get_db),
) -> DeplacerResponse:
    service = PlanifService(db)
    try:
        updated, warnings = service.deplacer(
            planif_id,
            payload.nouvelle_date,
            payload.nouvelle_heure_debut,
            payload.nouvelle_heure_fin,
        )
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return DeplacerResponse(success=True, planification=_to_out(updated), warnings=warnings)


@router.patch("/{planif_id}/changer-salle", response_model=ChangerSalleResponse)
def changer_salle(
    planif_id: int,
    payload: ChangerSalleRequest,
    db: Session = Depends(get_db),
) -> ChangerSalleResponse:
    service = PlanifService(db)
    try:
        updated, warnings = service.changer_salle(
            planif_id,
            payload.groupe_id,
            payload.nouvelle_salle_id,
        )
    except PlanificationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ConstraintViolationError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ChangerSalleResponse(success=True, planification=_to_out(updated), warnings=warnings)


@router.post("/valider-session", response_model=ValiderSessionResponse)
def valider_session_workflow(
    payload: ValiderSessionWorkflowRequest,
    db: Session = Depends(get_db),
) -> ValiderSessionResponse:
    service = PlanifService(db)
    erreurs: list[str] = []
    try:
        updated = service.valider_session(payload.session_id, section_id=payload.section_id)
    except Exception as exc:
        erreurs.append(str(exc))
        return ValiderSessionResponse(
            success=False,
            nb_planifications=0,
            statut=StatutPlanification.BROUILLON,
            planifications=[],
            erreurs=erreurs,
        )

    return ValiderSessionResponse(
        success=True,
        nb_planifications=len(updated),
        statut=StatutPlanification.VALIDEE,
        planifications=[_to_out(p) for p in updated],
        erreurs=[],
    )
