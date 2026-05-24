"""Business logic for planification module."""

from datetime import date

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.algorithms.contraintes import build_default_engine
from app.algorithms.planif_auto import generer
from app.crud.crud_planif import (
    create_planification,
    delete_planification,
    get_emploi_du_temps_filtre,
    get_planification,
    list_existing_for_session,
    list_planifications,
    replace_planif_salles,
    update_planification,
)
from app.models.planification import Planification
from app.schemas.planification import (
    GenerationRequest,
    GenerationResult,
    GenerationTask,
    GenerationCreneau,
    GenerationSalle,
    PlanifSalleAssign,
    PlanificationCreate,
    PlanificationUpdate,
    StatutPlanification,
    StatutSession,
    TypeEpreuve,
)
from app.services.catalogue_service import build_generation_request, load_catalogue


class ConstraintViolationError(ValueError):
    """Raised when one or many hard planning constraints are violated."""


class PlanificationNotFoundError(LookupError):
    """Raised when the target planification does not exist."""


class PlanifService:
    """Contains all planification business rules."""

    def __init__(self, db: Session):
        self.db = db
        self.engine = build_default_engine()

    def get_all(
        self,
        *,
        session_id: int | None = None,
        section_id: int | None = None,
        date_examen: date | None = None,
        type_epreuve: TypeEpreuve | None = None,
        statut: StatutPlanification | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Planification]:
        return list_planifications(
            self.db,
            session_id=session_id,
            section_id=section_id,
            date_examen=date_examen,
            type_epreuve=type_epreuve.value if type_epreuve is not None else None,
            statut=statut.value if statut is not None else None,
            skip=skip,
            limit=limit,
        )

    def get_by_id(self, planif_id: int) -> Planification:
        planif = get_planification(self.db, planif_id)
        if not planif:
            raise PlanificationNotFoundError(f"Planification {planif_id} introuvable")
        return planif

    def _validate_payload(
        self,
        payload: PlanificationCreate,
        *,
        exclude_planif_id: int | None = None,
    ) -> list[str]:
        existing = list_existing_for_session(self.db, payload.session_id)
        errors, warnings = self.engine.verifier_toutes(
            payload,
            {
                "existing_planifs": existing,
                "exclude_planif_id": exclude_planif_id,
                "known_section_matiere_ids": None,
                "section_departement_id": payload.section_departement_id,
            },
            self.db,
        )
        if errors:
            raise ConstraintViolationError(" | ".join(errors))
        return warnings

    def create(self, payload: PlanificationCreate) -> tuple[Planification, list[str]]:
        warnings = self._validate_payload(payload)
        created = create_planification(self.db, payload)
        return created, warnings

    def _resolve_session_context(self, request: GenerationRequest) -> GenerationRequest:
        inspector = inspect(self.db.bind)
        if not inspector.has_table("session"):
            return request

        row = self.db.execute(
            text(
                """
                SELECT id, annee_universitaire, date_debut, date_fin, statut
                FROM session
                WHERE id = :session_id
                """
            ),
            {"session_id": request.session_id},
        ).mappings().first()

        if row is None:
            raise ConstraintViolationError(f"[C16] session {request.session_id} introuvable")

        statut = str(row["statut"]).upper()
        if statut not in {"BROUILLON", "VALIDEE"}:
            raise ConstraintViolationError("[C17] session publiee, generation impossible")

        return request.model_copy(
            update={
                "annee_universitaire": row.get("annee_universitaire"),
                "session_date_debut": row["date_debut"],
                "session_date_fin": row["date_fin"],
                "session_statut": StatutSession(statut),
            }
        )

    def update(self, planif_id: int, payload: PlanificationUpdate) -> tuple[Planification, list[str]]:
        planif = self.get_by_id(planif_id)

        effective_salles = payload.salles
        if effective_salles is None:
            effective_salles = [
                PlanifSalleAssign(
                    salle_id=s.salle_id,
                    salle_capacite=s.salle_capacite,
                    salle_batiment=s.salle_batiment,
                    groupe_id=s.groupe_id,
                    groupe_effectif=s.groupe_effectif,
                )
                for s in planif.salles_affectees
            ]

        candidate = PlanificationCreate(
            session_id=planif.session_id,
            section_id=planif.section_id,
            section_matiere_id=planif.section_matiere_id,
            matiere=planif.matiere,
            type_epreuve=planif.type_epreuve,
            mode_affectation=payload.mode_affectation or planif.mode_affectation,
            statut=payload.statut or planif.statut,
            date_examen=payload.date_examen or planif.date_examen,
            heure_debut=payload.heure_debut or planif.heure_debut,
            heure_fin=payload.heure_fin or planif.heure_fin,
            session_date_debut=planif.session_date_debut,
            session_date_fin=planif.session_date_fin,
            session_statut=planif.session_statut,
            duree=payload.duree or planif.duree,
            coefficient=planif.coefficient,
            section_nb_etudiants=planif.section_nb_etudiants,
            nb_groupes=payload.nb_groupes or planif.nb_groupes,
            nb_surveillants_requis=payload.nb_surveillants_requis or planif.nb_surveillants_requis,
            salles=effective_salles,
        )
        warnings = self._validate_payload(candidate, exclude_planif_id=planif.id)
        updated = update_planification(self.db, planif, payload)
        return updated, warnings

    def delete(self, planif_id: int) -> None:
        planif = self.get_by_id(planif_id)
        delete_planification(self.db, planif)

    def generer_from_form(
        self,
        *,
        session_id: int,
        section_label: str,
        niveau: str,
        type_epreuve_label: str,
    ) -> GenerationResult:
        catalogue = load_catalogue(self.db)
        raw = build_generation_request(
            catalogue,
            session_id=session_id,
            section_label=section_label,
            type_epreuve_label=type_epreuve_label,
            niveau=niveau,
        )
        request = GenerationRequest(
            session_id=raw["session_id"],
            session_date_debut=raw["session_date_debut"],
            session_date_fin=raw["session_date_fin"],
            session_statut=StatutSession(raw["session_statut"]),
            mode=raw["mode"],
            scope_section_ids=raw["scope_section_ids"],
            tasks=[GenerationTask(**task) for task in raw["tasks"]],
            creneaux=[GenerationCreneau(**c) for c in raw["creneaux"]],
            salles=[GenerationSalle(**s) for s in raw["salles"]],
        )
        return self.generer_planifications(request)

    def generer_planifications(self, request: GenerationRequest) -> GenerationResult:
        request = self._resolve_session_context(request)
        existing = list_existing_for_session(self.db, request.session_id)
        known_section_matiere_ids = {item.section_matiere_id for item in request.tasks} or None
        creates, result = generer(
            request,
            self.engine,
            existing,
            self.db,
            known_section_matiere_ids=known_section_matiere_ids,
        )
        for payload in creates:
            create_planification(self.db, payload)
        return result

    def affecter_salles_manuel(self, planif_id: int, salles: list[PlanifSalleAssign]) -> tuple[Planification, list[str]]:
        planif = self.get_by_id(planif_id)
        candidate = PlanificationCreate(
            session_id=planif.session_id,
            section_id=planif.section_id,
            section_matiere_id=planif.section_matiere_id,
            matiere=planif.matiere,
            type_epreuve=planif.type_epreuve,
            mode_affectation="MANUEL",
            statut=planif.statut,
            date_examen=planif.date_examen,
            heure_debut=planif.heure_debut,
            heure_fin=planif.heure_fin,
            session_date_debut=planif.session_date_debut,
            session_date_fin=planif.session_date_fin,
            session_statut=planif.session_statut,
            duree=planif.duree,
            coefficient=planif.coefficient,
            section_nb_etudiants=planif.section_nb_etudiants,
            nb_groupes=len(salles),
            nb_surveillants_requis=planif.nb_surveillants_requis,
            salles=salles,
        )
        warnings = self._validate_payload(candidate, exclude_planif_id=planif.id)
        updated = replace_planif_salles(self.db, planif, salles)
        return updated, warnings

    def get_emploi_du_temps(
        self,
        session_id: int,
        *,
        section_id: int | None = None,
        type_epreuve: TypeEpreuve | None = None,
        statut: StatutPlanification | None = None,
    ) -> list[Planification]:
        return get_emploi_du_temps_filtre(
            self.db,
            session_id=session_id,
            section_id=section_id,
            type_epreuve=type_epreuve.value if type_epreuve is not None else None,
            statut=statut.value if statut is not None else None,
        )

    def valider_session(
        self,
        session_id: int,
        *,
        section_id: int | None = None,
    ) -> list[Planification]:
        planifs = list_planifications(
            self.db,
            session_id=session_id,
            section_id=section_id,
            statut=StatutPlanification.BROUILLON.value,
            skip=0,
            limit=500,
        )
        updated: list[Planification] = []
        for planif in planifs:
            patch = PlanificationUpdate(statut=StatutPlanification.VALIDEE)
            updated.append(update_planification(self.db, planif, patch))
        return updated

    def valider_planification(self, planif_id: int) -> Planification:
        planif = self.get_by_id(planif_id)
        patch = PlanificationUpdate(statut=StatutPlanification.VALIDEE)
        return update_planification(self.db, planif, patch)

    def publier_planification(self, planif_id: int) -> Planification:
        planif = self.get_by_id(planif_id)
        patch = PlanificationUpdate(statut=StatutPlanification.PUBLIEE)
        return update_planification(self.db, planif, patch)
