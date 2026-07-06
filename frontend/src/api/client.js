export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export function parseMetrics(response) {
  const raw = response.headers.get("X-Search-Metrics");
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function parseErrorDetail(response) {
  const detail = await response.json().catch(() => null);
  return detail?.detail ?? `Error ${response.status} al procesar la búsqueda.`;
}
