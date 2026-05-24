/**
 * API client for Surveillance (Proctoring) operations
 */

import type { GetAllSurveillantsResponse } from "@/lib/types/surveillance";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

// ============================================================================
// TYPES
// ============================================================================

export interface Departement {
  id: number;
  nom: string;
  code: string;
}

export interface Enseignant {
  enseignant_id: number;
  nom: string;
  prenom: string;
  grade: string | null;
  departement: Departement;
  volume_horaire: number;
  volume_consomme: number;
  volume_restant: number;
  taux_utilisation: number;
  nb_surveillances: number;
}

export interface EnseignantDisponible extends Enseignant {
  avertissements?: string[];
  est_externe?: boolean;
}

export interface GroupeResult {
  groupe: {
    id: number;
    numero: string;
    effectif: number;
  } | null;
  salle: {
    id: number;
    code: string;
    capacite: number;
  } | null;
  statut: string;
  surveillants_affectes: Array<{
    surveillance_id: number;
    enseignant_id: number;
    nom: string;
    prenom: string;
    grade: string | null;
    departement: Departement;
  }>;
  surveillants_requis: number;
  manquants: number;
}

export interface PlanificationResult {
  planification_id: number;
  type_epreuve: string;
  semestre: number;
  duree: number;
  statut_planif: string;
  matiere: {
    id: number;
    code: string;
    intitule: string;
  } | null;
  section: {
    id: number;
    nom: string;
  } | null;
  creneau: {
    id: number;
    date: string;
    heure_debut: string;
    heure_fin: string;
  } | null;
  statut: "AFFECTEE" | "CONFLIT" | "CONFLIT_PARTIEL";
  surveillants_requis: number;
  surveillants_affectes: number;
  manquants: number;
  groupes: GroupeResult[];
  raisons_exclusion: Array<{
    enseignant_id: number;
    nom: string;
    prenom: string;
    raison: string;
    details: string | null;
  }>;
}

export interface AffectationAutomatiqueResponse {
  session_id: number;
  session: {
    id: number;
    type_session: string;
    annee_universitaire: string;
    date_debut: string;
    date_fin: string;
    statut: string;
  } | null;
  total_planifications: number;
  affectees_automatiquement: number;
  en_conflit: number;
  message: string;
  resultats: PlanificationResult[];
  non_affectees: PlanificationResult[];
}

export interface ManualAssignmentRequest {
  session_id: number;
  planification_id: number;
  groupe_id: number;
  salle_id: number;
  enseignant_ids: number[];
  motifs_externes?: Record<string, string>;
}

export interface EnseignantsDisponiblesResponse {
  planification_id: number;
  date_planification: string;
  total_disponibles: number;
  total_avec_avertissement: number;
  departements: Array<{
    departement_id: number;
    departement_nom: string;
    departement_code: string;
    total: number;
    enseignants: EnseignantDisponible[];
  }>;
}

// ============================================================================
// HELPER
// ============================================================================

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `HTTP ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

// ============================================================================
// AFFECTATION AUTOMATIQUE
// ============================================================================

/**
 * Lance l'algorithme d'affectation automatique pour une session
 */
export async function affecterSessionAutomatique(
  sessionId: number,
  filters?: {
    section_nom?: string;
    periode?: string;
    type_epreuve?: string;
    save?: boolean;
  }
): Promise<AffectationAutomatiqueResponse> {
  const response = await fetch(`${API_BASE}/surveillances/affecter-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      ...filters,
    }),
  });
  return handleResponse<AffectationAutomatiqueResponse>(response);
}

// ============================================================================
// AFFECTATION MANUELLE
// ============================================================================

/**
 * Affecte manuellement des enseignants à une planification (résolution de conflit)
 */
export async function affecterManuellement(
  data: ManualAssignmentRequest
): Promise<any> {
  const response = await fetch(`${API_BASE}/surveillances/manual-assignment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

// ============================================================================
// CONSULTATION
// ============================================================================

/**
 * Récupère la liste des enseignants disponibles pour une planification
 */
export async function getEnseignantsDisponibles(
  planifId: number
): Promise<EnseignantsDisponiblesResponse> {
  const response = await fetch(
    `${API_BASE}/surveillances/enseignants-disponibles/${planifId}`
  );
  return handleResponse<EnseignantsDisponiblesResponse>(response);
}

/**
 * Récupère tous les enseignants avec leur volume horaire
 */
export async function getAllSurveillants(
  sessionId: number,
  params?: {
    page?: number;
    limit?: number;
    sort?: string;
    order?: "asc" | "desc";
  }
): Promise<GetAllSurveillantsResponse> {
  const query = new URLSearchParams({
    session_id: sessionId.toString(),
    page: (params?.page || 1).toString(),
    limit: (params?.limit || 100).toString(),
    sort: params?.sort || "volume_restant",
    order: params?.order || "desc",
  });

  const response = await fetch(
    `${API_BASE}/surveillances/getallsurveillants?${query}`
  );
  return handleResponse(response);
}

/**
 * Récupère toutes les surveillances d'une session
 */
export async function getSessionSurveillances(
  sessionId: number,
  filters?: {
    departement_id?: number;
    groupe_id?: number;
    salle_id?: number;
    type_epreuve?: string;
    statut?: string;
    section_id?: number;
    enseignant_id?: number;
    semestre?: number;
    skip?: number;
    limit?: number;
  }
): Promise<any> {
  const query = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        query.set(key, value.toString());
      }
    });
  }

  const response = await fetch(
    `${API_BASE}/surveillances/${sessionId}${query.toString() ? `?${query}` : ""}`
  );
  return handleResponse(response);
}

// ============================================================================
// GESTION
// ============================================================================

/**
 * Supprime une surveillance
 */
export async function deleteSurveillance(surveillanceId: number): Promise<void> {
  const response = await fetch(
    `${API_BASE}/surveillances/${surveillanceId}`,
    {
      method: "DELETE",
    }
  );
  return handleResponse<void>(response);
}

/**
 * Remplace un enseignant dans une surveillance
 */
export async function remplacerSurveillant(
  surveillanceId: number,
  nouvelEnseignantId: number,
  motifExterne?: string
): Promise<any> {
  const response = await fetch(
    `${API_BASE}/surveillances/${surveillanceId}/reassign`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nouvel_enseignant_id: nouvelEnseignantId,
        motif_externe: motifExterne,
      }),
    }
  );
  return handleResponse(response);
}

// ============================================================================
// DISPONIBILITÉS
// ============================================================================

/**
 * Récupère les disponibilités d'un enseignant
 */
export async function getEnseignantDisponibilites(
  enseignantId: number,
  params?: {
    annee_universitaire?: string;
    date_debut?: string;
    date_fin?: string;
  }
): Promise<any> {
  const query = new URLSearchParams();
  if (params?.annee_universitaire) query.set("annee_universitaire", params.annee_universitaire);
  if (params?.date_debut) query.set("date_debut", params.date_debut);
  if (params?.date_fin) query.set("date_fin", params.date_fin);

  const response = await fetch(
    `${API_BASE}/surveillances/enseignant/${enseignantId}/disponibilites${query.toString() ? `?${query}` : ""}`
  );
  return handleResponse(response);
}

/**
 * Crée une disponibilité pour un enseignant
 */
export async function createDisponibilite(data: {
  enseignant_id: number;
  date: string;
  heure_debut: string;
  heure_fin: string;
  type_dispo: string;
  motif?: string | null;
  confirme?: boolean;
}): Promise<any> {
  const response = await fetch(`${API_BASE}/disponibilites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse(response);
}

/**
 * Récupère toutes les surveillances d'un enseignant
 */
export async function getEnseignantSurveillances(
  enseignantId: number,
  params?: {
    annee_universitaire?: string;
    semestre?: number;
    type_epreuve?: string;
  }
): Promise<any> {
  const query = new URLSearchParams();
  if (params?.annee_universitaire) query.set("annee_universitaire", params.annee_universitaire);
  if (params?.semestre) query.set("semestre", params.semestre.toString());
  if (params?.type_epreuve) query.set("type_epreuve", params.type_epreuve);

  const response = await fetch(
    `${API_BASE}/surveillances/enseignant/${enseignantId}/toutes-surveillances${query.toString() ? `?${query}` : ""}`
  );
  return handleResponse(response);
}
