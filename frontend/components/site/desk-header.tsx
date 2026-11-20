"use client";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { AccountArea } from "./account-menu";
import { LanguageSwitcher } from "./language-switcher";

/** Landing header in the case-file style (sketch 2): red index tab + typed links. */
export function DeskHeader() {
  const t = useTranslations();
  return (
    <header className="desk-top">
      <a href="#main" className="sr-only-focusable fixed left-4 top-2 z-50 rounded bg-white px-3 py-2 text-black">{t("common.skipToContent")}</a>
      <Link className="tab-logo" href="/">{t("common.brand")}</Link>
      <div className="desk-top__right">
        <Link className="desk-link" href="/cases">{t("nav.cases")}</Link>
        <Link className="desk-link" href="/dashboard">{t("nav.dashboard")}</Link>
        <Link className="desk-link" href="/settings">{t("nav.settings")}</Link>
        <LanguageSwitcher tone="desk" />
        <AccountArea tone="desk" />
      </div>
    </header>
  );
}
