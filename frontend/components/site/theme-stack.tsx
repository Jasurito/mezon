"use client";
import { useTranslations } from "next-intl";
import { Court } from "@/game/Court";
import { CourtSnapshot } from "@/game/CourtSnapshot";
import { COURT_THEMES } from "@/lib/settings";
import { useSettings } from "@/store/settings";

/**
 * Home page hero for guests: the chosen courtroom theme as a live photo, the other themes as photos stacked behind
 * it. A photo from the back comes to the front on click and becomes the user's theme (also used by the game).
 */
export function ThemeStack() {
  const t = useTranslations("pitch");
  const ts = useTranslations("settings");
  const front = useSettings((s) => s.courtTheme);
  const set = useSettings((s) => s.set);
  const back = COURT_THEMES.filter((id) => id !== front);
  return (
    <div>
      <div className="photo-stack">
        {back.map((id, i) => (
          <button key={id} type="button" className={`photo photo-stack__back photo-stack__back--${i}`} onClick={() => set({ courtTheme: id })}
            aria-label={t("showTheme", { theme: ts(`theme_${id}`) })}>
            <CourtSnapshot theme={id} alt="" className="photo__scene block w-full object-cover" />
            <span className="photo-stack__label">{ts(`theme_${id}`)}</span>
          </button>
        ))}
        <figure className="photo photo-stack__front">
          <span className="clip" aria-hidden />
          <Court mode="hero" theme={front} className="photo__scene" label={t("photoAlt")} />
          <figcaption>{t("photoCaptionTheme", { theme: ts(`theme_${front}`) })}</figcaption>
        </figure>
      </div>
      <p className="photo-stack__hint">{t("stackHint")}</p>
    </div>
  );
}
