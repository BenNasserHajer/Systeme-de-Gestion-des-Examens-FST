/**
 * API client for Salles (Rooms) CRUD operations
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface Salle {
  id: number;
  code: string;
  designation: string | null;
  capacite: number;
  batiment: string | null;
}

export interface SalleCreate {
  code: string;
  designation?: string | null;
  capacite: number;
  batiment?: string | null;
}

export interface SalleUpdate {
  code?: string;
  designation?: string | null;
  capacite?: number;
  batiment?: string | null;
}

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

/**
 * Get all salles
 */
export async function getSalles(params?: { skip?: number; limit?: number }): Promise<Salle[]> {
  const query = new URLSearchParams();
  if (params?.skip !== undefined) query.set("skip", params.skip.toString());
  if (params?.limit !== undefined) query.set("limit", params.limit.toString());
  
  const url = `${API_BASE}/salles${query.toString() ? `?${query}` : ""}`;
  const response = await fetch(url);
  return handleResponse<Salle[]>(response);
}

/**
 * Get a single salle by ID
 */
export async function getSalle(salleId: number): Promise<Salle> {
  const response = await fetch(`${API_BASE}/salles/${salleId}`);
  return handleResponse<Salle>(response);
}

/**
 * Create a new salle
 */
export async function createSalle(data: SalleCreate): Promise<Salle> {
  const response = await fetch(`${API_BASE}/salles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Salle>(response);
}

/**
 * Update an existing salle
 */
export async function updateSalle(salleId: number, data: SalleUpdate): Promise<Salle> {
  const response = await fetch(`${API_BASE}/salles/${salleId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  return handleResponse<Salle>(response);
}

/**
 * Delete a salle
 */
export async function deleteSalle(salleId: number): Promise<void> {
  const response = await fetch(`${API_BASE}/salles/${salleId}`, {
    method: "DELETE",
  });
  return handleResponse<void>(response);
}
