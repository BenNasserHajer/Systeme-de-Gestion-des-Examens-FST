"""Constraint engine used by P1 exam planning logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.planification import Planification
from app.schemas.planification import PlanificationCreate, TypeEpreuve


def _time_to_minutes(value) -> int:
    return value.hour * 60 + value.minute


class Contrainte(ABC):
    """Base class for all planning constraints."""

    def __init__(self, priorite: int, active: bool = True, dure: bool = True):
        self.priorite = priorite
        self.active = active
        self.dure = dure

    @abstractmethod
    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        """Return True when the constraint is satisfied."""

    @abstractmethod
    def get_message(self) -> str:
        """Return a conflict/warning message when violated."""


class ContrainteSalleOccupee(Contrainte):
    """C1: one room cannot host two exams on the same slot."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = contexte.get("existing_planifs", [])
        excluded_id = contexte.get("exclude_planif_id")

        requested_salles = {s.salle_id for s in planif.salles}
        if not requested_salles:
            return True

        for other in existing:
            if excluded_id is not None and other.id == excluded_id:
                continue
            if other.date_examen != planif.date_examen or other.heure_debut != planif.heure_debut:
                continue
            for affectation in other.salles_affectees:
                if affectation.salle_id in requested_salles:
                    return False
        return True

    def get_message(self) -> str:
        return "C1: une salle ne peut pas etre affectee a deux epreuves sur le meme creneau."


class ContrainteCapaciteSalle(Contrainte):
    """C2: assigned room capacity must cover group size."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        if not planif.salles:
            return False
        for groupe in planif.salles:
            if groupe.salle_capacite < groupe.groupe_effectif:
                return False
        return sum(x.groupe_effectif for x in planif.salles) >= planif.section_nb_etudiants

    def get_message(self) -> str:
        return "C2: capacite salle insuffisante pour couvrir les effectifs des groupes."


class ContrainteCreneauSession(Contrainte):
    """C3/C18: slot date must stay inside the session period."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        return planif.session_date_debut <= planif.date_examen <= planif.session_date_fin

    def get_message(self) -> str:
        return "C3/C18: creneau hors periode officielle de la session."


class ContraintePasDimanche(Contrainte):
    """C4: no exam on Sunday."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        return planif.date_examen.weekday() != 6

    def get_message(self) -> str:
        return "C4: aucun examen ne doit etre planifie le dimanche."


class ContrainteSectionUnique(Contrainte):
    """C7/C14: a section cannot have two exams at the same slot."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = contexte.get("existing_planifs", [])
        excluded_id = contexte.get("exclude_planif_id")
        for other in existing:
            if excluded_id is not None and other.id == excluded_id:
                continue
            if other.section_id != planif.section_id:
                continue
            if other.date_examen == planif.date_examen and other.heure_debut == planif.heure_debut:
                return False
        return True

    def get_message(self) -> str:
        return "C7/C14: une section ne peut pas avoir deux epreuves sur le meme creneau."


class ContrainteSectionMatiereUnique(Contrainte):
    """C6/C12: one planification per (section_matiere, session, type)."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = contexte.get("existing_planifs", [])
        excluded_id = contexte.get("exclude_planif_id")
        for other in existing:
            if excluded_id is not None and other.id == excluded_id:
                continue
            if (
                other.section_matiere_id == planif.section_matiere_id
                and other.session_id == planif.session_id
                and other.type_epreuve == planif.type_epreuve.value
            ):
                return False
        return True

    def get_message(self) -> str:
        return "C6/C12: doublon detecte pour (section_matiere, session, type_epreuve)."


class ContrainteDecoupageObligatoire(Contrainte):
    """C8: splitting is mandatory when no room can host the full section."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        capacities = [s.salle_capacite for s in planif.salles]
        if not capacities:
            return False
        max_cap = max(capacities)
        if planif.section_nb_etudiants <= max_cap:
            return True
        return len(planif.salles) >= 2

    def get_message(self) -> str:
        return "C8: decoupage obligatoire en plusieurs groupes/salles non respecte."


class ContrainteMatiereEligible(Contrainte):
    """C11: only eligible subject types should be scheduled."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        if planif.type_epreuve == TypeEpreuve.EXAMEN_FINAL:
            return planif.a_examen_final
        return planif.a_ds

    def get_message(self) -> str:
        return "C11: matiere non eligible pour ce type d'epreuve."


class ContrainteDureeCreneau(Contrainte):
    """C15: exam duration must fit inside the slot."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        creneau = _time_to_minutes(planif.heure_fin) - _time_to_minutes(planif.heure_debut)
        return planif.duree <= creneau

    def get_message(self) -> str:
        return "C15: duree epreuve superieure a la duree du creneau."


class ContrainteSectionMatiereExists(Contrainte):
    """C16: section_matiere must be present before planning."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        known_ids: set[int] | None = contexte.get("known_section_matiere_ids")
        if known_ids is None:
            return planif.section_matiere_id > 0
        return planif.section_matiere_id in known_ids

    def get_message(self) -> str:
        return "C16: section_matiere introuvable pour cette planification."


class ContrainteSessionEditable(Contrainte):
    """C17: no create/update on published sessions."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        return planif.session_statut.value in {"BROUILLON", "VALIDEE"}

    def get_message(self) -> str:
        return "C17: session publiee, modifications interdites."


class ContrainteBatimentConsecutif(Contrainte):
    """C5 soft preference: keep same section in same building during the day."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = contexte.get("existing_planifs", [])
        candidate_batiments = {s.salle_batiment for s in planif.salles if s.salle_batiment}
        if not candidate_batiments:
            return True
        for other in existing:
            if other.section_id != planif.section_id or other.date_examen != planif.date_examen:
                continue
            other_batiments = {
                salle.salle_batiment
                for salle in other.salles_affectees
                if getattr(salle, "salle_batiment", None)
            }
            if other_batiments and candidate_batiments.isdisjoint(other_batiments):
                return False
        return True

    def get_message(self) -> str:
        return "C5 (souple): preferer le meme batiment pour une section sur la meme journee."


class ContrainteEquilibrageGroupes(Contrainte):
    """C9 soft preference: balanced group sizes (max delta = 1)."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        if len(planif.salles) <= 1:
            return True
        effectifs = [s.groupe_effectif for s in planif.salles]
        return max(effectifs) - min(effectifs) <= 1

    def get_message(self) -> str:
        return "C9 (souple): groupes non equilibres, ecart > 1 etudiant."


class ContrainteEspacementExamens(Contrainte):
    """C10 soft preference: avoid consecutive slots the same day for a section."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = contexte.get("existing_planifs", [])
        for other in existing:
            if other.section_id != planif.section_id or other.date_examen != planif.date_examen:
                continue
            diff = abs(_time_to_minutes(other.heure_debut) - _time_to_minutes(planif.heure_debut))
            if diff <= 180:
                return False
        return True

    def get_message(self) -> str:
        return "C10 (souple): espacement insuffisant entre deux examens de la section."


class ContrainteRepartitionUniforme(Contrainte):
    """C13 soft preference: avoid clustering section exams at period start."""

    def verifier(self, planif: PlanificationCreate, contexte: dict, db: Session) -> bool:
        existing: list[Planification] = [
            p for p in contexte.get("existing_planifs", []) if p.section_id == planif.section_id
        ]
        if len(existing) < 2:
            return True

        span = (planif.session_date_fin - planif.session_date_debut).days
        if span <= 2:
            return True

        threshold = planif.session_date_debut + timedelta(days=max(1, span // 3))
        early_count = sum(1 for p in existing if p.date_examen <= threshold)
        return not (planif.date_examen <= threshold and early_count >= len(existing) - 1)

    def get_message(self) -> str:
        return "C13 (souple): repartition non uniforme sur la periode de session."


class ContrainteEngine:
    """Executes all constraints and separates hard conflicts from soft warnings."""

    def __init__(self, contraintes: list[Contrainte]):
        self.contraintes = sorted(contraintes, key=lambda c: c.priorite)

    def verifier_toutes(
        self,
        planif: PlanificationCreate,
        contexte: dict,
        db: Session,
    ) -> tuple[list[str], list[str]]:
        erreurs: list[str] = []
        warnings: list[str] = []

        for contrainte in self.contraintes:
            if not contrainte.active:
                continue
            if contrainte.verifier(planif, contexte, db):
                continue
            if contrainte.dure:
                erreurs.append(contrainte.get_message())
            else:
                warnings.append(contrainte.get_message())
        return erreurs, warnings


def build_default_engine() -> ContrainteEngine:
    """Return the standard set of P1 constraints C1..C18."""

    return ContrainteEngine(
        [
            ContrainteSalleOccupee(priorite=1, dure=True),
            ContrainteCapaciteSalle(priorite=1, dure=True),
            ContrainteCreneauSession(priorite=1, dure=True),
            ContraintePasDimanche(priorite=1, dure=True),
            ContrainteSectionUnique(priorite=1, dure=True),
            ContrainteSectionMatiereUnique(priorite=1, dure=True),
            ContrainteDecoupageObligatoire(priorite=1, dure=True),
            ContrainteMatiereEligible(priorite=1, dure=True),
            ContrainteDureeCreneau(priorite=1, dure=True),
            ContrainteSectionMatiereExists(priorite=1, dure=True),
            ContrainteSessionEditable(priorite=1, dure=True),
            ContrainteBatimentConsecutif(priorite=2, dure=False),
            ContrainteEquilibrageGroupes(priorite=2, dure=False),
            ContrainteEspacementExamens(priorite=3, dure=False),
            ContrainteRepartitionUniforme(priorite=3, dure=False),
        ]
    )
