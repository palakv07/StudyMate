/**
 * API client — talks to FastAPI on port 8000.
 * Set VITE_API_URL in frontend/.env.development (default: direct backend URL).
 */

const BASE =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";


async function apiFetch(path: string, init?: RequestInit) {
  const url = `${BASE}${path}`;
  try {
    const res = await fetch(url, init);
    return res;
  } catch {
    throw new Error(
      `Cannot reach backend at ${BASE}. Start it: open backend/start_backend.bat`
    );
  }
}

export type Problem = {
  problem: string;
  topic: string;
  difficulty: string;
  status: string;
  time_taken: number | string;
  weakness_score: number | string;
  date_solved?: string;
};

export type SolvePayload = {
  problem: string;
  topic: string;
  difficulty: string;
  time_taken: number;
};

export async function markSolved(payload: SolvePayload) {
  const res = await apiFetch("/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = err.detail;
    const msg =
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).join(", ")
          : res.statusText;
    throw new Error(msg || "Request failed");
  }
  return res.json();
}

export async function fetchRecommendations() {
  const res = await apiFetch("/recommend");
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const detail = typeof err.detail === "string" ? err.detail : "Failed to load recommendations";
    throw new Error(detail);
  }
  return res.json();
}

export async function fetchStats() {
  const res = await apiFetch("/stats");
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}

export async function fetchProblems(): Promise<Problem[]> {
  const res = await apiFetch("/problems");
  if (!res.ok) throw new Error("Failed to load problems");
  const data = await res.json();
  return data.problems || [];
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await apiFetch("/health");
    return res.ok;
  } catch {
    return false;
  }
}

export async function getCalendarAuthUrl() {
  const res = await apiFetch("/calendar/auth_url");
  if (!res.ok) throw new Error("Failed to get calendar auth url");
  return res.json();
}

export async function getCalendarStatus() {
  const res = await apiFetch("/calendar/status");
  if (!res.ok) throw new Error("Failed to get calendar status");
  return res.json();
}

export async function scheduleCalendar(items: any[]) {
  const res = await apiFetch("/calendar/schedule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to schedule events");
  }
  return res.json();
}
