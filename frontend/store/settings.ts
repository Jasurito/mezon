"use client";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { applySettings, DEFAULT_SETTINGS, SETTINGS_KEY, type Settings } from "@/lib/settings";

interface SettingsStore extends Settings { set: (patch: Partial<Settings>) => void; reset: () => void }

export const useSettings = create<SettingsStore>()(
  persist(
    (set, get) => ({
      ...DEFAULT_SETTINGS,
      set: (patch) => { set(patch); applySettings({ ...get(), ...patch }); },
      reset: () => { set(DEFAULT_SETTINGS); applySettings(DEFAULT_SETTINGS); },
    }),
    { name: SETTINGS_KEY, partialize: ({ family, size, lineHeight, motion }) => ({ family, size, lineHeight, motion }) },
  ),
);
