import type {
  Surveillance,
  SurveillanceCreatePayload,
  TeacherCharge,
} from "@/lib/types/surveillance";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export async function getSurveillances(): Promise<Surveillance[]> {
  const response = await fetch(`${API_BASE}/surveillances/`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch surveillances");
  }
  return response.json();
}

export async function createSurveillance(
  payload: SurveillanceCreatePayload,
): Promise<Surveillance> {
  const response = await fetch(`${API_BASE}/surveillances/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create surveillance");
  }
  return response.json();
}

export async function getTeacherCharges(): Promise<TeacherCharge> {
  const response = await fetch(`${API_BASE}/surveillances/charges`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Failed to fetch charges");
  }
  return response.json();
}
