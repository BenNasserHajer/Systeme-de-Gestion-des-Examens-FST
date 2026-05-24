import type {
  GenerationResult,
  Planification,
  PlanificationUpdatePayload,
  PlanifSalleAssign,
  TypeEpreuve,
} from "@/lib/types/planification";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function handleResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    let detail = fallbackMessage;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) {
        detail = typeof body.detail === "string" ? body.detail : fallbackMessage;
      }
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

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
  payload: import("@/lib/types/planification").PlanificationCreatePayload,
): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Failed to create planification");
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
  const response = await fetch(`${API_BASE}/planifications/${buildQuery(params)}`, {
    cache: "no-store",
  });
  return handleResponse(response, "Failed to fetch planifications");
}

export async function getPlanification(id: number): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}`, { cache: "no-store" });
  return handleResponse(response, "Failed to fetch planification");
}

export async function updatePlanification(
  id: number,
  payload: PlanificationUpdatePayload,
): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Failed to update planification");
}

export async function getEmploiDuTemps(
  sessionId: number,
  params?: {
    section_id?: number;
    type_epreuve?: string;
    statut?: string;
  },
): Promise<Planification[]> {
  const response = await fetch(
    `${API_BASE}/sessions/${sessionId}/emploi-du-temps${buildQuery(params)}`,
    { cache: "no-store" },
  );
  return handleResponse(response, "Failed to fetch emploi du temps");
}

export async function genererPlanificationSimple(payload: {
  session_id: number;
  section_label: string;
  niveau: string;
  type_epreuve_label: string;
}): Promise<GenerationResult> {
  const response = await fetch(`${API_BASE}/sessions/${payload.session_id}/generer-simple`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: payload.session_id,
      section_label: payload.section_label,
      niveau: payload.niveau,
      type_epreuve_label: payload.type_epreuve_label,
    }),
  });
  return handleResponse(response, "Echec de la generation automatique");
}

export async function validerSessionPlanifications(
  sessionId: number,
  sectionId?: number,
): Promise<Planification[]> {
  const response = await fetch(`${API_BASE}/sessions/${sessionId}/valider`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sectionId ? { section_id: sectionId } : {}),
  });
  return handleResponse(response, "Echec de la validation");
}

export async function affecterSalles(
  id: number,
  salles: PlanifSalleAssign[],
): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}/salles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(salles),
  });
  return handleResponse(response, "Failed to affecter salles");
}

export type { TypeEpreuve };
