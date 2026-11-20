"use client";
import { useLocale, useTranslations } from "next-intl";
import { ErrorState, Loading, PageTitle } from "@/components/common/state";
import { Badge } from "@/components/ui/badge";
import { Link } from "@/i18n/navigation";
import { api, type ScenarioCard } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useLoad } from "@/hooks/use-load";

export default function CasesPage() {
  const t = useTranslations();
  const locale = useLocale();
  const { data: cards, error: failed, retry: load } = useLoad<ScenarioCard[]>(() => api.scenarios(locale), [locale]);

  return (
    <>
      <PageTitle title={t("cases.title")} lead={t("cases.lead")} />
      {failed ? <ErrorState onRetry={load} /> : !cards ? <Loading /> : (
        <ul className="grid gap-4 md:grid-cols-[1.6fr_1fr_1fr_1fr]">
          {cards.map((c) => {
            const body = (
              <>
                <span className="text-sm text-ink-muted">{c.category}</span>
                <span className={cn("font-bold", c.available ? "text-3xl" : "text-xl")}>{c.title}</span>
                <span className="text-sm text-ink-muted">
                  {c.available ? `${t("common.minutes", { count: c.minutes })}, ${t(`common.difficulty_${c.difficulty}`)}` : t("common.comingSoon")}
                </span>
                {c.available && (
                  <span className="mt-2 flex flex-wrap gap-1.5">{c.topics.map((tp) => <Badge key={tp} variant="secondary">{tp}</Badge>)}</span>
                )}
                {c.available && <span className="mt-auto pt-5 font-semibold text-gold">{t("cases.start")}</span>}
              </>
            );
            return (
              <li key={c.scenario_id}>
                {c.available ? (
                  <Link href={`/cases/${c.scenario_id}`} className="flex h-full flex-col gap-1.5 rounded-lg border border-gold bg-navy-3 p-6 no-underline hover:bg-[#24395c]">{body}</Link>
                ) : (
                  <div aria-disabled className="flex h-full flex-col gap-1.5 rounded-lg border border-paper/10 p-6 opacity-70">{body}</div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
