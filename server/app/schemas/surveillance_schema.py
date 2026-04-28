"""Pydantic schemas for surveillance module — version complète alignée sur l'algorithme v3."""

from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


# ─────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────

class ModeAffectation(str, Enum):
    AUTOMATIQUE = "AUTOMATIQUE"
    MANUELLE    = "MANUELLE"


class StatutSurveillance(str, Enum):
    AFFECTE  = "AFFECTE"
    CONFIRME = "CONFIRME"


class ReasonExclusion(str, Enum):
    INDISPONIBLE      = "INDISPONIBLE"
    DEJA_AFFECTE      = "DEJA_AFFECTE"
    VOLUME_EPUISE     = "VOLUME_EPUISE"
    CONFLIT_MATIERE   = "CONFLIT_MATIERE"
    HORS_DEPARTEMENT  = "HORS_DEPARTEMENT"


# ─────────────────────────────────────────────────────────────
# Surveillance CRUD schemas
# ─────────────────────────────────────────────────────────────

class SurveillanceCreate(BaseModel):
    planification_id:    int
    enseignant_id:       int
    groupe_id:           Optional[int]            = None
    salle_id:            Optional[int]            = None
    charge:              float                    = 1.0
    mode_affectation:    ModeAffectation          = ModeAffectation.AUTOMATIQUE
    statut_surveillance: StatutSurveillance       = StatutSurveillance.AFFECTE
    est_externe:         bool                     = False
    motif_externe:       Optional[str]            = None


class SurveillanceUpdate(BaseModel):
    presence:            Optional[bool]               = None
    statut_surveillance: Optional[StatutSurveillance] = None
    charge:              Optional[float]               = None
    motif_externe:       Optional[str]                = None


class SurveillanceOut(BaseModel):
    id:                  int
    planification_id:    int
    enseignant_id:       int
    groupe_id:           Optional[int]
    salle_id:            Optional[int]
    charge:              float
    presence:            bool
    mode_affectation:    str
    statut_surveillance: str
    est_externe:         bool
    motif_externe:       Optional[str]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Manual assignment schemas
# ─────────────────────────────────────────────────────────────

class ManualAssignmentRequest(BaseModel):
    session_id:       int
    planification_id: int
    groupe_id:        int
    salle_id:         int
    enseignant_ids:   list[int]
    motifs_externes:  dict[int, str] = {}


class AffectationItem(BaseModel):
    planification_id: int
    groupe_id:        int
    salle_id:         int
    enseignant_ids:   list[int]


class ManualAssignmentBatchRequest(BaseModel):
    session_id:      int
    affectations:    list[AffectationItem]
    motifs_externes: dict[int, str] = {}


# ─────────────────────────────────────────────────────────────
# Affectation automatique — Request avec filtres
# ─────────────────────────────────────────────────────────────

class AffecterSessionRequest(BaseModel):
    session_id:   int
    section_nom:  Optional[str] = None
    periode:      Optional[str] = None
    type_epreuve: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Sous-objets enrichis pour la réponse complète
# ─────────────────────────────────────────────────────────────

class DepartementOut(BaseModel):
    id:   Optional[int]
    nom:  Optional[str]
    code: Optional[str]


class NiveauOut(BaseModel):
    id:             Optional[int]
    libelle:        Optional[str]
    type_formation: Optional[str]


class SectionOut(BaseModel):
    id:     Optional[int]
    nom:    Optional[str]
    niveau: Optional[NiveauOut] = None


class GroupeOut(BaseModel):
    id:           Optional[int]
    numero:       Optional[int]
    effectif:     Optional[int]
    nb_etudiants: Optional[int]
    annee:        Optional[str]


class SalleOut(BaseModel):
    id:          Optional[int]
    code:        Optional[str]
    designation: Optional[str]
    capacite:    Optional[int]
    batiment:    Optional[str]


class MatiereOut(BaseModel):
    id:           Optional[int]
    code:         Optional[str]
    intitule:     Optional[str]
    coefficient:  Optional[float]
    credit:       Optional[int]
    duree_examen: Optional[int]
    duree_ds:     Optional[int]


class CreneauOut(BaseModel):
    id:          Optional[int]
    date:        Optional[str]
    heure_debut: Optional[str]
    heure_fin:   Optional[str]
    libelle:     Optional[str]


class SessionOut(BaseModel):
    id:                  Optional[int]
    type_session:        Optional[str]
    annee_universitaire: Optional[str]
    date_debut:          Optional[str]
    date_fin:            Optional[str]
    statut:              Optional[str]


class EnseignantAffecteOut(BaseModel):
    surveillance_id:     int
    enseignant_id:       int
    nom:                 str
    prenom:              str
    grade:               Optional[str]
    email:               Optional[str]
    telephone:           Optional[str]
    departement:         Optional[DepartementOut]
    groupe:              Optional[GroupeOut]
    salle:               Optional[SalleOut]
    charge:              float
    mode_affectation:    str
    statut_surveillance: str
    presence:            bool
    est_externe:         bool
    motif_externe:       Optional[str]


# ─────────────────────────────────────────────────────────────
# Response schemas — Affectation automatique COMPLÈTE
# ─────────────────────────────────────────────────────────────

class RaisonExclusionOut(BaseModel):
    enseignant_id: int
    nom:           str
    prenom:        str
    raison:        str
    details:       Optional[str] = None


class GroupeResultOut(BaseModel):
    groupe:                Optional[GroupeOut]
    salle:                 Optional[SalleOut]
    statut:                str
    surveillants_affectes: list[EnseignantAffecteOut]
    surveillants_requis:   int
    manquants:             int


class AffecterSessionResult(BaseModel):
    planification_id:       int
    type_epreuve:           str           = ""
    semestre:               Optional[int] = None
    duree:                  Optional[int] = None
    statut_planif:          str           = ""
    nb_surveillants_requis: int           = 0
    matiere:                Optional[MatiereOut]     = None
    section:                Optional[SectionOut]     = None
    departement_examen:     Optional[DepartementOut] = None
    creneau:                Optional[CreneauOut]     = None
    session:                Optional[SessionOut]     = None
    statut:                 str
    surveillants_requis:    int
    surveillants_affectes:  int
    manquants:              int
    groupes:                list[GroupeResultOut]    = []
    raisons_exclusion:      list[RaisonExclusionOut] = []


class AffecterSessionResponse(BaseModel):
    session_id:                int
    session:                   Optional[SessionOut]         = None
    total_planifications:      int
    affectees_automatiquement: int
    en_conflit:                int
    message:                   str
    resultats:                 list[AffecterSessionResult]  = []
    non_affectees:             list[AffecterSessionResult]  = []


# ─────────────────────────────────────────────────────────────
# Enseignants disponibles — par département avec avertissements
# ─────────────────────────────────────────────────────────────

class AvertissementIndisponibilite(BaseModel):
    date:        str
    heure_debut: str
    heure_fin:   str
    type_dispo:  str
    motif:       Optional[str]


class EnseignantDisponibleV2(BaseModel):
    enseignant_id:    int
    nom:              str
    prenom:           str
    grade:            Optional[str]
    email:            Optional[str]
    telephone:        Optional[str]
    volume_horaire:   float
    volume_consomme:  float
    volume_restant:   float
    nb_surveillances: int
    a_avertissement:  bool
    avertissements:   list[AvertissementIndisponibilite] = []


class DepartementDisponiblesOut(BaseModel):
    departement_id:   Optional[int]
    departement_nom:  Optional[str]
    departement_code: Optional[str]
    enseignants:      list[EnseignantDisponibleV2]
    total:            int


class EnseignantsDisponiblesResponse(BaseModel):
    planification_id:         int
    date_planification:       str
    total_disponibles:        int
    total_avec_avertissement: int
    departements:             list[DepartementDisponiblesOut]


# ─────────────────────────────────────────────────────────────
# Ancien schéma conservé pour compatibilité interne
# ─────────────────────────────────────────────────────────────

class EnseignantDisponible(BaseModel):
    enseignant_id:    int
    nom:              str
    prenom:           str
    grade:            Optional[str]
    departement:      dict
    volume_horaire:   float
    volume_consomme:  float
    volume_restant:   float
    nb_surveillances: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────
# Listing enseignants
# ─────────────────────────────────────────────────────────────

class GetAllSurveillantsItem(BaseModel):
    enseignant_id:    int
    nom:              str
    prenom:           str
    grade:            Optional[str]
    departement:      dict
    volume_horaire:   float
    volume_consomme:  float
    volume_restant:   float
    nb_surveillances: int

    class Config:
        from_attributes = True


class GetAllSurveillantsResponse(BaseModel):
    data:       list[GetAllSurveillantsItem]
    pagination: dict


# ─────────────────────────────────────────────────────────────
# Disponibilités
# ─────────────────────────────────────────────────────────────

class DisponibiliteItem(BaseModel):
    date:        str
    heure_debut: str
    heure_fin:   str
    type:        str
    motif:       Optional[str]


class GetDisponibilitesResponse(BaseModel):
    enseignant_id:  int
    date_debut:     str
    date_fin:       str
    disponibilites: list[DisponibiliteItem]


# ─────────────────────────────────────────────────────────────
# Statistiques
# ─────────────────────────────────────────────────────────────

class StatistiquesResponse(BaseModel):
    annee_universitaire: str
    total_surveillances: int
    total_heures:        float
    unique_enseignants:  int
    count_externes:      int
    taux_externe:        float
    taux_remplissage:    float


# ─────────────────────────────────────────────────────────────
# Remplacement
# ─────────────────────────────────────────────────────────────

class RemplacementRequest(BaseModel):
    nouvel_enseignant_id: int
    motif:                Optional[str] = None