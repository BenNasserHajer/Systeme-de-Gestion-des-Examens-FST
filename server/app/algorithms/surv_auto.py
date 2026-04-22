# """Powerful automatic surveillance affectation algorithm."""

# from datetime import datetime
# from dataclasses import dataclass
# from enum import Enum
# from typing import Optional

# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from app.models.surveillance import Surveillance
# from app.models.enseignant import Enseignant, ChargeHoraire, Enseignement
# from app.models.planification_examen import PlanificationExamen
# from app.models.disponibilite import DisponibiliteEnseignant
# from app.models.departement_niveau_section import Departement
# from app.models.salle_session import Session as SessionModel, Creneau
# from app.crud.crud_surv import create_surveillance
# from app.schemas.surveillance_schema import (
#     SurveillanceCreate,
#     ModeAffectation,
#     StatutSurveillance,
#     ReasonExclusion,
# )


# class ConstraintPriority(Enum):
#     """Priority levels for constraints."""
#     HARD = "HARD"  # Must always be respected
#     SOFT = "SOFT"  # Can be relaxed in last resort
#     INFO = "INFO"  # For information only


# @dataclass
# class EnseignantCandidat:
#     """Candidate enseignant for surveillance."""
#     enseignant_id: int
#     nom: str
#     prenom: str
#     grade: Optional[str]
#     departement_id: int
#     departement_nom: str
#     volume_horaire: float
#     volume_restant: float
#     volume_consomme: float
#     nb_surveillances: int
#     a_conflit_matiere: bool = False
#     est_dans_departement: bool = True
    
#     def __lt__(self, other):
#         """Sort by volume_restant DESC, then by nb_surveillances ASC."""
#         if self.volume_restant != other.volume_restant:
#             return self.volume_restant > other.volume_restant
#         return self.nb_surveillances < other.nb_surveillances


# @dataclass
# class ConstraintViolation:
#     """Record a constraint violation."""
#     enseignant_id: int
#     nom: str
#     prenom: str
#     raison: ReasonExclusion
#     details: Optional[str] = None


# @dataclass
# class PlanificationAffectationResult:
#     """Result of affectation attempt for a single planification."""
#     planification_id: int
#     statut: str  # "AFFECTEE" or "CONFLIT"
#     surveillants_affectes: list[Surveillance] = None
#     surveillants_requis: int = 0
#     manquants: int = 0
#     violations: list[ConstraintViolation] = None

#     def __post_init__(self):
#         if self.surveillants_affectes is None:
#             self.surveillants_affectes = []
#         if self.violations is None:
#             self.violations = []


# class AutomaticAffectationAlgorithm:
#     """Puissant algorithme d'affectation automatique des surveillances."""

#     TOLERANCE_PERCENT = 0.0005  # ±0.05% tolerance

#     def __init__(self, db: Session):
#         self.db = db

#     def affecter_session(
#         self,
#         session_id: int,
#     ) -> tuple[list[PlanificationAffectationResult], str]:
#         """
#         Main entry point: Affecter toutes les planifications VALIDEE d'une session.

#         Returns:
#             - List of results for each planification
#             - Global status message
#         """
#         # Récupérer la session
#         session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
#         if not session:
#             return [], f"Session {session_id} non trouvée"

#         annee_univ = session.annee_universitaire

#         # Récupérer toutes les planifications VALIDEE
#         planifications = self.db.query(Planification).filter(
#             Planification.session_id == session_id,
#             Planification.statut == "VALIDEE",
#         ).order_by(
#             Planification.date_examen.asc(),
#             Planification.heure_debut.asc(),
#         ).all()

#         if not planifications:
#             return [], f"Aucune planification VALIDEE trouvée dans la session {session_id}"

#         results = []
#         total_affectees = 0
#         total_conflits = 0

#         # BOUCLE: Traiter chaque planification
#         for planif in planifications:
#             result = self._affecter_planification(
#                 planif,
#                 annee_univ,
#             )
#             results.append(result)

#             if result.statut == "AFFECTEE":
#                 total_affectees += 1
#             else:
#                 total_conflits += 1

#         status_msg = (
#             f"Traitement terminé: {total_affectees} planifications affectées, "
#             f"{total_conflits} planifications en conflit"
#         )

#         return results, status_msg

#     def _affecter_planification(
#         self,
#         planif: PlanificationExamen,
#         annee_univ: str,
#     ) -> PlanificationAffectationResult:
#         """
#         Affecter une seule planification selon les 5 contraintes.

#         Étapes:
#         1. Calcul dynamique du volume restant
#         2. Filtrage selon les 5 contraintes
#         3. Tri des candidats éligibles
#         4. Insertion des surveillances (ou enregistrement du conflit)
#         """
#         result = PlanificationAffectationResult(
#             planification_id=planif.id,
#             statut="AFFECTEE",
#             surveillants_requis=planif.nb_surveillants_requis,
#         )

#         # Récupérer tous les enseignants du département
#         candidats_potentiels = self._get_enseignants_departement(planif.departement_id)

#         # Étape 1: Calculer le volume restant pour chaque candidat
#         for candidat in candidats_potentiels:
#             charge_consommee = self._get_charge_consumed(candidat.enseignant_id, annee_univ)
#             candidat.volume_consomme = charge_consommee
#             candidat.volume_restant = candidat.volume_horaire - charge_consommee

#         # Étape 2: Filtrer selon les contraintes
#         candidats_eligibles = []
#         violations = []

#         for candidat in candidats_potentiels:
#             # Contrainte 1: Disponibilité temporelle (HARD - toujours appliquée)
#             if not self._check_disponibilite_temporelle(candidat.enseignant_id, planif):
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.INDISPONIBLE,
#                 ))
#                 continue

#             # Contrainte 4: Non-simultanéité (HARD - toujours appliquée)
#             if self._check_conflit_simultaneite(candidat.enseignant_id, planif):
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.DEJA_AFFECTE,
#                 ))
#                 continue

#             # Contrainte 3: Volume horaire restant (HARD - respect tolérance ±0.05%)
#             tolerance = candidat.volume_horaire * self.TOLERANCE_PERCENT
#             if candidat.volume_restant < -tolerance:
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.VOLUME_EPUISE,
#                     details=f"Restant: {candidat.volume_restant:.2f}h (limite: {-tolerance:.2f}h)",
#                 ))
#                 continue

#             # Contrainte 2: Conflit de matière (SOFT - peut être relaxée)
#             a_conflit = self._check_conflit_matiere(candidat.enseignant_id, planif)
#             candidat.a_conflit_matiere = a_conflit

#             candidats_eligibles.append(candidat)

#         # Trier les candidats éligibles
#         candidats_eligibles.sort()

#         # Étape 3: Sélectionner les surveillants
#         surveillants_selectionnes = []
#         candidats_sans_conflit = [c for c in candidats_eligibles if not c.a_conflit_matiere]

#         # Priorité 1: Sans conflit de matière
#         for candidat in candidats_sans_conflit[:planif.nb_surveillants_requis]:
#             surv = self._creer_surveillance(planif, candidat)
#             surveillants_selectionnes.append(surv)

#         # Priorité 2: Avec conflit de matière (en dernier recours)
#         if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
#             candidats_avec_conflit = [c for c in candidats_eligibles if c.a_conflit_matiere]
#             for candidat in candidats_avec_conflit:
#                 if len(surveillants_selectionnes) >= planif.nb_surveillants_requis:
#                     break
#                 surv = self._creer_surveillance(planif, candidat)
#                 surveillants_selectionnes.append(surv)

#         # Étape 4: Vérifier si complet
#         if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
#             result.statut = "CONFLIT"
#             result.surveillants_affectes = surveillants_selectionnes
#             result.manquants = planif.nb_surveillants_requis - len(surveillants_selectionnes)
#             result.violations = violations
#         else:
#             result.surveillants_affectes = surveillants_selectionnes

#         return result

#     def _get_enseignants_departement(self, departement_id: int) -> list[EnseignantCandidat]:
#         """Récupérer tous les enseignants d'un département avec leurs infos."""
#         enseignants = self.db.query(
#             Enseignant.id,
#             Enseignant.nom,
#             Enseignant.prenom,
#             Enseignant.grade,
#             Enseignant.departement_id,
#         ).filter(Enseignant.departement_id == departement_id).all()

#         candidats = []
#         for ens in enseignants:
#             # Récupérer le volume horaire (assume current year)
#             from datetime import datetime as dt
#             current_year = f"{dt.now().year}/{dt.now().year + 1}"
#             charge = self.db.query(ChargeHoraire).filter(
#                 ChargeHoraire.enseignant_id == ens.id,
#                 ChargeHoraire.annee_univ == current_year,
#             ).first()

#             volume_horaire = charge.volume_horaire if charge else 0.0
#             departement = self.db.query(Departement).filter(Departement.id == departement_id).first()

#             candidats.append(EnseignantCandidat(
#                 enseignant_id=ens.id,
#                 nom=ens.nom,
#                 prenom=ens.prenom,
#                 grade=ens.grade,
#                 departement_id=ens.departement_id,
#                 departement_nom=departement.nom if departement else "Unknown",
#                 volume_horaire=volume_horaire,
#                 volume_restant=volume_horaire,
#                 volume_consomme=0.0,
#                 nb_surveillances=0,
#             ))

#         return candidats

#     def _get_charge_consumed(
#         self,
#         enseignant_id: int,
#         annee_univ: str,
#     ) -> float:
#         """Calculer la charge totale consommée par un enseignant en une année universitaire."""
#         result = self.db.query(func.coalesce(func.sum(Surveillance.charge), 0)).filter(
#             Surveillance.enseignant_id == enseignant_id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#         ).join(Planification).join(SessionModel).filter(
#             SessionModel.annee_universitaire == annee_univ,
#         ).scalar()

#         return float(result)

#     def _check_disponibilite_temporelle(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier la disponibilité temporelle d'un enseignant (Contrainte 1 - HARD)."""
#         from app.models.creneau import Creneau

#         # Récupérer le créneau de la planification
#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # Vérifier s'il y a une indisponibilité qui chevauche
#         indisponibilites = self.db.query(DisponibiliteEnseignant).filter(
#             DisponibiliteEnseignant.enseignant_id == enseignant_id,
#             DisponibiliteEnseignant.date == creneau.date,
#             DisponibiliteEnseignant.type_dispo.in_(["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]),
#         ).all()

#         for indispo in indisponibilites:
#             # Vérifier le chevauchement horaire
#             if (indispo.heure_debut < creneau.heure_fin and
#                 indispo.heure_fin > creneau.heure_debut):
#                 return False

#         return True

#     def _check_conflit_simultaneite(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier la non-simultanéité (Contrainte 4 - HARD)."""
#         from app.models.creneau import Creneau

#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # Chercher une autre surveillance du même enseignant au même créneau
#         conflits = self.db.query(Surveillance).join(Planification).join(Creneau).filter(
#             Surveillance.enseignant_id == enseignant_id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#             Creneau.date == creneau.date,
#             Creneau.heure_debut == creneau.heure_debut,
#         ).all()

#         return len(conflits) > 0

#     def _check_conflit_matiere(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier le conflit de matière (Contrainte 2 - SOFT)."""
#         from app.models.section_matiere import SectionMatiere

#         # Récupérer la section_matiere de la planification
#         section_matiere = self.db.query(SectionMatiere).filter(
#             SectionMatiere.id == planif.section_matiere_id,
#         ).first()

#         if not section_matiere:
#             return False

#         # Vérifier si l'enseignant enseigne cette matière (COURS ou TD)
#         enseignement = self.db.query(Enseignement).filter(
#             Enseignement.enseignant_id == enseignant_id,
#             Enseignement.matiere_id == section_matiere.matiere_id,
#             Enseignement.type_enseignement.in_(["COURS", "TD"]),
#         ).first()

#         return enseignement is not None

#     def _creer_surveillance(
#         self,
#         planif: Planification,
#         candidat: EnseignantCandidat,
#     ) -> Surveillance:
#         """Créer une surveillance dans la base de données."""
#         payload = SurveillanceCreate(
#             planification_id=planif.id,
#             enseignant_id=candidat.enseignant_id,
#             charge=float(planif.duree / 60),  # Convertir minutes en heures
#             mode_affectation=ModeAffectation.AUTOMATIQUE,
#             statut_surveillance=StatutSurveillance.AFFECTE,
#             est_externe=False,
#             motif_externe=None,
#         )

#         return create_surveillance(self.db, payload)

# """Powerful automatic surveillance affectation algorithm."""

# from datetime import datetime
# from dataclasses import dataclass
# from enum import Enum
# from typing import Optional

# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from app.models.surveillance import Surveillance
# from app.models.enseignant import Enseignant, ChargeHoraire, Enseignement
# from app.models.planification_examen import PlanificationExamen  # ✅ CORRIGÉ
# from app.models.disponibilite import DisponibiliteEnseignant
# from app.models.departement_niveau_section import Departement
# from app.models.salle_session import Session as SessionModel, Creneau
# from app.crud.crud_surv import create_surveillance
# from app.schemas.surveillance_schema import (
#     SurveillanceCreate,
#     ModeAffectation,
#     StatutSurveillance,
#     ReasonExclusion,
# )


# class ConstraintPriority(Enum):
#     """Priority levels for constraints."""
#     HARD = "HARD"  # Must always be respected
#     SOFT = "SOFT"  # Can be relaxed in last resort
#     INFO = "INFO"  # For information only


# @dataclass
# class EnseignantCandidat:
#     """Candidate enseignant for surveillance."""
#     enseignant_id: int
#     nom: str
#     prenom: str
#     grade: Optional[str]
#     departement_id: int
#     departement_nom: str
#     volume_horaire: float
#     volume_restant: float
#     volume_consomme: float
#     nb_surveillances: int
#     a_conflit_matiere: bool = False
#     est_dans_departement: bool = True
    
#     def __lt__(self, other):
#         """Sort by volume_restant DESC, then by nb_surveillances ASC."""
#         if self.volume_restant != other.volume_restant:
#             return self.volume_restant > other.volume_restant
#         return self.nb_surveillances < other.nb_surveillances


# @dataclass
# class ConstraintViolation:
#     """Record a constraint violation."""
#     enseignant_id: int
#     nom: str
#     prenom: str
#     raison: ReasonExclusion
#     details: Optional[str] = None


# @dataclass
# class PlanificationAffectationResult:
#     """Result of affectation attempt for a single planification."""
#     planification_id: int
#     statut: str  # "AFFECTEE" or "CONFLIT"
#     surveillants_affectes: list[Surveillance] = None
#     surveillants_requis: int = 0
#     manquants: int = 0
#     violations: list[ConstraintViolation] = None

#     def __post_init__(self):
#         if self.surveillants_affectes is None:
#             self.surveillants_affectes = []
#         if self.violations is None:
#             self.violations = []


# class AutomaticAffectationAlgorithm:
#     """Puissant algorithme d'affectation automatique des surveillances."""

#     TOLERANCE_PERCENT = 0.0005  # ±0.05% tolerance

#     def __init__(self, db: Session):
#         self.db = db

#     def affecter_session(
#         self,
#         session_id: int,
#     ) -> tuple[list[PlanificationAffectationResult], str]:
#         """
#         Main entry point: Affecter toutes les planifications VALIDEE d'une session.

#         Returns:
#             - List of results for each planification
#             - Global status message
#         """
#         # Récupérer la session
#         session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
#         if not session:
#             return [], f"Session {session_id} non trouvée"

#         annee_univ = session.annee_universitaire

#         # ✅ CORRIGÉ: PlanificationExamen au lieu de Planification
#         planifications = self.db.query(PlanificationExamen).filter(
#             PlanificationExamen.session_id == session_id,
#             PlanificationExamen.statut == "VALIDEE",  # ✅ CORRIGÉ: statut_planif
#         ).order_by(
#             PlanificationExamen.date_examen.asc(),
#             PlanificationExamen.heure_debut.asc(),
#         ).all()

#         if not planifications:
#             return [], f"Aucune planification VALIDEE trouvée dans la session {session_id}"

#         results = []
#         total_affectees = 0
#         total_conflits = 0

#         # BOUCLE: Traiter chaque planification
#         for planif in planifications:
#             result = self._affecter_planification(
#                 planif,
#                 annee_univ,
#             )
#             results.append(result)

#             if result.statut == "AFFECTEE":
#                 total_affectees += 1
#             else:
#                 total_conflits += 1

#         status_msg = (
#             f"Traitement terminé: {total_affectees} planifications affectées, "
#             f"{total_conflits} planifications en conflit"
#         )

#         return results, status_msg

#     def _affecter_planification(
#         self,
#         planif: PlanificationExamen,
#         annee_univ: str,
#     ) -> PlanificationAffectationResult:
#         """
#         Affecter une seule planification selon les 5 contraintes.

#         Étapes:
#         1. Calcul dynamique du volume restant
#         2. Filtrage selon les 5 contraintes
#         3. Tri des candidats éligibles
#         4. Insertion des surveillances (ou enregistrement du conflit)
#         """
#         result = PlanificationAffectationResult(
#             planification_id=planif.id,
#             statut="AFFECTEE",
#             surveillants_requis=planif.nb_surveillants_requis,
#         )

#         # Récupérer tous les enseignants du département
#         candidats_potentiels = self._get_enseignants_departement(planif.departement_id)

#         # Étape 1: Calculer le volume restant pour chaque candidat
#         for candidat in candidats_potentiels:
#             charge_consommee = self._get_charge_consumed(candidat.enseignant_id, annee_univ)
#             candidat.volume_consomme = charge_consommee
#             candidat.volume_restant = candidat.volume_horaire - charge_consommee

#         # Étape 2: Filtrer selon les contraintes
#         candidats_eligibles = []
#         violations = []

#         for candidat in candidats_potentiels:
#             # Contrainte 1: Disponibilité temporelle (HARD - toujours appliquée)
#             if not self._check_disponibilite_temporelle(candidat.enseignant_id, planif):
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.INDISPONIBLE,
#                 ))
#                 continue

#             # Contrainte 4: Non-simultanéité (HARD - toujours appliquée)
#             if self._check_conflit_simultaneite(candidat.enseignant_id, planif):
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.DEJA_AFFECTE,
#                 ))
#                 continue

#             # Contrainte 3: Volume horaire restant (HARD - respect tolérance ±0.05%)
#             tolerance = candidat.volume_horaire * self.TOLERANCE_PERCENT
#             if candidat.volume_restant < -tolerance:
#                 violations.append(ConstraintViolation(
#                     enseignant_id=candidat.enseignant_id,
#                     nom=candidat.nom,
#                     prenom=candidat.prenom,
#                     raison=ReasonExclusion.VOLUME_EPUISE,
#                     details=f"Restant: {candidat.volume_restant:.2f}h (limite: {-tolerance:.2f}h)",
#                 ))
#                 continue

#             # Contrainte 2: Conflit de matière (SOFT - peut être relaxée)
#             a_conflit = self._check_conflit_matiere(candidat.enseignant_id, planif)
#             candidat.a_conflit_matiere = a_conflit

#             candidats_eligibles.append(candidat)

#         # Trier les candidats éligibles
#         candidats_eligibles.sort()

#         # Étape 3: Sélectionner les surveillants
#         surveillants_selectionnes = []
#         candidats_sans_conflit = [c for c in candidats_eligibles if not c.a_conflit_matiere]

#         # Priorité 1: Sans conflit de matière
#         for candidat in candidats_sans_conflit[:planif.nb_surveillants_requis]:
#             surv = self._creer_surveillance(planif, candidat)
#             surveillants_selectionnes.append(surv)

#         # Priorité 2: Avec conflit de matière (en dernier recours)
#         if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
#             candidats_avec_conflit = [c for c in candidats_eligibles if c.a_conflit_matiere]
#             for candidat in candidats_avec_conflit:
#                 if len(surveillants_selectionnes) >= planif.nb_surveillants_requis:
#                     break
#                 surv = self._creer_surveillance(planif, candidat)
#                 surveillants_selectionnes.append(surv)

#         # ✅ NOUVEAU: Vérifier si on a utilisé des enseignants avec conflit matière
#         a_utilise_conflit_matiere = any(
#             c.enseignant_id in [cand.enseignant_id for cand in candidats_avec_conflit]
#             for c in surveillants_selectionnes
#         ) if 'candidats_avec_conflit' in dir() else False

#         # Étape 4: Vérifier si complet
#         if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
#             result.statut = "CONFLIT"
#             result.surveillants_affectes = surveillants_selectionnes
#             result.manquants = planif.nb_surveillants_requis - len(surveillants_selectionnes)
#             result.violations = violations
#         else:
#             result.surveillants_affectes = surveillants_selectionnes
#             # ✅ NOUVEAU: Ajouter un avertissement si contrainte matière a été levée
#             if a_utilise_conflit_matiere:
#                 result.violations.append(ConstraintViolation(
#                     enseignant_id=0,
#                     nom="AVERTISSEMENT",
#                     prenom="",
#                     raison=ReasonExclusion.CONFLIT_MATIERE,
#                     details="Contrainte matière levée en dernier recours (enseignant surveille sa propre matière)",
#                 ))

#         return result

#     def _get_enseignants_departement(self, departement_id: int) -> list[EnseignantCandidat]:
#         """Récupérer tous les enseignants d'un département avec leurs infos."""
#         enseignants = self.db.query(
#             Enseignant.id,
#             Enseignant.nom,
#             Enseignant.prenom,
#             Enseignant.grade,
#             Enseignant.departement_id,
#         ).filter(Enseignant.departement_id == departement_id).all()

#         candidats = []
#         for ens in enseignants:
#             # Récupérer le volume horaire (assume current year)
#             from datetime import datetime as dt
#             current_year = f"{dt.now().year}/{dt.now().year + 1}"
#             charge = self.db.query(ChargeHoraire).filter(
#                 ChargeHoraire.enseignant_id == ens.id,
#                 ChargeHoraire.annee_univ == current_year,
#             ).first()

#             volume_horaire = charge.volume_horaire if charge else 0.0
#             departement = self.db.query(Departement).filter(Departement.id == departement_id).first()

#             candidats.append(EnseignantCandidat(
#                 enseignant_id=ens.id,
#                 nom=ens.nom,
#                 prenom=ens.prenom,
#                 grade=ens.grade,
#                 departement_id=ens.departement_id,
#                 departement_nom=departement.nom if departement else "Unknown",
#                 volume_horaire=volume_horaire,
#                 volume_restant=volume_horaire,
#                 volume_consomme=0.0,
#                 nb_surveillances=0,
#             ))

#         return candidats

#     def _get_charge_consumed(
#         self,
#         enseignant_id: int,
#         annee_univ: str,
#     ) -> float:
#         """Calculer la charge totale consommée par un enseignant en une année universitaire."""
#         # ✅ CORRIGÉ: PlanificationExamen au lieu de Planification
#         result = self.db.query(func.coalesce(func.sum(Surveillance.charge), 0)).filter(
#             Surveillance.enseignant_id == enseignant_id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#         ).join(PlanificationExamen).join(SessionModel).filter(
#             SessionModel.annee_universitaire == annee_univ,
#         ).scalar()

#         return float(result)

#     def _check_disponibilite_temporelle(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier la disponibilité temporelle d'un enseignant (Contrainte 1 - HARD)."""
#         # Récupérer le créneau de la planification
#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # Vérifier s'il y a une indisponibilité qui chevauche
#         indisponibilites = self.db.query(DisponibiliteEnseignant).filter(
#             DisponibiliteEnseignant.enseignant_id == enseignant_id,
#             DisponibiliteEnseignant.date == creneau.date,
#             DisponibiliteEnseignant.type_dispo.in_(["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]),
#         ).all()

#         for indispo in indisponibilites:
#             # Vérifier le chevauchement horaire
#             if (indispo.heure_debut < creneau.heure_fin and
#                 indispo.heure_fin > creneau.heure_debut):
#                 return False

#         return True

#     def _check_conflit_simultaneite(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier la non-simultanéité (Contrainte 4 - HARD)."""
#         creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
#         if not creneau:
#             return False

#         # ✅ CORRIGÉ: PlanificationExamen au lieu de Planification
#         conflits = self.db.query(Surveillance).join(PlanificationExamen).join(Creneau).filter(
#             Surveillance.enseignant_id == enseignant_id,
#             Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
#             Creneau.date == creneau.date,
#             Creneau.heure_debut == creneau.heure_debut,
#         ).all()

#         return len(conflits) > 0

#     def _check_conflit_matiere(
#         self,
#         enseignant_id: int,
#         planif: PlanificationExamen,
#     ) -> bool:
#         """Vérifier le conflit de matière (Contrainte 2 - SOFT)."""
#         from app.models.section_matiere import SectionMatiere

#         # Récupérer la section_matiere de la planification
#         section_matiere = self.db.query(SectionMatiere).filter(
#             SectionMatiere.id == planif.section_matiere_id,
#         ).first()

#         if not section_matiere:
#             return False

#         # Vérifier si l'enseignant enseigne cette matière (COURS ou TD)
#         enseignement = self.db.query(Enseignement).filter(
#             Enseignement.enseignant_id == enseignant_id,
#             Enseignement.matiere_id == section_matiere.matiere_id,
#             Enseignement.type_enseignement.in_(["COURS", "TD"]),
#         ).first()

#         return enseignement is not None

#     def _creer_surveillance(
#         self,
#         planif: PlanificationExamen,  # ✅ CORRIGÉ
#         candidat: EnseignantCandidat,
#     ) -> Surveillance:
#         """Créer une surveillance dans la base de données."""
#         # ✅ CORRIGÉ: ajout de .value pour les enums
#         payload = SurveillanceCreate(
#             planification_id=planif.id,
#             enseignant_id=candidat.enseignant_id,
#             charge=float(planif.duree / 60),  # Convertir minutes en heures
#             mode_affectation=ModeAffectation.AUTOMATIQUE.value,
#             statut_surveillance=StatutSurveillance.AFFECTE.value,
#             est_externe=False,
#             motif_externe=None,
#         )

#         return create_surveillance(self.db, payload)


"""Powerful automatic surveillance affectation algorithm."""

from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.surveillance import Surveillance
from app.models.enseignant import Enseignant, ChargeHoraire, Enseignement
from app.models.planification_examen import PlanificationExamen
from app.models.disponibilite import DisponibiliteEnseignant
from app.models.departement_niveau_section import Departement
from app.models.salle_session import Session as SessionModel, Creneau
from app.crud.crud_surv import create_surveillance
from app.schemas.surveillance_schema import (
    SurveillanceCreate,
    ModeAffectation,
    StatutSurveillance,
    ReasonExclusion,
)


class ConstraintPriority(Enum):
    """Priority levels for constraints."""
    HARD = "HARD"  # Must always be respected
    SOFT = "SOFT"  # Can be relaxed in last resort
    INFO = "INFO"  # For information only


@dataclass
class EnseignantCandidat:
    """Candidate enseignant for surveillance."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str]
    departement_id: int
    departement_nom: str
    volume_horaire: float
    volume_restant: float
    volume_consomme: float
    nb_surveillances: int
    a_conflit_matiere: bool = False
    est_dans_departement: bool = True
    
    def __lt__(self, other):
        """Sort by volume_restant DESC, then by nb_surveillances ASC."""
        if self.volume_restant != other.volume_restant:
            return self.volume_restant > other.volume_restant
        return self.nb_surveillances < other.nb_surveillances


@dataclass
class ConstraintViolation:
    """Record a constraint violation."""
    enseignant_id: int
    nom: str
    prenom: str
    raison: ReasonExclusion
    details: Optional[str] = None


@dataclass
class PlanificationAffectationResult:
    """Result of affectation attempt for a single planification."""
    planification_id: int
    statut: str  # "AFFECTEE" or "CONFLIT"
    surveillants_affectes: list[Surveillance] = None
    surveillants_requis: int = 0
    manquants: int = 0
    violations: list[ConstraintViolation] = None

    def __post_init__(self):
        if self.surveillants_affectes is None:
            self.surveillants_affectes = []
        if self.violations is None:
            self.violations = []


class AutomaticAffectationAlgorithm:
    """Puissant algorithme d'affectation automatique des surveillances."""

    TOLERANCE_PERCENT = 0.0005  # ±0.05% tolerance

    def __init__(self, db: Session):
        self.db = db

    def affecter_session(
        self,
        session_id: int,
    ) -> tuple[list[PlanificationAffectationResult], str]:
        """
        Main entry point: Affecter toutes les planifications VALIDEE d'une session.

        Returns:
            - List of results for each planification
            - Global status message
        """
        # Récupérer la session
        session = self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return [], f"Session {session_id} non trouvée"

        annee_univ = session.annee_universitaire

        # ✅ CORRIGÉ: Jointure avec Creneau + statut au lieu de statut_planif
        planifications = self.db.query(PlanificationExamen).join(
            Creneau, PlanificationExamen.creneau_id == Creneau.id
        ).filter(
            PlanificationExamen.session_id == session_id,
            PlanificationExamen.statut == "VALIDEE",
        ).order_by(
            Creneau.date.asc(),
            Creneau.heure_debut.asc(),
        ).all()

        if not planifications:
            return [], f"Aucune planification VALIDEE trouvée dans la session {session_id}"

        results = []
        total_affectees = 0
        total_conflits = 0

        # BOUCLE: Traiter chaque planification
        for planif in planifications:
            result = self._affecter_planification(
                planif,
                annee_univ,
            )
            results.append(result)

            if result.statut == "AFFECTEE":
                total_affectees += 1
            else:
                total_conflits += 1

        status_msg = (
            f"Traitement terminé: {total_affectees} planifications affectées, "
            f"{total_conflits} planifications en conflit"
        )

        return results, status_msg

    def _affecter_planification(
        self,
        planif: PlanificationExamen,
        annee_univ: str,
    ) -> PlanificationAffectationResult:
        """
        Affecter une seule planification selon les 5 contraintes.

        Étapes:
        1. Calcul dynamique du volume restant
        2. Filtrage selon les 5 contraintes
        3. Tri des candidats éligibles
        4. Insertion des surveillances (ou enregistrement du conflit)
        """
        result = PlanificationAffectationResult(
            planification_id=planif.id,
            statut="AFFECTEE",
            surveillants_requis=planif.nb_surveillants_requis,
        )

        # Récupérer tous les enseignants du département
        candidats_potentiels = self._get_enseignants_departement(planif.departement_id)

        # Étape 1: Calculer le volume restant pour chaque candidat
        for candidat in candidats_potentiels:
            charge_consommee = self._get_charge_consumed(candidat.enseignant_id, annee_univ)
            candidat.volume_consomme = charge_consommee
            candidat.volume_restant = candidat.volume_horaire - charge_consommee

        # Étape 2: Filtrer selon les contraintes
        candidats_eligibles = []
        violations = []

        for candidat in candidats_potentiels:
            # Contrainte 1: Disponibilité temporelle (HARD - toujours appliquée)
            if not self._check_disponibilite_temporelle(candidat.enseignant_id, planif):
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom,
                    prenom=candidat.prenom,
                    raison=ReasonExclusion.INDISPONIBLE,
                ))
                continue

            # Contrainte 4: Non-simultanéité (HARD - toujours appliquée)
            if self._check_conflit_simultaneite(candidat.enseignant_id, planif):
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom,
                    prenom=candidat.prenom,
                    raison=ReasonExclusion.DEJA_AFFECTE,
                ))
                continue

            # Contrainte 3: Volume horaire restant (HARD - respect tolérance ±0.05%)
            tolerance = candidat.volume_horaire * self.TOLERANCE_PERCENT
            if candidat.volume_restant < -tolerance:
                violations.append(ConstraintViolation(
                    enseignant_id=candidat.enseignant_id,
                    nom=candidat.nom,
                    prenom=candidat.prenom,
                    raison=ReasonExclusion.VOLUME_EPUISE,
                    details=f"Restant: {candidat.volume_restant:.2f}h (limite: {-tolerance:.2f}h)",
                ))
                continue

            # Contrainte 2: Conflit de matière (SOFT - peut être relaxée)
            a_conflit = self._check_conflit_matiere(candidat.enseignant_id, planif)
            candidat.a_conflit_matiere = a_conflit

            candidats_eligibles.append(candidat)

        # Trier les candidats éligibles
        candidats_eligibles.sort()

        # Étape 3: Sélectionner les surveillants
        surveillants_selectionnes = []
        candidats_sans_conflit = [c for c in candidats_eligibles if not c.a_conflit_matiere]

        # Priorité 1: Sans conflit de matière
        for candidat in candidats_sans_conflit[:planif.nb_surveillants_requis]:
            surv = self._creer_surveillance(planif, candidat)
            surveillants_selectionnes.append(surv)

        # Priorité 2: Avec conflit de matière (en dernier recours)
        if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
            candidats_avec_conflit = [c for c in candidats_eligibles if c.a_conflit_matiere]
            for candidat in candidats_avec_conflit:
                if len(surveillants_selectionnes) >= planif.nb_surveillants_requis:
                    break
                surv = self._creer_surveillance(planif, candidat)
                surveillants_selectionnes.append(surv)

        # ✅ NOUVEAU: Vérifier si on a utilisé des enseignants avec conflit matière
        a_utilise_conflit_matiere = any(
            c.enseignant_id in [cand.enseignant_id for cand in candidats_avec_conflit]
            for c in surveillants_selectionnes
        ) if 'candidats_avec_conflit' in dir() else False

        # Étape 4: Vérifier si complet
        if len(surveillants_selectionnes) < planif.nb_surveillants_requis:
            result.statut = "CONFLIT"
            result.surveillants_affectes = surveillants_selectionnes
            result.manquants = planif.nb_surveillants_requis - len(surveillants_selectionnes)
            result.violations = violations
        else:
            result.surveillants_affectes = surveillants_selectionnes
            # ✅ NOUVEAU: Ajouter un avertissement si contrainte matière a été levée
            if a_utilise_conflit_matiere:
                result.violations.append(ConstraintViolation(
                    enseignant_id=0,
                    nom="AVERTISSEMENT",
                    prenom="",
                    raison=ReasonExclusion.CONFLIT_MATIERE,
                    details="Contrainte matière levée en dernier recours (enseignant surveille sa propre matière)",
                ))

        return result

    def _get_enseignants_departement(self, departement_id: int) -> list[EnseignantCandidat]:
        """Récupérer tous les enseignants d'un département avec leurs infos."""
        enseignants = self.db.query(
            Enseignant.id,
            Enseignant.nom,
            Enseignant.prenom,
            Enseignant.grade,
            Enseignant.departement_id,
        ).filter(Enseignant.departement_id == departement_id).all()

        candidats = []
        for ens in enseignants:
            # Récupérer le volume horaire (assume current year)
            from datetime import datetime as dt
            current_year = f"{dt.now().year}/{dt.now().year + 1}"
            charge = self.db.query(ChargeHoraire).filter(
                ChargeHoraire.enseignant_id == ens.id,
                ChargeHoraire.annee_univ == current_year,
            ).first()

            volume_horaire = charge.volume_horaire if charge else 0.0
            departement = self.db.query(Departement).filter(Departement.id == departement_id).first()

            candidats.append(EnseignantCandidat(
                enseignant_id=ens.id,
                nom=ens.nom,
                prenom=ens.prenom,
                grade=ens.grade,
                departement_id=ens.departement_id,
                departement_nom=departement.nom if departement else "Unknown",
                volume_horaire=volume_horaire,
                volume_restant=volume_horaire,
                volume_consomme=0.0,
                nb_surveillances=0,
            ))

        return candidats

    def _get_charge_consumed(
        self,
        enseignant_id: int,
        annee_univ: str,
    ) -> float:
        """Calculer la charge totale consommée par un enseignant en une année universitaire."""
        result = self.db.query(func.coalesce(func.sum(Surveillance.charge), 0)).filter(
            Surveillance.enseignant_id == enseignant_id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
        ).join(PlanificationExamen).join(SessionModel).filter(
            SessionModel.annee_universitaire == annee_univ,
        ).scalar()

        return float(result)

    def _check_disponibilite_temporelle(
        self,
        enseignant_id: int,
        planif: PlanificationExamen,
    ) -> bool:
        """Vérifier la disponibilité temporelle d'un enseignant (Contrainte 1 - HARD)."""
        # Récupérer le créneau de la planification
        creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        if not creneau:
            return False

        # Vérifier s'il y a une indisponibilité qui chevauche
        indisponibilites = self.db.query(DisponibiliteEnseignant).filter(
            DisponibiliteEnseignant.enseignant_id == enseignant_id,
            DisponibiliteEnseignant.date == creneau.date,
            DisponibiliteEnseignant.type_dispo.in_(["INDISPONIBLE", "COURS_PREVU", "MISSION", "CONGE"]),
        ).all()

        for indispo in indisponibilites:
            # Vérifier le chevauchement horaire
            if (indispo.heure_debut < creneau.heure_fin and
                indispo.heure_fin > creneau.heure_debut):
                return False

        return True

    def _check_conflit_simultaneite(
        self,
        enseignant_id: int,
        planif: PlanificationExamen,
    ) -> bool:
        """Vérifier la non-simultanéité (Contrainte 4 - HARD)."""
        creneau = self.db.query(Creneau).filter(Creneau.id == planif.creneau_id).first()
        if not creneau:
            return False

        conflits = self.db.query(Surveillance).join(PlanificationExamen).join(Creneau).filter(
            Surveillance.enseignant_id == enseignant_id,
            Surveillance.statut_surveillance.in_(["AFFECTE", "CONFIRME"]),
            Creneau.date == creneau.date,
            Creneau.heure_debut == creneau.heure_debut,
        ).all()

        return len(conflits) > 0

    def _check_conflit_matiere(
        self,
        enseignant_id: int,
        planif: PlanificationExamen,
    ) -> bool:
        """Vérifier le conflit de matière (Contrainte 2 - SOFT)."""
        from app.models.section_matiere import SectionMatiere

        # Récupérer la section_matiere de la planification
        section_matiere = self.db.query(SectionMatiere).filter(
            SectionMatiere.id == planif.section_matiere_id,
        ).first()

        if not section_matiere:
            return False

        # Vérifier si l'enseignant enseigne cette matière (COURS ou TD)
        enseignement = self.db.query(Enseignement).filter(
            Enseignement.enseignant_id == enseignant_id,
            Enseignement.matiere_id == section_matiere.matiere_id,
            Enseignement.type_enseignement.in_(["COURS", "TD"]),
        ).first()

        return enseignement is not None

    def _creer_surveillance(
        self,
        planif: PlanificationExamen,
        candidat: EnseignantCandidat,
    ) -> Surveillance:
        """Créer une surveillance dans la base de données."""
        payload = SurveillanceCreate(
            planification_id=planif.id,
            enseignant_id=candidat.enseignant_id,
            charge=float(planif.duree / 60),  # Convertir minutes en heures
            mode_affectation=ModeAffectation.AUTOMATIQUE.value,
            statut_surveillance=StatutSurveillance.AFFECTE.value,
            est_externe=False,
            motif_externe=None,
        )

        return create_surveillance(self.db, payload)
