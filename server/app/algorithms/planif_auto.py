"""
planif_auto.py
==============
Automatic exam-planification algorithm (best effort).

Implemented constraints:
  Hard : C1 C2 C3 C4 C6 C7 C8 C10b C11 C12 C14 C15 C16 C17 C18
  Soft : C5 C9 C10 C13

The engine keeps generating other subjects even if one subject fails.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, time
from math import ceil
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.algorithms.contraintes import ContrainteEngine
from app.models.planification import Planification
from app.config import settings
from app.schemas.planification import (
    GenerationRequest,
    GenerationResult,
    ModeAffectation,
    PlanifSalleAssign,
    PlanificationCreate,
    StatutPlanification,
    TypeEpreuve,
)

logger = logging.getLogger(__name__)


CONTRAINTES_DURES: Set[str] = {
    "C1",
    "C2",
    "C3",
    "C4",
    "C6",
    "C7",
    "C8",
    "C11",
    "C12",
    "C14",
    "C15",
    "C16",
    "C17",
    "C18",
}

CONTRAINTES_SOUPLES: Set[str] = {
    "C5",
    "C5bis",
    "C9",
    "C10",
    "C13",
}


class ConflitContrainte(Exception):
    """Raised when a hard constraint is violated."""

    def __init__(self, contrainte: str, message: str) -> None:
        self.contrainte = contrainte
        super().__init__(f"[{contrainte}] {message}")


class SessionVerrouillee(Exception):
    """Raised when trying to plan into a published session."""


@dataclass
class SalleDTO:
    id: int
    code: str
    capacite: int
    batiment: str
    departement_id: int | None = None


@dataclass
class CreneauDTO:
    id: int
    date: date
    heure_debut: time
    heure_fin: time
    libelle: str


@dataclass
class SectionDTO:
    id: int
    nom: str
    nb_etudiants: int
    departement_id: int | None = None


@dataclass
class MatiereDTO:
    id: int
    code: str
    intitule: str
    coefficient: float
    a_examen_final: bool
    a_ds: bool


@dataclass
class SectionMatiereDTO:
    id: int
    section: SectionDTO
    matiere: MatiereDTO
    section_id: int
    matiere_id: int
    semestre: str
    a_examen_final: bool
    a_ds: bool
    duree_examen: int
    duree_ds: int
    type_epreuve: str = "EXAMEN_FINAL"
    nb_surveillants_requis: int = 1


@dataclass
class SessionDTO:
    id: int
    statut: str
    date_debut: date
    date_fin: date
    type_session: str
    annee_universitaire: str | None = None


@dataclass
class AttributionSalle:
    groupe_effectif: int
    salle: SalleDTO


@dataclass
class ResultatPlanification:
    section_matiere: SectionMatiereDTO
    creneau: CreneauDTO
    attributions: List[AttributionSalle]
    score_souples: int = 0


@dataclass
class ConflitDetail:
    matiere_intitule: str
    section_nom: str
    contrainte: str
    message: str
    suggestion: str


@dataclass
class RapportGeneration:
    nb_crees: int = 0
    nb_conflits: int = 0
    conflits: List[ConflitDetail] = field(default_factory=list)

    def ajouter_conflit(self, sm: SectionMatiereDTO, contrainte: str, message: str) -> None:
        self.nb_conflits += 1
        self.conflits.append(
            ConflitDetail(
                matiere_intitule=sm.matiere.intitule,
                section_nom=sm.section.nom,
                contrainte=contrainte,
                message=message,
                suggestion=_suggestion(contrainte),
            )
        )


def _suggestion(c: str) -> str:
    mapping = {
        "C1": "Room collision: spread exams on more slots or add rooms.",
        "C2": "No room can cover capacity: increase capacity or split groups.",
        "C7": "Section already busy on this slot: choose another slot.",
        "C8": "Not enough rooms for mandatory split: add rooms.",
        "C12": "Exam already planned for this section/subject.",
        "C14": "Exam duration exceeds slot duration.",
    }
    return mapping.get(c, "Resolve manually from the admin planning screen.")


class ContextePlanification:
    """In-memory state updated after each successful assignment."""

    def __init__(
        self,
        session: SessionDTO,
        creneaux: List[CreneauDTO],
        salles: List[SalleDTO],
        planifs_existantes: List[Tuple[int, int, str, int, int]],
    ) -> None:
        self.session = session
        self.creneaux_disponibles: List[CreneauDTO] = [
            c
            for c in creneaux
            if session.date_debut <= c.date <= session.date_fin and c.date.weekday() != 6
        ]
        self.salles_triees: List[SalleDTO] = sorted(salles, key=lambda s: s.capacite)
        self.salles_par_departement: Dict[int | None, List[SalleDTO]] = {}
        for salle in self.salles_triees:
            self.salles_par_departement.setdefault(salle.departement_id, []).append(salle)
        self.salles_par_departement.setdefault(None, [])

        self._salles_occupees: Dict[Tuple[date, time], Set[int]] = {}
        self._sections_occupees: Dict[Tuple[date, time], Set[int]] = {}
        self._matieres_planifiees: Set[Tuple[int, int, str]] = set()
        self._examens_par_section_jour: Dict[Tuple[int, date], int] = {}
        self._batiments_par_section_jour: Dict[Tuple[int, date], Set[str]] = {}

        self._creneaux_index: Dict[int, CreneauDTO] = {c.id: c for c in creneaux}
        self._salles_index: Dict[int, SalleDTO] = {s.id: s for s in salles}

        exams_seen: Set[Tuple[int, int, str, int]] = set()
        for section_id, matiere_id, semestre, creneau_id, salle_id in planifs_existantes:
            exam_key = (section_id, matiere_id, semestre, creneau_id)
            c = self._creneaux_index.get(creneau_id)
            s = self._salles_index.get(salle_id)

            self._matieres_planifiees.add((section_id, matiere_id, semestre))
            if c is None:
                continue

            if exam_key not in exams_seen:
                exams_seen.add(exam_key)
                self._enregistrer_exam(section_id, matiere_id, semestre, c)

            if s is not None:
                self._enregistrer_salle(section_id, c, s)

    def salle_est_libre(self, salle_id: int, creneau: CreneauDTO) -> bool:
        key = (creneau.date, creneau.heure_debut)
        return salle_id not in self._salles_occupees.get(key, set())

    def section_est_libre(self, section_id: int, creneau: CreneauDTO) -> bool:
        key = (creneau.date, creneau.heure_debut)
        return section_id not in self._sections_occupees.get(key, set())

    def est_deja_planifiee(self, section_id: int, matiere_id: int, semestre: str) -> bool:
        return (section_id, matiere_id, semestre) in self._matieres_planifiees

    def nb_examens_section_jour(self, section_id: int, d: date) -> int:
        return self._examens_par_section_jour.get((section_id, d), 0)

    def batiments_section_jour(self, section_id: int, d: date) -> Set[str]:
        return self._batiments_par_section_jour.get((section_id, d), set())

    def total_planifs_ce_jour(self, d: date) -> int:
        return sum(v for (_, jour), v in self._examens_par_section_jour.items() if jour == d)

    def enregistrer(self, resultat: ResultatPlanification) -> None:
        sm = resultat.section_matiere
        self._enregistrer_exam(sm.section_id, sm.matiere_id, sm.semestre, resultat.creneau)
        for attr in resultat.attributions:
            self._enregistrer_salle(sm.section_id, resultat.creneau, attr.salle)

    def _enregistrer_exam(self, section_id: int, matiere_id: int, semestre: str, creneau: CreneauDTO) -> None:
        key_slot = (creneau.date, creneau.heure_debut)
        key_day = (section_id, creneau.date)
        self._matieres_planifiees.add((section_id, matiere_id, semestre))
        self._sections_occupees.setdefault(key_slot, set()).add(section_id)
        self._examens_par_section_jour[key_day] = self._examens_par_section_jour.get(key_day, 0) + 1

    def _enregistrer_salle(self, section_id: int, creneau: CreneauDTO, salle: SalleDTO) -> None:
        key_slot = (creneau.date, creneau.heure_debut)
        key_day = (section_id, creneau.date)
        self._salles_occupees.setdefault(key_slot, set()).add(salle.id)
        self._batiments_par_section_jour.setdefault(key_day, set()).add(salle.batiment)


def _duree_creneau_minutes(creneau: CreneauDTO) -> int:
    return (creneau.heure_fin.hour * 60 + creneau.heure_fin.minute) - (
        creneau.heure_debut.hour * 60 + creneau.heure_debut.minute
    )


def _duree_epreuve(sm: SectionMatiereDTO) -> int:
    return sm.duree_ds if sm.type_epreuve == "DS" else sm.duree_examen


def verifier_c14(sm: SectionMatiereDTO, creneau: CreneauDTO) -> None:
    duree_creneau = _duree_creneau_minutes(creneau)
    duree_epreuve = _duree_epreuve(sm)
    if duree_epreuve > duree_creneau:
        raise ConflitContrainte(
            "C14",
            f"Required duration {duree_epreuve} min > slot duration {duree_creneau} min ({creneau.libelle}).",
        )


def decouper_en_groupes(effectif_total: int, capacite_cible: int) -> list[int]:
    if effectif_total <= 0 or capacite_cible <= 0:
        return []

    nb_groupes = max(1, ceil(effectif_total / capacite_cible))
    base = effectif_total // nb_groupes
    reste = effectif_total % nb_groupes
    return [base + 1] * reste + [base] * (nb_groupes - reste)


def calculer_groupes(effectif_total: int, creneau: CreneauDTO, contexte: ContextePlanification) -> Optional[List[int]]:
    salles_libres = [s for s in contexte.salles_triees if contexte.salle_est_libre(s.id, creneau)]
    if not salles_libres:
        return None

    capacite_max = max(s.capacite for s in salles_libres)
    if effectif_total <= capacite_max:
        return [effectif_total]

    nb_groupes = ceil(effectif_total / capacite_max)
    if len(salles_libres) < nb_groupes:
        return None

    return decouper_en_groupes(effectif_total, capacite_max)


def _priorite_departement_salle(salle: SalleDTO, section_departement_id: int | None) -> int:
    if section_departement_id is None:
        return 0 if salle.departement_id is None else 1
    if salle.departement_id == section_departement_id:
        return 0
    if salle.departement_id is None:
        return 1
    return 2


def trouver_attribution_salles(
    groupes: List[int],
    creneau: CreneauDTO,
    contexte: ContextePlanification,
    section_id: int,
    section_departement_id: int | None = None,
) -> Optional[List[AttributionSalle]]:
    batiments_preferes = contexte.batiments_section_jour(section_id, creneau.date)
    disponibles = [s for s in contexte.salles_triees if contexte.salle_est_libre(s.id, creneau)]
    disponibles.sort(
        key=lambda s: (
            0 if s.batiment in batiments_preferes else 1,
            _priorite_departement_salle(s, section_departement_id),
            s.capacite,
        )
    )

    attributions: List[AttributionSalle] = []
    deja_utilisees: Set[int] = set()

    for effectif_groupe in groupes:
        salle = next(
            (
                s
                for s in disponibles
                if s.capacite >= effectif_groupe and s.id not in deja_utilisees
            ),
            None,
        )
        if salle is None:
            return None
        attributions.append(AttributionSalle(effectif_groupe, salle))
        deja_utilisees.add(salle.id)
    return attributions


def score_souples(
    sm: SectionMatiereDTO,
    creneau: CreneauDTO,
    attributions: List[AttributionSalle],
    contexte: ContextePlanification,
) -> int:
    score = 0

    if contexte.nb_examens_section_jour(sm.section_id, creneau.date) > 0:
        score += 10

    score += contexte.total_planifs_ce_jour(creneau.date) * 2

    batiments_preferes = contexte.batiments_section_jour(sm.section_id, creneau.date)
    for attr in attributions:
        if attr.salle.batiment in batiments_preferes:
            score -= 5

    # C5bis: Bonus if room is from section's department
    if sm.section.departement_id is not None:
        for attr in attributions:
            if attr.salle.departement_id == sm.section.departement_id:
                score -= 3
            elif attr.salle.departement_id is None:
                # Shared rooms (no department) get a smaller bonus
                score -= 1

    return score


def _filtrer_matieres_a_planifier(
    matieres: List[SectionMatiereDTO],
    contexte: ContextePlanification,
    *,
    semestre: str,
    scope_section_ids: set[int] | None,
) -> list[SectionMatiereDTO]:
    filtered: list[SectionMatiereDTO] = []
    for sm in matieres:
        if sm.semestre != semestre:
            continue
        if scope_section_ids and sm.section_id not in scope_section_ids:
            continue
        if sm.type_epreuve == "EXAMEN_FINAL" and not sm.a_examen_final:
            continue
        if sm.type_epreuve == "DS" and not sm.a_ds:
            continue
        if contexte.est_deja_planifiee(sm.section_id, sm.matiere_id, sm.semestre):
            continue
        filtered.append(sm)
    return filtered


class Planificateur:
    """Pure planner layer, independent from SQLAlchemy persistence."""

    def __init__(
        self,
        session: SessionDTO,
        matieres: List[SectionMatiereDTO],
        contexte: ContextePlanification,
        known_section_matiere_ids: set[int] | None = None,
        semestre: str = "S1",
        scope_section_ids: set[int] | None = None,
    ) -> None:
        if session.statut == "PUBLIEE":
            raise SessionVerrouillee(f"[C15/C17] Session {session.id} is published.")

        self.session = session
        self.contexte = contexte
        self.known_section_matiere_ids = known_section_matiere_ids
        self.semestre = semestre
        self.scope_section_ids = scope_section_ids

        filtered = _filtrer_matieres_a_planifier(
            matieres,
            contexte,
            semestre=semestre,
            scope_section_ids=scope_section_ids,
        )

        self.matieres = sorted(
            filtered,
            key=lambda sm: (
                -sm.section.nb_etudiants,
                -sm.matiere.coefficient,
                -_duree_epreuve(sm),
            ),
        )

    def generer(self) -> Tuple[List[ResultatPlanification], RapportGeneration]:
        rapport = RapportGeneration()
        resultats: List[ResultatPlanification] = []

        logger.info("Generation start - session %s, %d subjects", self.session.id, len(self.matieres))

        for sm in self.matieres:
            try:
                resultat = self._planifier_matiere(sm)
                self.contexte.enregistrer(resultat)
                resultats.append(resultat)
                rapport.nb_crees += 1
            except ConflitContrainte as exc:
                rapport.ajouter_conflit(sm, exc.contrainte, str(exc))
                logger.warning("Conflict %s on %s/%s", exc.contrainte, sm.matiere.intitule, sm.section.nom)

        logger.info("Generation done - created=%d conflicts=%d", rapport.nb_crees, rapport.nb_conflits)
        return resultats, rapport

    def _planifier_matiere(self, sm: SectionMatiereDTO) -> ResultatPlanification:
        if sm.id <= 0:
            raise ConflitContrainte("C16", "section_matiere must exist before planning.")

        if self.known_section_matiere_ids is not None and sm.id not in self.known_section_matiere_ids:
            raise ConflitContrainte("C16", f"section_matiere {sm.id} not found in referential data.")

        if self.contexte.est_deja_planifiee(sm.section_id, sm.matiere_id, sm.semestre):
            raise ConflitContrainte("C12", "Subject already planned for this section and session.")

        meilleur: Optional[ResultatPlanification] = None
        meilleur_score = float("inf")

        for creneau in self.contexte.creneaux_disponibles:
            try:
                verifier_c14(sm, creneau)
            except ConflitContrainte:
                continue

            if not self.contexte.section_est_libre(sm.section_id, creneau):
                continue

            if (
                self.contexte.nb_examens_section_jour(sm.section_id, creneau.date)
                >= settings.max_examens_par_jour_section
            ):
                continue

            groupes = calculer_groupes(sm.section.nb_etudiants, creneau, self.contexte)
            if groupes is None:
                continue

            attributions = trouver_attribution_salles(
                groupes,
                creneau,
                self.contexte,
                sm.section_id,
                sm.section.departement_id,
            )
            if attributions is None:
                continue

            score = score_souples(sm, creneau, attributions, self.contexte)

            if score < meilleur_score:
                meilleur_score = score
                meilleur = ResultatPlanification(
                    section_matiere=sm,
                    creneau=creneau,
                    attributions=attributions,
                    score_souples=score,
                )

            if meilleur_score <= 0:
                break

        if meilleur is None:
            raise ConflitContrainte(
                "C1/C7/C8",
                "No slot satisfies all hard constraints for this subject/section.",
            )

        return meilleur


def _build_planner_inputs(
    request: GenerationRequest,
    existing_planifs: list[Planification],
) -> tuple[SessionDTO, list[SectionMatiereDTO], ContextePlanification, dict[int, object]]:
    session = SessionDTO(
        id=request.session_id,
        statut=request.session_statut.value,
        date_debut=request.session_date_debut,
        date_fin=request.session_date_fin,
        type_session="EXAMEN",
        annee_universitaire=request.annee_universitaire,
    )

    creneaux: list[CreneauDTO] = []
    creneau_key_to_id: dict[tuple[date, time], int] = {}
    for idx, c in enumerate(sorted(request.creneaux, key=lambda x: (x.date_examen, x.heure_debut)), start=1):
        creneaux.append(
            CreneauDTO(
                id=idx,
                date=c.date_examen,
                heure_debut=c.heure_debut,
                heure_fin=c.heure_fin,
                libelle=f"{c.date_examen} {c.heure_debut.strftime('%H:%M')}",
            )
        )
        creneau_key_to_id[(c.date_examen, c.heure_debut)] = idx

    salles: list[SalleDTO] = []
    salle_code_to_id: dict[str, int] = {}
    for idx, s in enumerate(sorted(request.salles, key=lambda x: x.capacite), start=1):
        salles.append(
            SalleDTO(
                id=idx,
                code=s.salle_id,
                capacite=s.capacite,
                batiment=s.batiment or "",
                departement_id=s.departement_id,
            )
        )
        salle_code_to_id[s.salle_id] = idx

    matieres: list[SectionMatiereDTO] = []
    task_by_sm_id: dict[int, object] = {}
    for task in request.tasks:
        matieres.append(
            SectionMatiereDTO(
                id=task.section_matiere_id,
                section=SectionDTO(
                    id=task.section_id,
                    nom=f"Section-{task.section_id}",
                    nb_etudiants=task.section_nb_etudiants,
                    departement_id=task.section_departement_id,
                ),
                matiere=MatiereDTO(
                    id=task.matiere_id or task.section_matiere_id,
                    code=f"MAT-{task.matiere_id or task.section_matiere_id}",
                    intitule=task.matiere,
                    coefficient=task.coefficient,
                    a_examen_final=task.a_examen_final,
                    a_ds=task.a_ds,
                ),
                section_id=task.section_id,
                matiere_id=task.matiere_id or task.section_matiere_id,
                semestre=task.semestre,
                a_examen_final=task.a_examen_final,
                a_ds=task.a_ds,
                duree_examen=task.duree,
                duree_ds=task.duree,
                type_epreuve=task.type_epreuve.value,
                nb_surveillants_requis=task.nb_surveillants_requis,
            )
        )
        task_by_sm_id[task.section_matiere_id] = task

    planifs_existantes: list[tuple[int, int, str, int, int]] = []
    for planif in existing_planifs:
        creneau_id = creneau_key_to_id.get((planif.date_examen, planif.heure_debut))
        if creneau_id is None:
            continue
        task = task_by_sm_id.get(planif.section_matiere_id)
        matiere_id = (task.matiere_id if task and task.matiere_id else planif.section_matiere_id)
        semestre = task.semestre if task else request.semestre
        for salle in planif.salles_affectees:
            salle_id = salle_code_to_id.get(salle.salle_id)
            if salle_id is None:
                continue
            planifs_existantes.append((planif.section_id, matiere_id, semestre, creneau_id, salle_id))

    contexte = ContextePlanification(
        session=session,
        creneaux=creneaux,
        salles=salles,
        planifs_existantes=planifs_existantes,
    )
    return session, matieres, contexte, task_by_sm_id


def _to_planification_create(
    request: GenerationRequest,
    resultat: ResultatPlanification,
    task,
) -> PlanificationCreate:
    type_epreuve = TypeEpreuve(task.type_epreuve.value if hasattr(task.type_epreuve, "value") else task.type_epreuve)
    mode = ModeAffectation(request.mode.value if hasattr(request.mode, "value") else request.mode)

    salles = [
        PlanifSalleAssign(
            salle_id=attr.salle.code,
            salle_capacite=attr.salle.capacite,
            salle_batiment=attr.salle.batiment or None,
            groupe_id=idx,
            groupe_effectif=attr.groupe_effectif,
        )
        for idx, attr in enumerate(resultat.attributions, start=1)
    ]

    return PlanificationCreate(
        session_id=request.session_id,
        section_id=resultat.section_matiere.section_id,
        section_matiere_id=resultat.section_matiere.id,
        matiere=resultat.section_matiere.matiere.intitule,
        type_epreuve=type_epreuve,
        mode_affectation=mode,
        statut=StatutPlanification.BROUILLON,
        date_examen=resultat.creneau.date,
        heure_debut=resultat.creneau.heure_debut,
        heure_fin=resultat.creneau.heure_fin,
        session_date_debut=request.session_date_debut,
        session_date_fin=request.session_date_fin,
        session_statut=request.session_statut,
        duree=task.duree,
        coefficient=task.coefficient,
        section_nb_etudiants=task.section_nb_etudiants,
        nb_groupes=len(salles),
        nb_surveillants_requis=task.nb_surveillants_requis,
        a_examen_final=task.a_examen_final,
        a_ds=task.a_ds,
        salles=salles,
    )


def generer(
    request: GenerationRequest,
    engine: ContrainteEngine,
    existing_planifs: list[Planification],
    db: Session,
    known_section_matiere_ids: set[int] | None = None,
) -> tuple[list[PlanificationCreate], GenerationResult]:
    """Compatibility wrapper used by the service layer."""
    del engine
    del db

    session, matieres, contexte, task_by_sm_id = _build_planner_inputs(request, existing_planifs)
    scope_section_ids = set(request.scope_section_ids) if request.scope_section_ids else None

    try:
        planner = Planificateur(
            session,
            matieres,
            contexte,
            known_section_matiere_ids,
            semestre=request.semestre,
            scope_section_ids=scope_section_ids,
        )
        resultats, rapport = planner.generer()
    except SessionVerrouillee:
        return [], GenerationResult(nb_crees=0, nb_conflits=1, conflits=["[C15/C17] Session is published."])

    creates: list[PlanificationCreate] = []
    for r in resultats:
        task = task_by_sm_id.get(r.section_matiere.id)
        if task is None:
            continue
        creates.append(_to_planification_create(request, r, task))

    conflits = [
        f"[{c.contrainte}] {c.section_nom} / {c.matiere_intitule} - {c.message}"
        for c in rapport.conflits
    ]
    return creates, GenerationResult(nb_crees=len(creates), nb_conflits=len(conflits), conflits=conflits)
