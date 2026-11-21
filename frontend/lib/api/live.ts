/**
 * Real backend client (FastAPI, same origin under /api via nginx). Enabled with NEXT_PUBLIC_API_MODE=live.
 * Replace with the generated openapi-fetch client once `make api-client` is wired.
 */
import { ApiError, type Api, type Locale, type MentorEvent } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

async function call<T>(path: string, init: RequestInit & { query?: Record<string, string | undefined> } = {}): Promise<T> {
  const url = new URL(BASE + "/api" + path, typeof window === "undefined" ? "http://localhost" : window.location.origin);
  for (const [k, v] of Object.entries(init.query ?? {})) if (v != null) url.searchParams.set(k, v);
  const res = await fetch(url, { ...init, credentials: "include", headers: { "Content-Type": "application/json", ...init.headers } });
  if (res.status === 202 || res.status === 204) return undefined as T;
  const body = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, body?.error?.code ?? "HTTP_" + res.status, body?.error?.message ?? res.statusText, body?.error?.details);
  return body as T;
}
const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

async function* sse(res: Response): AsyncGenerator<MentorEvent> {
  const reader = res.body!.pipeThrough(new TextDecoderStream()).getReader();
  let buf = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buf += value;
    let i: number;
    while ((i = buf.indexOf("\n\n")) >= 0) {
      const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
      const event = /^event: (.+)$/m.exec(chunk)?.[1];
      const data = chunk.split("\n").filter((l) => l.startsWith("data: ")).map((l) => l.slice(6)).join("\n");
      if (event && data) yield { event, data: JSON.parse(data) } as MentorEvent;
    }
  }
}

export const liveApi: Api = {
  health: () => call("/health"),
  createUser: (display_name = null) => call("/users", post({ display_name })),
  dashboard: (id, locale) => call(`/users/${id}/dashboard`, { query: { locale } }),
  scenarios: (locale) => call("/scenarios", { query: { locale } }),
  scenario: (id, locale) => call(`/scenarios/${id}`, { query: { locale } }),
  quiz: (id, kind, locale) => call(`/quiz/${id}`, { query: { kind, locale } }),
  submitQuiz: (id, body, locale) => call(`/quiz/${id}/attempts`, { ...post(body), query: { locale } }),
  createSession: (body) => call("/sessions", post(body)),
  session: (id, locale?: Locale) => call(`/sessions/${id}`, { query: { locale } }),
  setSessionLocale: (id, locale) => call(`/sessions/${id}`, { method: "PATCH", body: JSON.stringify({ locale }) }),
  act: (id, action_id, params) => call(`/sessions/${id}/actions`, post({ action_id, params: params ?? null })),
  askNpc: (id, character, text) => call(`/sessions/${id}/npc/${encodeURIComponent(character)}/ask`, post({ text })),
  result: (id, locale) => call(`/sessions/${id}/result`, { query: { locale } }),
  citation: (id, date, locale) => call(`/legal/citations/${id}`, { query: { date: date ?? undefined, locale } }),
  document: async () => [], // TODO(backend): endpoint for evidence document bodies
  async *mentor(body, signal) {
    const res = await fetch(BASE + "/api/mentor/ask", { method: "POST", body: JSON.stringify(body), signal, credentials: "include", headers: { "Content-Type": "application/json", Accept: "text/event-stream" } });
    if (!res.ok || !res.body) { yield { event: "error", data: { code: "HTTP_" + res.status, message: res.statusText } }; return; }
    yield* sse(res);
  },
  events: (body) => call("/events", post(body)),
};
