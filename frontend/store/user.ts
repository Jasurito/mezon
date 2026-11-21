"use client";
import { create } from "zustand";
import { api } from "@/lib/api";
import { auth, type AccountUser } from "@/lib/auth";

const GUEST_KEY = "mezon.user_id";

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
    const account = await auth.me().catch(() => null);
    if (account) forgetGuest(); // back from Google: the server already merged the guest into the account
    set({ userId: account?.id ?? id, account, ready: true });
  })()),
  ensureUser: async () => {
    await get().init();
    const existing = get().account?.id ?? get().userId; if (existing) return existing;
    const { user_id } = await api.createUser(get().account?.display_name ?? null);
    try { localStorage.setItem(GUEST_KEY, user_id); } catch { /* ignore */ }
    set({ userId: user_id }); return user_id;
  },
  setAccount: (account) => {
    if (account) forgetGuest();
    set({ account, userId: account?.id ?? null });
  },
  signOut: async () => { await auth.signOut(); set({ account: null, userId: null }); },
}));
