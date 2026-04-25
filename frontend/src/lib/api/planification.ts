import type {
  Planification,
  PlanificationCreatePayload,
  PlanificationUpdatePayload,
  PlanifSalleAssign,
} from "@/lib/types/planification";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function getPlanifications(params?: {
  session_id?: number;
  section_id?: number;
  date_examen?: string;
  type_epreuve?: string;
  statut?: string;
  skip?: number;
  limit?: number;
}): Promise<Planification[]> {
  const queryParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value));
      }
    });
  }
  const url = `${API_BASE}/planifications/?${queryParams.toString()}`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch planifications");
  }
  return response.json();
}

export async function getPlanification(id: number): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch planification");
  }
  return response.json();
}

export async function createPlanification(
  payload: PlanificationCreatePayload,
): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create planification");
  }
  return response.json();
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
  if (!response.ok) {
    throw new Error("Failed to update planification");
  }
  return response.json();
}

export async function deletePlanification(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/planifications/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete planification");
  }
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
  if (!response.ok) {
    throw new Error("Failed to affecter salles");
  }
  return response.json();
}

export async function getEmploiDuTemps(
  sessionId: number,
  params?: {
    section_id?: number;
    type_epreuve?: string;
    statut?: string;
  }
): Promise<Planification[]> {
  const queryParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        queryParams.append(key, String(value));
      }
    });
  }
  const url = `${API_BASE}/sessions/${sessionId}/emploi-du-temps?${queryParams.toString()}`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch emploi du temps");
  }
  return response.json();
}

export async function validerPlanification(id: number): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}/valider`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to valider planification");
  }
  return response.json();
}

export async function publierPlanification(id: number): Promise<Planification> {
  const response = await fetch(`${API_BASE}/planifications/${id}/publier`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error("Failed to publier planification");
  }
  return response.json();
}
