"use client";
import { Settings } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Link, usePathname } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import { AccountArea } from "./account-menu";
import { LanguageSwitcher } from "./language-switcher";

/** App header (night theme). The landing uses DeskHeader instead. */
export function SiteHeader({ className }: { className?: string }) {
  const t = useTranslations();
  const pathname = usePathname();
  const nav = [
    { href: "/cases", label: t("nav.cases") },
    { href: "/dashboard", label: t("nav.dashboard") },
  ] as const;
  return (
    <header className={cn("border-b border-hairline", className)}>
      <a href="#main" className="sr-only-focusable fixed left-4 top-2 z-50 rounded bg-paper px-3 py-2 text-navy">{t("common.skipToContent")}</a>
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
        <Link href="/" className="font-extrabold uppercase tracking-[0.32em] text-gold no-underline">{t("common.brand")}</Link>
        <nav aria-label={t("nav.cases")} className="flex gap-1">
          {nav.map((n) => (
            <Link key={n.href} href={n.href} aria-current={pathname.startsWith(n.href) ? "page" : undefined}
              className="rounded px-2 py-1.5 text-ink-muted no-underline hover:text-paper aria-[current=page]:text-paper">{n.label}</Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <LanguageSwitcher />
          <Button asChild variant="ghost" size="icon" aria-label={t("nav.settings")} title={t("nav.settings")}>
            <Link href="/settings"><Settings /></Link>
          </Button>
          <AccountArea />
        </div>
      </div>
    </header>
  );
}

export function SiteFooter() {
  const t = useTranslations("common");
  return (
    <footer className="mx-auto mt-20 flex max-w-6xl flex-wrap justify-between gap-2 border-t border-paper/10 px-4 pb-20 pt-6 text-sm text-ink-muted sm:px-6">
      <p>{t("disclaimer")}</p>
      <p>LexHackathon 2026</p>
    </footer>
  );
}
