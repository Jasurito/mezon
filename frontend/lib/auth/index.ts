/**
 * Account service. The backend owns auth (backend/app/api/auth.py): Google OAuth (PKCE) + email/password,
 * an httpOnly `mezon_session` cookie on the same origin, CSRF = Origin check (same origin, so nothing to send).
 *   GET  /api/auth/google/start?next=/dashboard&guest_user_id=…  -> 302 to Google -> /api/auth/google/callback
 *        -> 302 to next, or to /?auth_error=google on any failure (shown by <AuthErrorNotice/>)
 *   POST /api/auth/signup  {display_name, email, password, guest_user_id}  -> AccountUser | 409 EMAIL_EXISTS
 *   POST /api/auth/login   {email, password, guest_user_id}                -> AccountUser | 401 INVALID_CREDENTIALS
 *   POST /api/auth/logout  -> 204
 *   GET  /api/auth/me      -> AccountUser | 401
 * 429 RATE_LIMITED (Retry-After), 422 validation. Guest progress (guest_user_id) moves to the account on sign-in.
 * Mock mode keeps accounts in localStorage (demo only, never real credentials).
 */
import { API_MODE } from "@/lib/api";
import { mergeMockGuest } from "@/lib/api/mock";

export interface AccountUser { id: string; display_name: string; email: string; provider: "google" | "email"; avatar_url?: string | null }
export type AuthErrorCode = "credentials" | "exists" | "rate_limited" | "invalid" | "network";
/** Live mode shows "Continue with Google" only when the server has Google credentials (NEXT_PUBLIC_GOOGLE_AUTH=true). */
export const GOOGLE_ENABLED = API_MODE === "mock" || process.env.NEXT_PUBLIC_GOOGLE_AUTH === "true";
export class AuthError extends Error { constructor(public code: AuthErrorCode) { super(code); } }

export interface AuthService {
  me(): Promise<AccountUser | null>;
  signIn(email: string, password: string, guestUserId: string | null): Promise<AccountUser>;
  signUp(name: string, email: string, password: string, guestUserId: string | null): Promise<AccountUser>;
  /** Real mode redirects the browser to Google; mock mode resolves with a demo account. */
  google(next: string, guestUserId: string | null): Promise<AccountUser | void>;
  signOut(): Promise<void>;
}

const K_USERS = "mezon.auth.users", K_ME = "mezon.auth.me";
const read = <T,>(k: string, d: T): T => { try { return JSON.parse(localStorage.getItem(k) || "null") ?? d; } catch { return d; } };
const write = (k: string, v: unknown) => localStorage.setItem(k, JSON.stringify(v));
const wait = (ms = 450) => new Promise((r) => setTimeout(r, ms));
async function hash(s: string) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode("mezon-demo:" + s));
  return Array.from(new Uint8Array(buf), (b) => b.toString(16).padStart(2, "0")).join("");
}

const mockAuth: AuthService = {
  async me() { return read<AccountUser | null>(K_ME, null); },
  async signIn(email, password, guest) {
    await wait(); const users = read<Record<string, AccountUser & { pw: string }>>(K_USERS, {});
    const u = users[email.toLowerCase()];
    if (!u || u.pw !== (await hash(password))) throw new AuthError("credentials");
    const me: AccountUser = { id: u.id, display_name: u.display_name, email: u.email, provider: u.provider };
    mergeMockGuest(guest, me.id); write(K_ME, me); return me;
  },
  async signUp(name, email, password, guest) {
    await wait(); const users = read<Record<string, AccountUser & { pw: string }>>(K_USERS, {});
    const key = email.toLowerCase(); if (users[key]) throw new AuthError("exists");
    const me: AccountUser = { id: crypto.randomUUID(), display_name: name.trim(), email: key, provider: "email" };
    users[key] = { ...me, pw: await hash(password) }; write(K_USERS, users);
    mergeMockGuest(guest, me.id); write(K_ME, me); return me;
  },
  async google(_next, guest) {
    await wait(700);
    const me: AccountUser = { id: "google-demo", display_name: "Demo Google", email: "demo@example.com", provider: "google" };
    mergeMockGuest(guest, me.id); write(K_ME, me); return me;
  },
  async signOut() { localStorage.removeItem(K_ME); },
};

/** same origin in production (nginx); `make dev-all` points it at the local backend */
const AUTH_BASE = (process.env.NEXT_PUBLIC_API_BASE ?? "") + "/api/auth";

async function req<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(AUTH_BASE + path, { method: body ? "POST" : "GET", credentials: "include", headers: { "Content-Type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  if (res.status === 401) throw new AuthError("credentials");
  if (res.status === 409) throw new AuthError("exists");
  if (res.status === 429) throw new AuthError("rate_limited");
  if (res.status === 422) throw new AuthError("invalid");
  if (!res.ok) throw new AuthError("network");
  return res.status === 204 ? (undefined as T) : res.json();
}
const liveAuth: AuthService = {
  async me() { try { return await req<AccountUser>("/me"); } catch { return null; } },
  signIn: (email, password, guest_user_id) => req("/login", { email, password, guest_user_id }),
  signUp: (display_name, email, password, guest_user_id) => req("/signup", { display_name, email, password, guest_user_id }),
  async google(next, guest) {
    const q = new URLSearchParams({ next, ...(guest ? { guest_user_id: guest } : {}) });
    // full navigation on purpose: /api/* is the backend (OAuth redirect), not a Next.js page
    window.location.assign(AUTH_BASE + "/google/start?" + q);
  },
  signOut: () => req("/logout", {}),
};

export const auth: AuthService = API_MODE === "live" ? liveAuth : mockAuth;
