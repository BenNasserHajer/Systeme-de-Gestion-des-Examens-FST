# """Business logic for surveillance module."""

# from typing import Optional
# from datetime import datetime

# from sqlalchemy import func
# from sqlalchemy.orm import Session as SQLSession

# from app.algorithms.surv_auto import AutomaticAffectationAlgorithm
# from app.crud.crud_surv import (
#     create_surveillance,
#     create_surveillances_batch,
#     delete_surveillance,
#     delete_surveillance_by_id,
#     delete_surveillances_for_planification,
#     get_surveillance,
#     get_surveillance_by_planif_and_enseignant,
#     get_surveillances_for_enseignant,
#     get_surveillances_for_planification,
#     list_surveillances,
#     replace_surveillance,
#     update_surveillance,
#     get_enseignant_charge_for_year,
#     count_surveillances_for_enseignant,
# )
# from app.models.surveillance import Surveillance
# from app.models.planification_examen import PlanificationExamen
# from app.models.enseignant import Enseignant, ChargeHoraire
# from app.models.disponibilite import DisponibiliteEnseignant
# from app.models.salle_session import Session
# from app.schemas.surveillance_schema import (
#     SurveillanceCreate,
#     SurveillanceUpdate,
#     ManualAssignmentRequest,
#     ManualAssignmentBatchRequest,
#     EnseignantDisponible,
# )


# class SurvService:
#     """Business logic layer for surveillance module."""

#     def __init__(self, db: SQLSession):
#         self.db = db
#         self.algorithm = AutomaticAffectationAlgorithm(db)

#     # ========================================================================
#     # CONSULTATION & LISTING
#     # ========================================================================

#     def get_all_surveillances(
#         self,
#         *,
#         planification_id: Optional[int] = None,
#         enseignant_id: Optional[int] = None,
#         session_id: Optional[int] = None,
#         est_externe: Optional[bool] = None,
#         skip: int = 0,
#         limit: int = 50,
#     ) -> list[Surveillance]:
#         """Get all surveillances with optional filters."""
#         return list_surveillances(
#             self.db,
#             planification_id=planification_id,
#             enseignant_id=enseignant_id,
#             session_id=session_id,
#             est_externe=est_externe,
#             skip=skip,
#             limit=limit,
#         )

#     def get_surveillance_by_id(self, surveillance_id: int) -> Optional[Surveillance]:
#         """Get a surveillance by ID."""
#         return get_surveillance(self.db, surveillance_id)

#     def get_surveillances_for_planification(
#         self, planification_id: int
#     ) -> list[Surveillance]:
#         """Get all surveillances for a planification."""
#         return get_surveillances_for_planification(self.db, planification_id)

#     def get_surveillances_for_enseignant(
#         self,
#         enseignant_id: int,
#         annee_universitaire: Optional[str] = None,
#     ) -> list[Surveillance]:
#         """Get all surveillances for an enseignant."""
#         return get_surveillances_for_enseignant(
#             self.db,
#             enseignant_id,
#             annee_universitaire,
#         )

#     # ========================================================================
#     # CREATION & MODIFICATION
#     # ========================================================================

#     def create_surveillance(self, payload: SurveillanceCreate) -> Surveillance:
#         """Create a new surveillance."""
#         return create_surveillance(self.db, payload)

#     def update_surveillance(
#         self,
#         surveillance_id: int,
#         payload: SurveillanceUpdate,
#     ) -> Optional[Surveillance]:
#         """Update a surveillance."""
#         surveillance = get_surveillance(self.db, surveillance_id)
#         if not surveillance:
#             return None
#         return update_surveillance(self.db, surveillance, payload)

#     def delete_surveillance(self, surveillance_id: int) -> bool:
#         """Delete a surveillance (physical deletion)."""
#         return delete_surveillance_by_id(self.db, surveillance_id)

#     def replace_surveillance(
#         self,
#         surveillance_id: int,
#         new_enseignant_id: int,
#         motif: str,
#     ) -> Optional[tuple]:
#         """Replace an enseignant on a surveillance."""
#         old = get_surveillance(self.db, surveillance_id)
#         if not old:
#             return None
#         return replace_surveillance(self.db, old, new_enseignant_id, motif)

#     # ========================================================================
#     # AUTOMATIC AFFECTATION
#     # ========================================================================

#     def affecter_session_automatique(self, session_id: int) -> tuple:
#         """
#         Lancer l'affectation automatique pour toutes les planifications VALIDEE
#         d'une session.

#         Returns:
#             - results: List of PlanificationAffectationResult
#             - message: Status message
#         """
#         return self.algorithm.affecter_session(session_id)

#     # ========================================================================
#     # MANUAL AFFECTATION
#     # ========================================================================

#     def affecter_planification_manuellement(
#         self,
#         request: ManualAssignmentRequest,
#     ) -> dict:
#         """
#         Handle manual affectation for a single conflicted planification.

#         Validates constraints 1 and 4 only.
#         """
#         # Récupérer la planification
#         planif = self.db.query(PlanificationExamen).filter(
#             PlanificationExamen.id == request.planification_id,
#             PlanificationExamen.session_id == request.session_id,
#         ).first()

#         if not planif:
#             raise ValueError(f"Planification {request.planification_id} non trouvée dans la session")

#         # Récupérer la session pour l'année universitaire
#         session = self.db.query(Session).filter(
#             Session.id == request.session_id,
#         ).first()

#         # Valider les enseignants et créer les surveillances
#         surveillances_creees = []
#         erreurs = []

#         for ens_id in request.enseignant_ids:
#             # Vérifier contrainte 1 (disponibilité)
#             if not self._check_disponibilite_temporelle(ens_id, planif):
#                 erreurs.append({
#                     "enseignant_id": ens_id,
#                     "raison": "INDISPONIBLE",
#                 })
#                 continue

#             # Vérifier contrainte 4 (non-simultanéité)
#             if self._check_conflit_simultaneite(ens_id, planif):
#                 erreurs.append({
#                     "enseignant_id": ens_id,
#                     "raison": "DEJA_AFFECTE",
#                 })
#                 continue

#             # Déterminer si externe
#             ens = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
#             est_externe = ens.departement_id != planif.departement_id

#             motif = request.motifs_externes.get(ens_id) if est_externe else None

#             payload = SurveillanceCreate(
#                 planification_id=request.planification_id,
#                 enseignant_id=ens_id,
#                 charge=float(planif.duree / 60),
#                 mode_affectation="MANUELLE",
#                 est_externe=est_externe,
#                 motif_externe=motif,
#             )

#             surv = create_surveillance(self.db, payload)
#             surveillances_creees.append(surv)

#         if erreurs:
#             # Tout ou rien: si une erreur, on delete tout ce qui a été créé
#             for surv in surveillances_creees:
#                 delete_surveillance(self.db, surv)
#             raise ValueError(f"Validation échouée: {erreurs}")

#         return {
#             "planification_id": request.planification_id,
#             "statut": "CONFLIT_RESOLU",
#             "surveillants_inseres": len(surveillances_creees),
#         }

#     def affecter_session_manuellement(
#         self,
#         request: ManualAssignmentBatchRequest,
#     ) -> dict:
#         """
#         Handle full manual affectation for an entire session.

#         Validates constraints 1 and 4 only.
#         One transaction for all planifications.
#         """
#         # Récupérer la session
#         session = self.db.query(SessionModel).filter(
#             SessionModel.id == request.session_id,
#         ).first()

#         if not session:
#             raise ValueError(f"Session {request.session_id} non trouvée")

#         annee_univ = session.annee_universitaire

#         # Valider toutes les affectations d'abord
#         all_valid_payloads = []
#         erreurs_globales = []

#         for planif_id, ens_ids in request.affectations.items():
#             # Récupérer la planification
#             planif = self.db.query(Planification).filter(
#                 Planification.id == planif_id,
#                 Planification.session_id == request.session_id,
#             ).first()

#             if not planif:
#                 erreurs_globales.append({
#                     "planification_id": planif_id,
#                     "erreur": "Non trouvée",
#                 })
#                 continue

#             for ens_id in ens_ids:
#                 # Vérifier contrainte 1
#                 if not self._check_disponibilite_temporelle(ens_id, planif):
#                     erreurs_globales.append({
#                         "planification_id": planif_id,
#                         "enseignant_id": ens_id,
#                         "raison": "INDISPONIBLE",
#                     })
#                     continue

#                 # Vérifier contrainte 4
#                 if self._check_conflit_simultaneite(ens_id, planif):
#                     erreurs_globales.append({
#                         "planification_id": planif_id,
#                         "enseignant_id": ens_id,
#                         "raison": "DEJA_AFFECTE",
#                     })
#                     continue

#                 # Déterminer si externe
#                 ens = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
#                 est_externe = ens.departement_id != planif.departement_id
#                 motif = request.motifs_externes.get(ens_id) if est_externe else None

#                 payload = SurveillanceCreate(
#                     planification_id=planif_id,
#                     enseignant_id=ens_id,
#                     charge=float(planif.duree / 60),
#                     mode_affectation="MANUELLE",
#                     est_externe=est_externe,
#                     motif_externe=motif,
#                 )

#                 all_valid_payloads.append(payload)

#         if erreurs_globales:
#             raise ValueError(f"Validation échouée: {erreurs_globales}")

#         # Transaction unique pour toutes les surveillances
#         surveillances = create_surveillances_batch(self.db, all_valid_payloads)

#         return {
#             "session_id": request.session_id,
#             "statut": "SUCCES",
#             "total_surveillances_inserees": len(surveillances),
#         }

#     # ========================================================================
#     # HELPER METHODS FOR CONSTRAINT CHECKING
#     # ========================================================================

#     def _check_disponibilite_temporelle(
#         self,
#         enseignant_id: int,
#         planif: Planification,
#     ) -> bool:
#         """Vérifier disponibilité temporelle (Contrainte 1)."""
#         from app.models.creneau import Creneau

#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # Vérifier indisponibilités
#         indisponibilites = self.db.query(DisponibiliteEnseignant).filter(
#             DisponibiliteEnseignant.enseignant_id == enseignant_id,
#             DisponibiliteEnseignant.date == creneau.date,
#             DisponibiliteEnseignant.type_dispo.in_(["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]),
#         ).all()

#         for indispo in indisponibilites:
#             if indispo.heure_debut < creneau.heure_fin and indispo.heure_fin > creneau.heure_debut:
#                 return False

#         return True

#     def _check_conflit_simultaneite(
#         self,
#         enseignant_id: int,
#         planif: Planification,
#     ) -> bool:
#         """Vérifier non-simultanéité (Contrainte 4)."""
#         from app.models.creneau import Creneau

#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # Chercher conflits
#         conflits = self.db.query(Surveillance).join(Planification).join(Creneau).filter(
#             Surveillance.enseignant_id == enseignant_id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#             Creneau.date == creneau.date,
#             Creneau.heure_debut == creneau.heure_debut,
#         ).all()

#         return len(conflits) > 0

#     # ========================================================================
#     # ANALYTICS & REPORTS
#     # ========================================================================

#     def get_volume_restant_enseignant(
#         self,
#         enseignant_id: int,
#         annee_universitaire: str,
#     ) -> dict:
#         """Get volume information for an enseignant."""
#         charge_horaire = self.db.query(ChargeHoraire).filter(
#             ChargeHoraire.enseignant_id == enseignant_id,
#             ChargeHoraire.annee_univ == annee_universitaire,
#         ).first()

#         volume_horaire = charge_horaire.volume_horaire if charge_horaire else 0.0
#         volume_consomme = get_enseignant_charge_for_year(
#             self.db,
#             enseignant_id,
#             annee_universitaire,
#         )
#         nb_surveillances = count_surveillances_for_enseignant(
#             self.db,
#             enseignant_id,
#             annee_universitaire,
#         )

#         return {
#             "enseignant_id": enseignant_id,
#             "volume_horaire": volume_horaire,
#             "volume_consomme": volume_consomme,
#             "volume_restant": volume_horaire - volume_consomme,
#             "nb_surveillances": nb_surveillances,
#         }

#     def get_enseignants_disponibles_pour_planification(
#         self,
#         planif_id: int,
#     ) -> list[EnseignantDisponible]:
#         """
#         Get all available enseignants for a planification (for conflict resolution).

#         Applies only constraints 1 and 4 (no department filter).
#         Returns all departments.
#         """
#         planif = self.db.query(Planification).filter(Planification.id == planif_id).first()
#         if not planif:
#             return []

#         session = self.db.query(SessionModel).filter(
#             SessionModel.id == planif.session_id,
#         ).first()
#         annee_univ = session.annee_universitaire if session else None

#         # Récupérer tous les enseignants
#         enseignants = self.db.query(Enseignant).all()
#         disponibles = []

#         for ens in enseignants:
#             # Contrainte 1: Disponibilité
#             if not self._check_disponibilite_temporelle(ens.id, planif):
#                 continue

#             # Contrainte 4: Non-simultanéité
#             if self._check_conflit_simultaneite(ens.id, planif):
#                 continue

#             # Récupérer les infos de volume
#             volume_info = self.get_volume_restant_enseignant(ens.id, annee_univ)

#             disponibles.append(EnseignantDisponible(
#                 enseignant_id=ens.id,
#                 nom=ens.nom,
#                 prenom=ens.prenom,
#                 grade=ens.grade,
#                 departement={
#                     "id": ens.departement_id,
#                     "nom": ens.departement.nom if ens.departement else "Unknown",
#                     "code": ens.departement.code if ens.departement else "UNK",
#                 },
#                 volume_horaire=volume_info["volume_horaire"],
#                 volume_consomme=volume_info["volume_consomme"],
#                 volume_restant=volume_info["volume_restant"],
#                 nb_surveillances=volume_info["nb_surveillances"],
#             ))

#         # Trier par volume_restant DESC
#         disponibles.sort(key=lambda x: x.volume_restant, reverse=True)
#         return disponibles


"""Business logic for surveillance module."""

from typing import Optional

from sqlalchemy.orm import Session as SQLSession

from app.algorithms.surv_auto import AutomaticAffectationAlgorithm
from app.crud.crud_surv import (
    create_surveillance,
    create_surveillances_batch,
    delete_surveillance,
    delete_surveillance_by_id,
    get_surveillance,
    get_surveillances_for_enseignant,
    get_surveillances_for_planification,
    list_surveillances,
    replace_surveillance,
    update_surveillance,
    get_enseignant_charge_for_year,
    count_surveillances_for_enseignant,
)
from app.models.surveillance import Surveillance
from app.models.planification_examen import PlanificationExamen
from app.models.enseignant import Enseignant, ChargeHoraire
from app.models.disponibilite import DisponibiliteEnseignant
from app.models.salle_session import Session, Creneau  # ✅ Correction: Ajout de Creneau
from app.schemas.surveillance_schema import (
    SurveillanceCreate,
    SurveillanceUpdate,
    ManualAssignmentRequest,
    ManualAssignmentBatchRequest,
    EnseignantDisponible,
)


class SurvService:
    """Business logic layer for surveillance module."""

    def __init__(self, db: SQLSession):
        self.db = db
        self.algorithm = AutomaticAffectationAlgorithm(db)

    # ========================================================================
    # CONSULTATION & LISTING
    # ========================================================================

    def get_all_surveillances(
        self,
        *,
        planification_id: Optional[int] = None,
        enseignant_id: Optional[int] = None,
        session_id: Optional[int] = None,
        est_externe: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Surveillance]:
        """Get all surveillances with optional filters."""
        return list_surveillances(
            self.db,
            planification_id=planification_id,
            enseignant_id=enseignant_id,
            session_id=session_id,
            est_externe=est_externe,
            skip=skip,
            limit=limit,
        )

    def get_surveillance_by_id(self, surveillance_id: int) -> Optional[Surveillance]:
        """Get a surveillance by ID."""
        return get_surveillance(self.db, surveillance_id)

    def get_surveillances_for_planification(
        self, planification_id: int
    ) -> list[Surveillance]:
        """Get all surveillances for a planification."""
        return get_surveillances_for_planification(self.db, planification_id)

    def get_surveillances_for_enseignant(
        self,
        enseignant_id: int,
        annee_universitaire: Optional[str] = None,
    ) -> list[Surveillance]:
        """Get all surveillances for an enseignant."""
        return get_surveillances_for_enseignant(
            self.db,
            enseignant_id,
            annee_universitaire,
        )

    # ========================================================================
    # CREATION & MODIFICATION
    # ========================================================================

    def create_surveillance(self, payload: SurveillanceCreate) -> Surveillance:
        """Create a new surveillance."""
        return create_surveillance(self.db, payload)

    def update_surveillance(
        self,
        surveillance_id: int,
        payload: SurveillanceUpdate,
    ) -> Optional[Surveillance]:
        """Update a surveillance."""
        surveillance = get_surveillance(self.db, surveillance_id)
        if not surveillance:
            return None
        return update_surveillance(self.db, surveillance, payload)

    def delete_surveillance(self, surveillance_id: int) -> bool:
        """Delete a surveillance (physical deletion)."""
        return delete_surveillance_by_id(self.db, surveillance_id)

    def replace_surveillance(
        self,
        surveillance_id: int,
        new_enseignant_id: int,
        motif: str,
    ) -> Optional[tuple]:
        """Replace an enseignant on a surveillance."""
        old = get_surveillance(self.db, surveillance_id)
        if not old:
            return None
        return replace_surveillance(self.db, old, new_enseignant_id, motif)

    # ========================================================================
    # AUTOMATIC AFFECTATION
    # ========================================================================

    def affecter_session_automatique(self, session_id: int) -> tuple:
        """
        Lancer l'affectation automatique pour toutes les planifications VALIDEE
        d'une session.

        Returns:
            - results: List of PlanificationAffectationResult
            - message: Status message
        """
        return self.algorithm.affecter_session(session_id)

    # ========================================================================
    # MANUAL AFFECTATION
    # ========================================================================

    def affecter_planification_manuellement(
        self,
        request: ManualAssignmentRequest,
    ) -> dict:
        """
        Handle manual affectation for a single conflicted planification.

        Validates constraints 1 and 4 only.
        """
        # Récupérer la planification
        planif = self.db.query(PlanificationExamen).filter(
            PlanificationExamen.id == request.planification_id,
            PlanificationExamen.session_id == request.session_id,
        ).first()

        if not planif:
            raise ValueError(f"Planification {request.planification_id} non trouvée dans la session")

        # Valider les enseignants et créer les surveillances
        surveillances_creees = []
        erreurs = []

        for ens_id in request.enseignant_ids:
            # Vérifier contrainte 1 (disponibilité)
            if not self._check_disponibilite_temporelle(ens_id, planif):
                erreurs.append({
                    "enseignant_id": ens_id,
                    "raison": "INDISPONIBLE",
                })
                continue

            # Vérifier contrainte 4 (non-simultanéité)
            if self._check_conflit_simultaneite(ens_id, planif):
                erreurs.append({
                    "enseignant_id": ens_id,
                    "raison": "DEJA_AFFECTE",
                })
                continue

            # Déterminer si externe
            ens = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
            est_externe = ens.departement_id != planif.departement_id

            motif = request.motifs_externes.get(ens_id) if est_externe else None

            # ✅ Vérification: motif_externe obligatoire si externe
            if est_externe and not motif:
                raise ValueError(f"Enseignant externe {ens_id} nécessite un motif_externe")

            payload = SurveillanceCreate(
                planification_id=request.planification_id,
                enseignant_id=ens_id,
                charge=float(planif.duree / 60),
                mode_affectation="MANUELLE",
                est_externe=est_externe,
                motif_externe=motif,
            )

            surv = create_surveillance(self.db, payload)
            surveillances_creees.append(surv)

        if erreurs:
            # Tout ou rien: si une erreur, on delete tout ce qui a été créé
            for surv in surveillances_creees:
                delete_surveillance(self.db, surv)
            raise ValueError(f"Validation échouée: {erreurs}")

        return {
            "planification_id": request.planification_id,
            "statut": "CONFLIT_RESOLU",
            "surveillants_inseres": len(surveillances_creees),
        }

    def affecter_session_manuellement(
        self,
        request: ManualAssignmentBatchRequest,
    ) -> dict:
        """
        Handle full manual affectation for an entire session.

        Validates constraints 1 and 4 only.
        One transaction for all planifications.
        """
        # Récupérer la session
        session = self.db.query(Session).filter(
            Session.id == request.session_id,
        ).first()

        if not session:
            raise ValueError(f"Session {request.session_id} non trouvée")

        # Valider toutes les affectations d'abord
        all_valid_payloads = []
        erreurs_globales = []
        planifications_non_affectees = []

        for planif_id, ens_ids in request.affectations.items():
            # Récupérer la planification
            planif = self.db.query(PlanificationExamen).filter(
                PlanificationExamen.id == planif_id,
                PlanificationExamen.session_id == request.session_id,
            ).first()

            if not planif:
                planifications_non_affectees.append(planif_id)
                erreurs_globales.append({
                    "planification_id": planif_id,
                    "erreur": "Non trouvée",
                })
                continue

            # Vérifier si la planification a assez de surveillants
            if len(ens_ids) < planif.nb_surveillants_requis:
                planifications_non_affectees.append(planif_id)

            for ens_id in ens_ids:
                # Vérifier contrainte 1
                if not self._check_disponibilite_temporelle(ens_id, planif):
                    erreurs_globales.append({
                        "planification_id": planif_id,
                        "enseignant_id": ens_id,
                        "raison": "INDISPONIBLE",
                    })
                    continue

                # Vérifier contrainte 4
                if self._check_conflit_simultaneite(ens_id, planif):
                    erreurs_globales.append({
                        "planification_id": planif_id,
                        "enseignant_id": ens_id,
                        "raison": "DEJA_AFFECTE",
                    })
                    continue

                # Déterminer si externe
                ens = self.db.query(Enseignant).filter(Enseignant.id == ens_id).first()
                est_externe = ens.departement_id != planif.departement_id
                motif = request.motifs_externes.get(ens_id) if est_externe else None

                # ✅ Vérification: motif_externe obligatoire si externe
                if est_externe and not motif:
                    raise ValueError(f"Enseignant externe {ens_id} nécessite un motif_externe")

                payload = SurveillanceCreate(
                    planification_id=planif_id,
                    enseignant_id=ens_id,
                    charge=float(planif.duree / 60),
                    mode_affectation="MANUELLE",
                    est_externe=est_externe,
                    motif_externe=motif,
                )

                all_valid_payloads.append(payload)

        # ✅ Avertissement si des planifications sont incomplètes
        if planifications_non_affectees:
            return {
                "session_id": request.session_id,
                "statut": "AVERTISSEMENT",
                "message": "Certaines planifications n'ont pas assez de surveillants",
                "planifications_non_affectees": planifications_non_affectees,
                "avertissement": "Voulez-vous continuer ?",
            }

        if erreurs_globales:
            raise ValueError(f"Validation échouée: {erreurs_globales}")

        # Transaction unique pour toutes les surveillances
        surveillances = create_surveillances_batch(self.db, all_valid_payloads)

        return {
            "session_id": request.session_id,
            "statut": "SUCCES",
            "total_surveillances_inserees": len(surveillances),
        }

    # ========================================================================
    # HELPER METHODS FOR CONSTRAINT CHECKING
    # ========================================================================

    def _check_disponibilite_temporelle(
        self,
        enseignant_id: int,
        planif: PlanificationExamen,  # ✅ Correction: PlanificationExamen au lieu de Planification
    ) -> bool:
        """Vérifier disponibilité temporelle (Contrainte 1)."""
        creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        if not creneau:
            return False

        # Vérifier indisponibilités
        indisponibilites = self.db.query(DisponibiliteEnseignant).filter(
            DisponibiliteEnseignant.enseignant_id == enseignant_id,
            DisponibiliteEnseignant.date == creneau.date,
            DisponibiliteEnseignant.type_dispo.in_(["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]),
        ).all()

        for indispo in indisponibilites:
            if indispo.heure_debut < creneau.heure_fin and indispo.heure_fin > creneau.heure_debut:
                return False

        return True

    def _check_conflit_simultaneite(
        self,
        enseignant_id: int,
        planif: PlanificationExamen,  # ✅ Correction: PlanificationExamen au lieu de Planification
    ) -> bool:
        """Vérifier non-simultanéité (Contrainte 4)."""
        creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        if not creneau:
            return False

        # Chercher conflits
        conflits = self.db.query(Surveillance).join(PlanificationExamen).join(Creneau).filter(
            Surveillance.enseignant_id == enseignant_id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
            Creneau.date == creneau.date,
            Creneau.heure_debut == creneau.heure_debut,
        ).all()

        return len(conflits) > 0

    # ========================================================================
    # ANALYTICS & REPORTS
    # ========================================================================

    def get_volume_restant_enseignant(
        self,
        enseignant_id: int,
        annee_universitaire: str,
    ) -> dict:
        """Get volume information for an enseignant."""
        charge_horaire = self.db.query(ChargeHoraire).filter(
            ChargeHoraire.enseignant_id == enseignant_id,
            ChargeHoraire.annee_univ == annee_universitaire,
        ).first()

        volume_horaire = charge_horaire.volume_horaire if charge_horaire else 0.0
        volume_consomme = get_enseignant_charge_for_year(
            self.db,
            enseignant_id,
            annee_universitaire,
        )
        nb_surveillances = count_surveillances_for_enseignant(
            self.db,
            enseignant_id,
            annee_universitaire,
        )

        return {
            "enseignant_id": enseignant_id,
            "volume_horaire": volume_horaire,
            "volume_consomme": volume_consomme,
            "volume_restant": volume_horaire - volume_consomme,
            "nb_surveillances": nb_surveillances,
        }

    def get_enseignants_disponibles_pour_planification(
        self,
        planif_id: int,
    ) -> list[EnseignantDisponible]:
        """
        Get all available enseignants for a planification (for conflict resolution).

        Applies only constraints 1 and 4 (no department filter).
        Returns all departments.
        """
        planif = self.db.query(PlanificationExamen).filter(PlanificationExamen.id == planif_id).first()
        if not planif:
            return []

        session = self.db.query(Session).filter(
            Session.id == planif.session_id,
        ).first()
        annee_univ = session.annee_universitaire if session else None

        # Récupérer tous les enseignants
        enseignants = self.db.query(Enseignant).all()
        disponibles = []

        for ens in enseignants:
            # Contrainte 1: Disponibilité
            if not self._check_disponibilite_temporelle(ens.id, planif):
                continue

            # Contrainte 4: Non-simultanéité
            if self._check_conflit_simultaneite(ens.id, planif):
                continue

            # Récupérer les infos de volume
            volume_info = self.get_volume_restant_enseignant(ens.id, annee_univ)

            disponibles.append(EnseignantDisponible(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                departement={
                    "id": ens.departement_id,
                    "nom": ens.departement.nom if ens.departement else "Unknown",
                    "code": ens.departement.code if ens.departement else "UNK",
                },
                volume_horaire=volume_info["volume_horaire"],
                volume_consomme=volume_info["volume_consomme"],
                volume_restant=volume_info["volume_restant"],
                nb_surveillances=volume_info["nb_surveillances"],
            ))

        # Trier par volume_restant DESC
        disponibles.sort(key=lambda x: x.volume_restant, reverse=True)
        return disponibles