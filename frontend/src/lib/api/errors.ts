/** Shared API error parsing and fetch wrapper. */

export class ApiError extends Error {
  readonly status?: number;
  readonly constraints: string[];

  constructor(message: string, options?: { status?: number; constraints?: string[] }) {
    super(message);
    this.name = "ApiError";
    this.status = options?.status;
    this.constraints = options?.constraints ?? [];
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

function parseDetailValue(detail: unknown): { message: string; constraints: string[] } {
  if (typeof detail === "string") {
    const constraints = detail.includes(" | ")
      ? detail.split(" | ").map((part) => part.trim()).filter(Boolean)
      : detail.trim()
        ? [detail.trim()]
        : [];
    return {
      message: constraints[0] ?? detail,
      constraints,
    };
  }

  if (Array.isArray(detail)) {
    const constraints = detail.map((item) => {
      if (typeof item === "string") {
        return item;
      }
      if (item && typeof item === "object") {
        const record = item as { msg?: string; message?: string; loc?: unknown[] };
        const loc = Array.isArray(record.loc) ? record.loc.join(".") : "";
        const msg = record.msg ?? record.message ?? JSON.stringify(item);
        return loc ? `${loc}: ${msg}` : msg;
      }
      return String(item);
    });
    return {
      message: constraints.join("\n"),
      constraints,
    };
  }

  return { message: "Erreur API", constraints: [] };
}

export async function parseApiErrorResponse(
  response: Response,
  fallbackMessage: string,
): Promise<ApiError> {
  let body: unknown = null;
  try {
    body = await response.json();
  } catch {
    // ignore non-json body
  }

  const detail =
    body && typeof body === "object" && "detail" in body
      ? (body as { detail: unknown }).detail
      : undefined;

  const parsed = parseDetailValue(detail ?? fallbackMessage);

  return new ApiError(parsed.message || fallbackMessage, {
    status: response.status,
    constraints: parsed.constraints.length > 0 ? parsed.constraints : [parsed.message],
  });
}

export async function apiFetch(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new ApiError(
        "Impossible de joindre l'API. Verifiez que le backend est demarre (uvicorn sur http://localhost:8000).",
      );
    }
    throw error;
  }
}

export async function handleApiResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    throw await parseApiErrorResponse(response, fallbackMessage);
  }
  return response.json() as Promise<T>;
}
