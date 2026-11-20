"use client";
import { create } from "zustand";
import { api, ApiError, type GameEvent, type GameState, type Locale } from "@/lib/api";
import { useSettings } from "@/store/settings";

export interface CourtApi {
  talk(id: string, on: boolean): void;
  focus(id: string | null): void;
  react(id: string, kind: string): void;
  gavel(): void;
}

type Say = Extract<GameEvent, { type: "say" }>;

interface GameStore {
  sessionId: string | null;
  state: GameState | null;
  queue: GameEvent[];
  current: Say | null;
  typed: string;
  typing: boolean;
  waiting: boolean;
  busy: boolean;
  note: { citation_id: string; text: string } | null;
  toast: { title: string; key: number } | null;
  scorePop: { delta: number; key: number } | null;
  newEvidence: string[];
  error: "offline" | "load" | null;
  illegal: number;
  /** review_<doc> actions requested while the event queue was busy; sent when it drains */
  pending: string[];
  court: CourtApi | null;
  setCourt: (c: CourtApi | null) => void;
  load: (sid: string, locale: Locale) => Promise<void>;
  dispatch: (actionId: string, params?: { option?: string }) => Promise<void>;
  markReviewed: (evidenceId: string) => void;
  review: (evidenceId: string) => void;
  advance: () => void;
  next: () => void;
  reset: () => void;
}

let timer: ReturnType<typeof setInterval> | null = null;
const reduce = () => useSettings.getState().motion === "reduced";
const later = (fn: () => void, ms: number) => setTimeout(fn, reduce() ? 0 : ms);

export const useGame = create<GameStore>()((set, get) => {
  const finishTyping = () => {
    if (timer) { clearInterval(timer); timer = null; }
    const cur = get().current; if (!cur) return;
    get().court?.talk(cur.speaker, false);
    set({ typed: cur.text, typing: false, waiting: true });
  };

  return {
    sessionId: null, state: null, queue: [], current: null, typed: "", typing: false, waiting: false, busy: false,
    note: null, toast: null, scorePop: null, newEvidence: [], error: null, illegal: 0, pending: [], court: null,

    setCourt: (court) => set({ court }),

    load: async (sid, locale) => {
      if (timer) { clearInterval(timer); timer = null; }
      set({ sessionId: sid, error: null, busy: true, current: null, typed: "", waiting: false, note: null });
      try {
        const state = await api.session(sid, locale);
        set({ state, queue: [...state.events] });
        later(() => get().next(), 400);
      } catch (e) {
        set({ error: e instanceof ApiError && e.status === 404 ? "load" : "offline", busy: false });
      }
    },

    dispatch: async (actionId, params) => {
      const { sessionId, busy } = get(); if (!sessionId || busy) return;
      set({ busy: true, note: null });
      try {
        const state = await api.act(sessionId, actionId, params);
        set({ state, queue: [...get().queue, ...state.events], error: null });
        get().next();
      } catch (e) {
        if (e instanceof ApiError && e.status === 409) {
          set({ illegal: Date.now(), busy: false });
          const state = await api.session(sessionId).catch(() => null);
          if (state) set({ state });
        } else set({ error: "offline", busy: false });
      }
    },

    markReviewed: (id) => set({ newEvidence: get().newEvidence.filter((x) => x !== id) }),

    review: (id) => {
      const actionId = `review_${id}`;
      const { state, busy, pending } = get();
      if (!state?.available_actions.some((a) => a.action_id === actionId)) return;
      if (busy) { if (!pending.includes(actionId)) set({ pending: [...pending, actionId] }); return; }
      get().dispatch(actionId);
    },

    advance: () => {
      const { typing, waiting } = get();
      if (typing) return finishTyping();
      if (waiting) get().next();
    },

    next: () => {
      const { queue, court } = get();
      set({ waiting: false });
      const ev = queue[0];
      if (!ev) {
        court?.focus(null); set({ busy: false });
        const [first, ...rest] = get().pending;
        if (first) { set({ pending: rest }); if (get().state?.available_actions.some((a) => a.action_id === first)) get().dispatch(first); else get().next(); }
        return;
      }
      set({ queue: queue.slice(1) });
      switch (ev.type) {
        case "say": {
          court?.focus(ev.speaker); court?.talk(ev.speaker, true);
          set({ current: ev, typed: "", typing: true });
          if (reduce()) { finishTyping(); break; }
          let i = 0;
          timer = setInterval(() => { i += 1; if (i >= ev.text.length) finishTyping(); else set({ typed: ev.text.slice(0, i) }); }, 22);
          break;
        }
        case "react": if (ev.reaction === "gavel") court?.gavel(); else court?.react(ev.character, ev.reaction); later(() => get().next(), 350); break;
        case "stage_changed": set({ toast: { title: ev.title, key: Date.now() } }); later(() => get().next(), 700); break;
        case "score": set({ scorePop: { delta: ev.delta, key: Date.now() } }); later(() => get().next(), 300); break;
        case "legal_note": set({ note: { citation_id: ev.citation_id, text: ev.text } }); get().next(); break;
        case "evidence_added": set({ newEvidence: [...get().newEvidence, ev.evidence_id] }); get().next(); break;
        default: get().next();
      }
    },

    reset: () => { if (timer) { clearInterval(timer); timer = null; } set({ sessionId: null, state: null, queue: [], current: null, typed: "", busy: false, note: null, newEvidence: [], pending: [], error: null }); },
  };
});
