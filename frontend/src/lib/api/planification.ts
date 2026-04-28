import type {
  Planification,
  PlanificationCreatePayload,
} from "@/lib/types/planification";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function getPlanifications(): Promise<Planification[]> {
  const response = await fetch(`${API_BASE}/planifications/`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch planifications");
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
