"use client";
import { useLocale, useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useTransition } from "react";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type Locale } from "@/i18n/routing";
import { cn } from "@/lib/utils";

export const LOCALE_LABELS: Record<Locale, { short: string; long: string }> = {
  "uz-Latn": { short: "Oʻz", long: "Oʻzbekcha" },
  "uz-Cyrl": { short: "Ўз", long: "Ўзбекча" },
  ru: { short: "Ru", long: "Русский" },
};

/** Switches the URL prefix; the play page additionally PATCHes the session (spec §7). */
export function LanguageSwitcher({ className, tone = "app" }: { className?: string; tone?: "app" | "desk" }) {
  const t = useTranslations("nav");
  const locale = useLocale();
  const pathname = usePathname();
  const params = useParams();
  const router = useRouter();
  const [pending, start] = useTransition();
  return (
    <div role="group" aria-label={t("language")} className={cn("flex items-center gap-0.5", pending && "opacity-60", className)}>
      {routing.locales.map((l) => (
        <button
          key={l}
          type="button"
          lang={l}
          title={LOCALE_LABELS[l].long}
          aria-pressed={l === locale}
          onClick={() => start(() => router.replace(
            // @ts-expect-error -- pathname + params of the current dynamic route are always valid
            { pathname, params }, { locale: l, scroll: false }))}
          className={cn(
            "min-h-9 rounded px-2 text-sm transition-colors",
            tone === "app" ? "text-ink-muted hover:text-paper aria-pressed:bg-paper/10 aria-pressed:text-paper"
              : "text-[#9aa3b8] hover:text-[#e4e7de] aria-pressed:text-[#e4e7de] aria-pressed:underline underline-offset-4",
          )}
        >
          {LOCALE_LABELS[l].short}
        </button>
      ))}
    </div>
  );
}
