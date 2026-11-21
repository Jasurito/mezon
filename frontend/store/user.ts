"use client";
import { create } from "zustand";
import { api, API_MODE, ApiError } from "@/lib/api";
import { auth, PENDING_AUDIENCE, type AccountUser, type Audience } from "@/lib/auth";

// separate keys: a guest id made by the in-browser mock means nothing to the real backend
const GUEST_KEY = API_MODE === "live" ? "mezon.live.user_id" : "mezon.user_id";

/** the backend does not know this learner id (e.g. a guest from before a database reset): 404 with details.user_id */
export const isUnknownUser = (e: unknown) =>
  e instanceof ApiError && e.status === 404 && !!(e.details as { user_id?: string } | null)?.user_id;

interface UserStore {
  /**
   * The learner id used in API calls: the account id when signed in, else the anonymous guest id
   * (spec: UUID in localStorage). On sign-in the backend moves the guest's sessions and quiz attempts
   * to the account, so the guest id is dropped; signing out starts a new guest.
   */
  userId: string | null;
  account: AccountUser | null;
  ready: boolean;
  init: () => Promise<void>;
  ensureUser: () => Promise<string>;
  /** run a call that needs the learner id; an unknown guest id is replaced by a new guest once */
  withUser: <T>(fn: (userId: string) => Promise<T>) => Promise<T>;
  /** forget a guest id the backend does not know (no-op when signed in) */
  dropGuest: () => void;
  setAccount: (a: AccountUser | null) => void;
  signOut: () => Promise<void>;
}

let initPromise: Promise<void> | null = null;
const forgetGuest = () => { try { localStorage.removeItem(GUEST_KEY); } catch { /* storage blocked */ } };

export const useUser = create<UserStore>()((set, get) => ({
  userId: null, account: null, ready: false,
  init: () => (initPromise ??= (async () => {
    let id: string | null = null;
    try { id = localStorage.getItem(GUEST_KEY); } catch { /* storage blocked */ }
    let account = await auth.me().catch(() => null);
    if (account) forgetGuest(); // back from Google: the server already merged the guest into the account
    // back from "Continue with Google" on the sign-up page: save the chosen audience on the new account
    let pending: string | null = null;
    try { pending = sessionStorage.getItem(PENDING_AUDIENCE); sessionStorage.removeItem(PENDING_AUDIENCE); } catch { /* storage blocked */ }
    if (account && !account.audience && (pending === "professional" || pending === "public")) {
      account = await auth.setAudience(account, pending as Audience).catch(() => account);
    }
    set({ userId: account?.id ?? id, account, ready: true });
  })()),
  ensureUser: async () => {
    await get().init();
    const existing = get().account?.id ?? get().userId; if (existing) return existing;
    const { user_id } = await api.createUser(get().account?.display_name ?? null);
    try { localStorage.setItem(GUEST_KEY, user_id); } catch { /* ignore */ }
    set({ userId: user_id }); return user_id;
  },
  withUser: async (fn) => {
    const id = await get().ensureUser();
    try { return await fn(id); } catch (e) {
      if (!isUnknownUser(e) || get().account) throw e;
      get().dropGuest();
      return fn(await get().ensureUser());
    }
  },
  dropGuest: () => { if (get().account) return; forgetGuest(); set({ userId: null }); },
  setAccount: (account) => {
    if (account) forgetGuest();
    set({ account, userId: account?.id ?? null });
  },
  signOut: async () => { await auth.signOut(); set({ account: null, userId: null }); },
}));
