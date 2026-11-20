"use client";
import { create } from "zustand";
import { api } from "@/lib/api";
import { auth, type AccountUser } from "@/lib/auth";

const GUEST_KEY = "mezon.user_id";

interface UserStore {
  /** Anonymous learner id (spec: UUID in localStorage). Kept after sign-in so guest progress is linked. */
  userId: string | null;
  account: AccountUser | null;
  ready: boolean;
  init: () => Promise<void>;
  ensureUser: () => Promise<string>;
  setAccount: (a: AccountUser | null) => void;
  signOut: () => Promise<void>;
}

let initPromise: Promise<void> | null = null;

export const useUser = create<UserStore>()((set, get) => ({
  userId: null, account: null, ready: false,
  init: () => (initPromise ??= (async () => {
    let id: string | null = null;
    try { id = localStorage.getItem(GUEST_KEY); } catch { /* storage blocked */ }
    const account = await auth.me().catch(() => null);
    set({ userId: id, account, ready: true });
  })()),
  ensureUser: async () => {
    await get().init();
    const existing = get().userId; if (existing) return existing;
    const { user_id } = await api.createUser(get().account?.display_name ?? null);
    try { localStorage.setItem(GUEST_KEY, user_id); } catch { /* ignore */ }
    set({ userId: user_id }); return user_id;
  },
  setAccount: (account) => set({ account }),
  signOut: async () => { await auth.signOut(); set({ account: null }); },
}));
