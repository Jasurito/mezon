"use client";
import { create } from "zustand";

interface UiStore {
  legal: { id: string; date: string | null } | null;
  openLegal: (id: string, date?: string | null) => void;
  closeLegal: () => void;
}
export const useUi = create<UiStore>()((set) => ({
  legal: null,
  openLegal: (id, date = null) => set({ legal: { id, date } }),
  closeLegal: () => set({ legal: null }),
}));
