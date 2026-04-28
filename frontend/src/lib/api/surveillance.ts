import type {
  AffecterSessionResponse,
  DisponibiliteEnseignant,
  DisponibiliteEnseignantCreatePayload,
  EnseignantsDisponiblesResponse,
  GetAllSurveillantsResponse,
  GetDisponibilitesResponse,
  ManualAssignmentBatchRequest,
  ManualAssignmentRequest,
  StatistiquesResponse,
  SurveillanceUpdatePayload,
} from "@/lib/types/surveillance";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

type AffecterSessionRequest = {
  session_id: number;
  section_nom?: string;
  periode?: string;
  type_epreuve?: string;
};

type SessionSurveillancesResponse = {
  session: {
    id: number;
    type_session?: string | null;
    annee_universitaire?: string | null;
    date_debut?: string | null;
    date_fin?: string | null;
    statut?: string | null;
  };
  total: number;
  skip: number;
  limit: number;
  data: Array<Record<string, unknown>>;
};

type RapportSessionResponse = {
  session: Record<string, unknown>;
  statistiques: Record<string, unknown>;
  planifications: Array<Record<string, unknown>>;
  en_conflit: Array<Record<string, unknown>>;
  classement_enseignants: Array<Record<string, unknown>>;
  date_generation: string;
};

type ConflitsSessionResponse = {
  session_id: number;
  total_conflits: number;
  conflits: Array<Record<string, unknown>>;
};

type ReassignPayload = {
  nouvel_enseignant_id: number;
  motif?: string | null;
};

type ReassignResponse = {
  ancienne_surveillance_id: number;
  ancien_enseignant_id: number;
  motif?: string | null;
  nouvelle_surveillance: Record<string, unknown> | null;
};

type DeleteResponse = {
  message: string;
  id: number;
};

type ResetSessionResponse = {
  session_id: number;
  surveillances_supprimees: number;
  message: string;
};

function buildQuery(params: Record<string, string | number | boolean | null | undefined>) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }
    query.set(key, String(value));
  });
  return query.toString();
}

export async function affecterSession(
  payload: AffecterSessionRequest,
): Promise<AffecterSessionResponse> {
  const response = await fetch(`${API_BASE}/surveillances/affecter-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to affecter session");
  }
  return response.json();
}

export async function manualAssignment(
  payload: ManualAssignmentRequest,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/surveillances/manual-assignment`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to assign surveillants");
  }
  return response.json();
}

export async function manualAssignmentBatch(
  payload: ManualAssignmentBatchRequest,
): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/surveillances/manual-assignment-batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to assign surveillants batch");
  }
  return response.json();
}

export async function getSessionSurveillances(
  sessionId: number,
  filters: {
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
  } = {},
): Promise<SessionSurveillancesResponse> {
  const query = buildQuery(filters);
  const url = query
    ? `${API_BASE}/surveillances/${sessionId}?${query}`
    : `${API_BASE}/surveillances/${sessionId}`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch session surveillances");
  }
  return response.json();
}

export async function getSurveillanceDetail(
  surveillanceId: number,
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${API_BASE}/surveillances/${surveillanceId}/full-details`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Failed to fetch surveillance detail");
  }
  return response.json();
}

export async function getAllSurveillants(
  params: {
    session_id: number;
    page?: number;
    limit?: number;
    sort?: string;
    order?: "asc" | "desc";
  },
): Promise<GetAllSurveillantsResponse> {
  const query = buildQuery(params);
  const response = await fetch(`${API_BASE}/surveillances/getallsurveillants?${query}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to fetch surveillants list");
  }
  return response.json();
}

export async function getEnseignantsDisponibles(
  planifId: number,
): Promise<EnseignantsDisponiblesResponse> {
  const response = await fetch(
    `${API_BASE}/surveillances/enseignants-disponibles/${planifId}`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Failed to fetch enseignants disponibles");
  }
  return response.json();
}

export async function updateSurveillance(
  surveillanceId: number,
  payload: SurveillanceUpdatePayload,
): Promise<Record<string, unknown>> {
  const response = await fetch(
    `${API_BASE}/surveillances/edit/${surveillanceId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  if (!response.ok) {
    throw new Error("Failed to update surveillance");
  }
  return response.json();
}

export async function reassignSurveillance(
  surveillanceId: number,
  payload: ReassignPayload,
): Promise<ReassignResponse> {
  const response = await fetch(
    `${API_BASE}/surveillances/${surveillanceId}/reassign`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  if (!response.ok) {
    throw new Error("Failed to reassign surveillance");
  }
  return response.json();
}

export async function deleteSurveillance(surveillanceId: number): Promise<DeleteResponse> {
  const response = await fetch(`${API_BASE}/surveillances/${surveillanceId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete surveillance");
  }
  return response.json();
}

export async function resetSessionSurveillances(
  sessionId: number,
): Promise<ResetSessionResponse> {
  const response = await fetch(`${API_BASE}/surveillances/session/${sessionId}/reset`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to reset session surveillances");
  }
  return response.json();
}

export async function getSessionRapport(
  sessionId: number,
  departementId?: number,
): Promise<RapportSessionResponse> {
  const query = buildQuery({ departement_id: departementId });
  const url = query
    ? `${API_BASE}/surveillances/session/${sessionId}/rapport?${query}`
    : `${API_BASE}/surveillances/session/${sessionId}/rapport`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch session rapport");
  }
  return response.json();
}

export async function getSessionConflits(
  sessionId: number,
  filters: { semestre?: number; type_epreuve?: string; section_nom?: string } = {},
): Promise<ConflitsSessionResponse> {
  const query = buildQuery(filters);
  const url = query
    ? `${API_BASE}/surveillances/session/${sessionId}/conflits?${query}`
    : `${API_BASE}/surveillances/session/${sessionId}/conflits`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch session conflits");
  }
  return response.json();
}

export async function getStatistiques(annee_univ: string): Promise<StatistiquesResponse> {
  const query = buildQuery({ annee_univ });
  const response = await fetch(`${API_BASE}/surveillances/statistiques?${query}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to fetch statistiques");
  }
  return response.json();
}

export async function getEnseignantDisponibilites(
  enseignantId: number,
  dateDebut: string,
  dateFin: string,
): Promise<GetDisponibilitesResponse> {
  const query = buildQuery({ date_debut: dateDebut, date_fin: dateFin });
  const response = await fetch(
    `${API_BASE}/surveillances/enseignant/${enseignantId}/disponibilites?${query}`,
    { cache: "no-store" },
  );
  if (!response.ok) {
    throw new Error("Failed to fetch disponibilites");
  }
  return response.json();
}

export async function createDisponibilite(
  payload: DisponibiliteEnseignantCreatePayload,
): Promise<DisponibiliteEnseignant> {
  const response = await fetch(`${API_BASE}/surveillances/disponibilites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create disponibilite");
  }
  return response.json();
}

export async function getEnseignantSurveillances(
  enseignantId: number,
  filters: { annee_universitaire?: string; semestre?: number; type_epreuve?: string } = {},
): Promise<Record<string, unknown>> {
  const query = buildQuery(filters);
  const url = query
    ? `${API_BASE}/surveillances/enseignant/${enseignantId}/toutes-surveillances?${query}`
    : `${API_BASE}/surveillances/enseignant/${enseignantId}/toutes-surveillances`;
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch enseignant surveillances");
  }
  return response.json();
}
