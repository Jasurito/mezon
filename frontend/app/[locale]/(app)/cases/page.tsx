"use client";
import { useLocale, useTranslations } from "next-intl";
import { useState, useSyncExternalStore } from "react";
import { ErrorState, Loading, PageTitle } from "@/components/common/state";
import { Badge } from "@/components/ui/badge";
import { Link } from "@/i18n/navigation";
import { api, type CaseKind, type ScenarioCard } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useLoad } from "@/hooks/use-load";

type KindTab = "all" | CaseKind;
const TABS: KindTab[] = ["all", "situation", "court"];

/** "#track-situation" (links from the home page) preselects a tab; read without a hydration mismatch */
const onHash = (cb: () => void) => { window.addEventListener("hashchange", cb); return () => window.removeEventListener("hashchange", cb); };
const hashKind = (): KindTab => {
  const m = /^#track-(situation|court)$/.exec(window.location.hash);
  return (m?.[1] as CaseKind | undefined) ?? "all";
};

export default function CasesPage() {
  const t = useTranslations();
  const locale = useLocale();
  const { data: cards, error: failed, retry: load } = useLoad<ScenarioCard[]>(() => api.scenarios(locale), [locale]);
  const fromHash = useSyncExternalStore(onHash, hashKind, () => "all" as KindTab);
  const [picked, setPicked] = useState<KindTab | null>(null);
  const [topic, setTopic] = useState<string | null>(null);
  const kind = picked ?? fromHash;

  const all = cards ?? [];
  const kindOf = (c: ScenarioCard): CaseKind => c.kind ?? "court";
  const count = (k: KindTab) => (k === "all" ? all.length : all.filter((c) => kindOf(c) === k).length);
  const byKind = kind === "all" ? all : all.filter((c) => kindOf(c) === kind);
  const topics = [...new Set(byKind.map((c) => c.category))];
  const shown = topic && topics.includes(topic) ? byKind.filter((c) => c.category === topic) : byKind;

  function chooseKind(k: KindTab) {
    setPicked(k); setTopic(null);
    window.history.replaceState(window.history.state, "", k === "all" ? window.location.pathname : `#track-${k}`);
  }

  return (
    <>
      <PageTitle title={t("cases.title")} lead={t("cases.lead")} />
      {failed ? <ErrorState onRetry={load} /> : !cards ? <Loading /> : (
        <div>
          {/* filters: category tabs, then topic chips for the cases in that category */}
          <div role="tablist" aria-label={t("cases.filterKind")} className="flex flex-wrap gap-2 border-b border-hairline pb-3">
            {TABS.map((k) => (
              <button key={k} type="button" role="tab" aria-selected={kind === k} aria-controls="case-grid" onClick={() => chooseKind(k)}
                className="flex min-h-11 items-center gap-2 rounded-md px-4 font-semibold text-ink-muted hover:bg-navy-2 hover:text-paper aria-selected:bg-gold aria-selected:text-navy">
                {t(`cases.tab_${k}`)}<span className="num rounded bg-black/15 px-1.5 py-0.5 text-xs">{count(k)}</span>
              </button>
            ))}
          </div>
          {topics.length > 1 && (
            <div role="group" aria-label={t("cases.filterTopic")} className="mt-3 flex flex-wrap gap-2">
              {[null, ...topics].map((tp) => (
                <button key={tp ?? "all"} type="button" aria-pressed={(topic ?? null) === tp} onClick={() => setTopic(tp)}
                  className="min-h-9 rounded-full border border-paper/20 px-3 text-sm hover:border-gold aria-pressed:border-gold aria-pressed:bg-gold/15 aria-pressed:text-gold">
                  {tp ?? t("cases.allTopics")}
                </button>
              ))}
            </div>
          )}
          {kind !== "all" && <p className="mt-4 max-w-[62ch] text-ink-muted">{t(`cases.track_${kind}_lead`)}</p>}

          <ul id="case-grid" role="tabpanel" className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {shown.map((c) => {
              const body = (
                <>
                  <span className="flex items-center justify-between gap-2 text-sm text-ink-muted">
                    <span>{c.category}</span>
                    <span className={cn("rounded-sm border px-1.5 py-0.5 text-xs", kindOf(c) === "situation" ? "border-teal/50 text-teal" : "border-gold/50 text-gold")}>{t(`cases.kind_${kindOf(c)}`)}</span>
                  </span>
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
                <li key={c.scenario_id} className="fade-in">
                  {c.available ? (
                    <Link href={`/cases/${c.scenario_id}`} className="flex h-full flex-col gap-1.5 rounded-lg border border-gold bg-navy-3 p-6 no-underline hover:bg-[#24395c]">{body}</Link>
                  ) : (
                    <div aria-disabled className="flex h-full flex-col gap-1.5 rounded-lg border border-paper/10 p-6 opacity-70">{body}</div>
                  )}
                </li>
              );
            })}
          </ul>
          {shown.length === 0 && <p className="mt-6 text-ink-muted">{t("cases.empty")}</p>}
        </div>
      )}
    </>
  );
}
