import type {
  GenerationAutoResponse,
  Planification,
  PlanificationCreatePayload,
  PlanifSalleAssign,
  TypeEpreuve,
  ValiderSessionResponse,
} from "@/lib/types/planification";

import { apiFetch, handleApiResponse } from "@/lib/api/errors";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

function buildQuery(params?: Record<string, string | number | undefined>): string {
  const queryParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value));
      }
    });
  }
  const qs = queryParams.toString();
  return qs ? `?${qs}` : "";
}

export async function createPlanification(
  payload: PlanificationCreatePayload,
): Promise<Planification> {
  const response = await apiFetch(`${API_BASE}/planifications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleApiResponse(response, "Echec de la creation de l'examen");
}

export async function getPlanifications(params?: {
  session_id?: number;
  section_id?: number;
  date_examen?: string;
  type_epreuve?: string;
  statut?: string;
  skip?: number;
  limit?: number;
}): Promise<Planification[]> {
  const response = await apiFetch(`${API_BASE}/planifications${buildQuery(params)}`, {
    cache: "no-store",
  });
  return handleApiResponse(response, "Impossible de charger les planifications");
}

export async function getEmploiDuTemps(
  sessionId: number,
  params?: {
    section_id?: number;
    type_epreuve?: string;
    statut?: string;
  },
): Promise<Planification[]> {
  const response = await apiFetch(
    `${API_BASE}/sessions/${sessionId}/emploi-du-temps${buildQuery(params)}`,
    { cache: "no-store" },
  );
  return handleApiResponse(response, "Impossible de charger l'emploi du temps");
}

export async function genererAuto(payload: {
  section_id: number;
  session_id: number;
  type_epreuve: TypeEpreuve;
  semestre: string;
}): Promise<GenerationAutoResponse> {
  const response = await apiFetch(`${API_BASE}/planification/generer-auto`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleApiResponse(response, "Echec de la generation automatique");
}

export async function deplacerPlanification(
  id: number,
  payload: {
    nouvelle_date: string;
    nouvelle_heure_debut: string;
    nouvelle_heure_fin: string;
  },
): Promise<{ planification: Planification; warnings: string[] }> {
  const response = await apiFetch(`${API_BASE}/planification/${id}/deplacer`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await handleApiResponse<{
    success: boolean;
    planification: Planification;
    warnings: string[];
  }>(response, "Echec du deplacement");
  return { planification: data.planification, warnings: data.warnings };
}

export async function changerSallePlanification(
  id: number,
  payload: { groupe_id?: number; nouvelle_salle_id: string },
): Promise<{ planification: Planification; warnings: string[] }> {
  const response = await apiFetch(`${API_BASE}/planification/${id}/changer-salle`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ groupe_id: payload.groupe_id ?? 1, nouvelle_salle_id: payload.nouvelle_salle_id }),
  });
  const data = await handleApiResponse<{
    success: boolean;
    planification: Planification;
    warnings: string[];
  }>(response, "Echec du changement de salle");
  return { planification: data.planification, warnings: data.warnings };
}

export async function validerSession(payload: {
  session_id: number;
  section_id?: number;
}): Promise<ValiderSessionResponse> {
  const response = await apiFetch(`${API_BASE}/planification/valider-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleApiResponse(response, "Echec de la validation");
}

export async function affecterSalles(
  id: number,
  salles: PlanifSalleAssign[],
): Promise<Planification> {
  const response = await apiFetch(`${API_BASE}/planifications/${id}/salles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(salles),
  });
  return handleApiResponse(response, "Echec de l'affectation des salles");
}

export type { TypeEpreuve };
