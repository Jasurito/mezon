"use client";
import { useTranslations } from "next-intl";

/** Review-only pill linking back to the two reference sketches (kept on 1.modeus.cc and 2.modeus.cc). */
export function SketchSwitcher() {
  const t = useTranslations("nav");
  if (process.env.NEXT_PUBLIC_SHOW_SKETCHES === "false") return null;
  return (
    <nav aria-label={t("sketches")} className="fixed bottom-3 left-3 z-40 flex items-center gap-1 rounded-full bg-[#141418]/85 p-1.5 text-xs font-semibold text-white backdrop-blur">
      <span className="px-2 opacity-75">{t("sketches")}</span>
      {[1, 2].map((n) => (
        <a key={n} href={`https://${n}.modeus.cc/`} className="grid h-7 min-w-7 place-items-center rounded-full px-2 text-white no-underline hover:bg-white/20">{n}</a>
      ))}
    </nav>
  );
}
