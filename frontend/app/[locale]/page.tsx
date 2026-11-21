import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { use } from "react";
import { CaseDesk } from "@/components/site/case-desk";
import { DeskHeader } from "@/components/site/desk-header";
import { HomeGate } from "@/components/site/home-gate";
import { Pitch } from "@/components/site/pitch";
import type { Locale } from "@/i18n/routing";

export default function Landing({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  setRequestLocale(locale as Locale);
  const common = useTranslations("common");
  return (
    <div className="desk-page">
      <DeskHeader />
      {/* guests: what Mezon is and for whom; signed-in users: their case desk */}
      <div className="page-in"><HomeGate guest={<Pitch />} member={<CaseDesk />} /></div>
      <footer className="desk-foot">{common("disclaimer")} LexHackathon 2026.</footer>
    </div>
  );
}
