"""Pydantic schemas for surveillance management."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ModeAffectation(str, Enum):
    """Mode d'affectation des surveillances."""
    AUTOMATIQUE = "AUTOMATIQUE"
    MANUELLE = "MANUELLE"


class StatutSurveillance(str, Enum):
    """Statut d'une surveillance."""
    AFFECTE = "AFFECTE"
    CONFIRME = "CONFIRME"


class ReasonExclusion(str, Enum):
    """Raisons d'exclusion d'un enseignant."""
    INDISPONIBLE = "INDISPONIBLE"
    VOLUME_EPUISE = "VOLUME_EPUISE"
    CONFLIT_MATIERE = "CONFLIT_MATIERE"
    DEJA_AFFECTE = "DEJA_AFFECTE"
    DEPARTEMENT_DIFFERENT = "DEPARTEMENT_DIFFERENT"
    AUTRE = "AUTRE"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class SurveillanceBase(BaseModel):
    """Base schema for surveillance."""
    planification_id: int
    enseignant_id: int
    charge: float = Field(default=1.0, ge=0.0)
    presence: bool = False
    mode_affectation: ModeAffectation = ModeAffectation.AUTOMATIQUE
    statut_surveillance: StatutSurveillance = StatutSurveillance.AFFECTE
    est_externe: bool = Field(default=False, description="Enseignant d'un autre département")
    motif_externe: Optional[str] = Field(None, description="Motif du recours à un enseignant externe")


class SurveillanceCreate(BaseModel):
    """Schema for creating a surveillance entry."""
    planification_id: int
    enseignant_id: int
    charge: float = Field(default=1.0, ge=0.0)
    mode_affectation: ModeAffectation = ModeAffectation.AUTOMATIQUE
    statut_surveillance: StatutSurveillance = StatutSurveillance.AFFECTE
    est_externe: bool = Field(default=False)
    motif_externe: Optional[str] = None


class SurveillanceUpdate(BaseModel):
    """Schema for updating a surveillance entry."""
    presence: Optional[bool] = None
    statut_surveillance: Optional[StatutSurveillance] = None
    charge: Optional[float] = Field(default=None, ge=0.0)
    motif_externe: Optional[str] = None


class SurveillanceOut(SurveillanceBase):
    """Schema returned from API."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ENSEIGNANT INFO SCHEMAS (for lists and reports)
# ============================================================================

class EnseignantVolumeInfo(BaseModel):
    """Info sur un enseignant et son volume horaire."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str] = None
    email: Optional[str] = None
    volume_horaire: float
    volume_restant: float
    charge_imputee: float = Field(description="Sum of charges for this academic year")
    nb_surveillances: int = Field(description="Count of surveillances (AFFECTE + CONFIRME)")
    peut_accepter: bool = Field(description="Can accept more surveillance (for manual mode indication)")


class EnseignantExclusionReason(BaseModel):
    """Raison d'exclusion d'un enseignant pour une planification."""
    enseignant_id: int
    nom: str
    prenom: str
    raison: ReasonExclusion


# ============================================================================
# PLANIFICATION RESULT SCHEMAS
# ============================================================================

class SurveillantAffecte(BaseModel):
    """Surveillant affecté à une planification."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str] = None
    charge_imputee: float
    mode_affectation: ModeAffectation
    status_surveillance: StatutSurveillance
    est_externe: bool = False
    motif_externe: Optional[str] = None


class PlanificationResultAFFECTEE(BaseModel):
    """Résultat quand une planification est complètement affectée."""
    planification_id: int
    statut: str = "AFFECTEE"
    surveillants: list[SurveillantAffecte]


class PlanificationResultCONFLIT(BaseModel):
    """Résultat quand une planification est en conflit."""
    planification_id: int
    matiere_code: str
    matiere_intitule: str
    statut: str = "CONFLIT"
    surveillants_requis: int
    surveillants_trouves: int
    surveillants_affectes: list[SurveillantAffecte] = []
    manquants: int
    raisons_exclusion: list[EnseignantExclusionReason]


PlanificationResult = PlanificationResultAFFECTEE | PlanificationResultCONFLIT


# ============================================================================
# BULK AFFECTATION SCHEMAS
# ============================================================================

class BulkAffectationRequest(BaseModel):
    """Request body for bulk automatic affectation."""
    session_id: int


class BulkAffectationResponse(BaseModel):
    """Response for bulk automatic affectation."""
    session_id: int
    total_planifications: int
    affectees_automatiquement: int
    en_conflit: int
    affectees_manuellement_anterieures: int = Field(description="Already manual before this bulk op")
    resultats: list[PlanificationResult]


# ============================================================================
# MANUAL VALIDATION SCHEMAS
# ============================================================================

class ValidationManuelleRequest(BaseModel):
    """Request for manual validation of conflicted planification."""
    session_id: int
    planification_id: int
    enseignant_ids: list[int] = Field(min_items=1)


class ConfitErreurEnseignant(BaseModel):
    """Erreur pour un enseignant spécifique en validation manuelle."""
    enseignant_id: int
    raison: ReasonExclusion


class ValidationManuelleResponse(BaseModel):
    """Response for successful manual validation."""
    planification_id: int
    statut: str = "AFFECTEE_MANUELLEMENT"
    surveillants_inseres: list[SurveillantAffecte]


class ValidationManuelleErrorResponse(BaseModel):
    """Error response for manual validation."""
    statut: str = "ERREUR_VALIDATION"
    erreurs: list[ConfitErreurEnseignant]


# ============================================================================
# SESSION CONSOLIDATED SCHEMAS
# ============================================================================

class StatutAffectationPlanif(str, Enum):
    """Statut d'affectation d'une planification."""
    COMPLETE = "COMPLETE"
    PARTIELLE = "PARTIELLE"
    NON_AFFECTEE = "NON_AFFECTEE"


class CreneauInfo(BaseModel):
    """Info sur un créneau."""
    date: str
    heure_debut: str
    heure_fin: str
    libelle: Optional[str] = None


class MatiereInfo(BaseModel):
    """Info sur une matière."""
    code: str
    intitule: str
    coefficient: Optional[float] = None


class SalleInfo(BaseModel):
    """Info sur une salle."""
    code: str
    designation: Optional[str] = None
    capacite: int
    batiment: Optional[str] = None


class SectionInfo(BaseModel):
    """Info sur une section."""
    nom: str
    nb_etudiants: Optional[int] = None
    niveau: Optional[str] = None


class PlanificationConsolidee(BaseModel):
    """Info consolidée sur une planification avec ses surveillants."""
    planification_id: int
    statut_affectation: StatutAffectationPlanif
    type_epreuve: str
    duree: int
    creneau: CreneauInfo
    matiere: MatiereInfo
    section: SectionInfo
    salles: list[SalleInfo]
    nb_surveillants_requis: int
    nb_surveillants_affectes: int
    surveillants: list[SurveillantAffecte]


class SessionInfo(BaseModel):
    """Info générale sur la session."""
    id: int
    type_session: str
    annee_univ: str
    date_debut: str
    date_fin: str
    statut: str


class StatistiquesSession(BaseModel):
    """Statistiques d'affectation pour une session."""
    total_planifications: int
    completes: int
    partielles: int
    non_affectees: int
    affectees_manuellement: int = 0


class SessionConsolideeResponse(BaseModel):
    """Réponse complète pour une session."""
    session: SessionInfo
    statistiques: StatistiquesSession
    planifications: list[PlanificationConsolidee]


# ============================================================================
# RAPPORT SCHEMAS
# ============================================================================

class RapportPlanification(BaseModel):
    """Détail d'une planification dans le rapport."""
    planification_id: int
    matiere_code: str
    matiere_intitule: str
    section_nom: str
    creneau: CreneauInfo
    salles: list[SalleInfo]
    type_epreuve: str
    nb_surveillants_requis: int
    surveillants: list[SurveillantAffecte]


class ClassementEnseignant(BaseModel):
    """Classement d'un enseignant par charge cumulée."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str] = None
    charge_totale: float
    nb_surveillances: int
    taux_utilisation: float = Field(description="charge_totale / volume_horaire * 100")


class RapportSessionResponse(BaseModel):
    """Rapport complet d'une session."""
    session: SessionInfo
    statistiques: StatistiquesSession
    planifications: list[RapportPlanification]
    en_conflit: list[RapportPlanification] = []
    classement_enseignants: list[ClassementEnseignant]
    date_generation: datetime


# ============================================================================
# MANUAL ASSIGNMENT SCHEMAS
# ============================================================================

class ManualAssignmentRequest(BaseModel):
    """Request for manual assignment of a single planification."""
    session_id: int
    planification_id: int
    enseignant_ids: list[int] = Field(min_items=1, description="Liste des enseignants à affecter")
    motifs_externes: dict[int, Optional[str]] = Field(
        default_factory=dict,
        description="Motifs des affectations externes par enseignant_id"
    )


class ManualAssignmentBatchRequest(BaseModel):
    """Request for batch manual assignment of entire session."""
    session_id: int
    affectations: dict[int, list[int]] = Field(
        ...,
        description="Map planification_id -> liste des enseignant_ids"
    )
    motifs_externes: dict[int, Optional[str]] = Field(
        default_factory=dict,
        description="Motifs des affectations externes par enseignant_id"
    )


class ManualAssignmentResponse(BaseModel):
    """Response for successful manual assignment."""
    planification_id: int
    statut: str = "CONFLIT_RESOLU"
    surveillants_inseres: list[SurveillantAffecte]


class ManualAssignmentBatchResponse(BaseModel):
    """Response for batch manual assignment."""
    session_id: int
    statut: str
    total_planifications: int
    total_surveillances_inserees: int
    planifications_non_affectees: list[int] = []
    detail: list[PlanificationConsolidee]


# ============================================================================
# DISPONIBLES ENSEIGNANTS SCHEMA
# ============================================================================

class DepartementInfo(BaseModel):
    """Info sur un département."""
    id: int
    nom: str
    code: str


class EnseignantDisponible(BaseModel):
    """Enseignant disponible pour affectation."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str] = None
    departement: DepartementInfo
    volume_horaire: float
    volume_consomme: float
    volume_restant: float
    nb_surveillances: int


class EnseignantsDisponiblesResponse(BaseModel):
    """Liste des enseignants disponibles."""
    data: list[EnseignantDisponible]
    pagination: Optional[dict] = None


# ============================================================================
# REPLACEMENT SCHEMA
# ============================================================================

class RemplacementRequest(BaseModel):
    """Request for replacing an enseignant on a surveillance."""
    nouvel_enseignant_id: int = Field(..., description="ID du nouvel enseignant")
    motif: str = Field(..., description="Motif du remplacement")


class RemplacementResponse(BaseModel):
    """Response for replacement."""
    ancienne_surveillance_id: int
    nouvelle_surveillance_id: int
    enseignant_remplace: dict
    enseignant_remplacant: dict
    motif: str


# ============================================================================
# EXPORT SCHEMAS
# ============================================================================

class ExportFormatEnum(str, Enum):
    """Formats d'export supportés."""
    CSV = "csv"
    XLSX = "xlsx"


# ============================================================================
# AFFECTATION SESSION SCHEMAS
# ============================================================================

class AffecterSessionRequest(BaseModel):
    """Request body for automatic affectation."""
    session_id: int = Field(..., description="ID de la session", example=1)


class GetAllSurveillantsParams(BaseModel):
    """Query parameters for getallsurveillants."""
    session_id: int = Field(..., description="ID de la session", example=1)
    page: int = Field(1, ge=1, description="Numéro de page")
    limit: int = Field(20, ge=1, le=100, description="Nombre d'éléments par page")
    sort: str = Field("volume_restant", description="Champ de tri")
    order: str = Field("desc", pattern="^(asc|desc)$", description="Ordre de tri")


class GetDisponibilitesParams(BaseModel):
    """Query parameters for enseignant disponibilites."""
    date_debut: str = Field(..., description="Date de début (YYYY-MM-DD)", example="2026-01-01")
    date_fin: str = Field(..., description="Date de fin (YYYY-MM-DD)", example="2026-01-31")


class ExportSessionParams(BaseModel):
    """Query parameters for export session."""
    format: str = Field("csv", pattern="^(csv|xlsx)$", description="Format d'export")

# ============================================================================
# REPONSES SCHEMAS
# ============================================================================

class AffecterSessionResult(BaseModel):
    """Résultat de l'affectation automatique pour une planification."""
    planification_id: int
    statut: str
    surveillants_requis: int
    surveillants_affectes: int
    manquants: int
    raisons_exclusion: list = []


class AffecterSessionResponse(BaseModel):
    """Réponse complète de l'affectation automatique d'une session."""
    session_id: int
    total_planifications: int
    affectees_automatiquement: int
    en_conflit: int
    message: str
    resultats: list[AffecterSessionResult]


class GetAllSurveillantsItem(BaseModel):
    """Enseignant dans la liste getallsurveillants."""
    enseignant_id: int
    nom: str
    prenom: str
    grade: Optional[str] = None
    departement: dict
    volume_horaire: float
    volume_consomme: float
    volume_restant: float
    nb_surveillances: int


class GetAllSurveillantsResponse(BaseModel):
    """Réponse de getallsurveillants."""
    data: list[GetAllSurveillantsItem]
    pagination: dict


class DisponibiliteItem(BaseModel):
    """Disponibilité d'un enseignant."""
    date: str
    heure_debut: str
    heure_fin: str
    type: str
    motif: Optional[str] = None


class GetDisponibilitesResponse(BaseModel):
    """Réponse des disponibilités d'un enseignant."""
    enseignant_id: int
    date_debut: str
    date_fin: str
    disponibilites: list[DisponibiliteItem]


class StatistiquesResponse(BaseModel):
    """Réponse des statistiques globales."""
    annee_universitaire: str
    total_surveillances: int
    total_heures: float
    unique_enseignants: int
    count_externes: int
    taux_externe: float
    taux_remplissage: float