"use client";
import { useTranslations } from "next-intl";
import { CourtSnapshot } from "@/game/CourtSnapshot";
import { COURT_THEMES } from "@/lib/settings";
import { cn } from "@/lib/utils";
import { useSettings } from "@/store/settings";

/** Courtroom theme as picture cards (Settings); the choice is used by the game and the home page. */
export function ThemePicker() {
  const t = useTranslations("settings");
  const theme = useSettings((s) => s.courtTheme);
  const set = useSettings((s) => s.set);
  return (
    <div role="radiogroup" aria-label={t("theme")} className="grid gap-3 sm:grid-cols-2">
      {COURT_THEMES.map((id) => (
        <button key={id} type="button" role="radio" aria-checked={theme === id} onClick={() => set({ courtTheme: id })}
          className={cn("overflow-hidden rounded-md border-2 text-left transition-colors hover:border-gold/70", theme === id ? "border-gold" : "border-paper/15")}>
          <CourtSnapshot theme={id} alt={t(`theme_${id}`)} className="aspect-video w-full object-cover" />
          <span className={cn("block px-3 py-2 text-sm", theme === id ? "bg-gold font-semibold text-navy" : "bg-navy-2")}>{t(`theme_${id}`)}</span>
        </button>
      ))}
    </div>
  );
}
