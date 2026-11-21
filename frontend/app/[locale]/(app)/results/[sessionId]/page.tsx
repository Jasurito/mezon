"use client";
import { Check, X } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { CitationChip, ErrorState, Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Link, useRouter } from "@/i18n/navigation";
import { api, type DecisionKind, type ResultKind, type SessionResult } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useUser } from "@/store/user";
import { useLoad } from "@/hooks/use-load";

/** stamp colour per outcome kind: green win, gold partial, paper settlement, red loss / left without consideration */
const STAMP: Record<ResultKind, string> = {
  win: "border-teal text-teal", partial: "border-gold text-gold", settlement: "border-paper text-paper",
  loss: "border-terra text-terra", procedural_loss: "border-terra text-terra",
};
const KINDS: ResultKind[] = ["win", "partial", "loss", "settlement", "procedural_loss"];
const DKINDS: DecisionKind[] = ["action", "reasoning", "prediction"];

const short = (id: string, locale: string) => { const n = id.split(".").pop(); return locale === "ru" ? `ст. ${n}` : `${n}-modda`; };

export default function ResultsPage() {
  const t = useTranslations("results");
  const nav = useTranslations("nav");
  const locale = useLocale();
  const router = useRouter();
  const { sessionId } = useParams<{ sessionId: string }>();
  const withUser = useUser((s) => s.withUser);
  // the result plus the case's legal date (article editions are shown as of that date)
  const { data, error: failed, retry: load } = useLoad<[SessionResult, string | null]>(
    () => Promise.all([api.result(sessionId, locale), api.session(sessionId, locale).then((s) => s.legal_date).catch(() => null)]),
    [sessionId, locale],
  );
  const [r, legalDate] = data ?? [null, null];

  async function replay() {
    const s = await withUser((user_id) => api.createSession({ user_id, scenario_id: r!.scenario_id, locale }));
    router.push(`/play/${s.session_id}`);
  }

  if (failed) return <ErrorState onRetry={load} />;
  if (!r) return <Loading />;
  const min = Math.floor(r.time_spent_sec / 60), sec = r.time_spent_sec % 60;
  // the label is ours (2026 Uzbek alphabet, same wording everywhere); unknown kinds fall back to the backend's text
  const kind = KINDS.includes(r.result_kind) ? r.result_kind : null;
  const label = kind ? t(`kind_${kind}`) : r.result_label;
  return (
    <article className="grid gap-10 lg:grid-cols-[1.5fr_1fr]">
      <div>
        <p className="text-ink-muted">{t("kicker")}</p>
        {label && (
          <p className={cn("result-stamp mt-4", STAMP[kind ?? "settlement"])}>
            <span className="sr-only">{t("resultLabel")}: </span>{label}
          </p>
        )}
        <h1 className="mt-3 text-4xl font-extrabold">{r.outcome_title}</h1>
        <p className="pix mt-3 text-5xl text-gold">{r.score}<span className="text-2xl text-ink-muted">/{r.max_score}</span></p>
        <p className="mt-2 text-ink-muted">{t("rate", { pct: Math.round(r.correct_decision_rate * 100) })}. {t("time", { min, sec })}</p>
        <p className="mt-5 border-l-4 border-gold bg-gold/10 px-4 py-3">{t("disclaimer")}</p>
        <p className="mt-5 max-w-[65ch]">{r.ruling_text}</p>

        <section className="mt-10" aria-labelledby="decisions">
          <h2 id="decisions" className="mb-4 text-xl font-bold">{t("decisions")}</h2>
          <ol className="relative grid gap-3 border-l border-hairline pl-6">
            {r.decisions.map((d) => (
              <li key={d.decision_id} className="relative">
                <span className={cn("absolute -left-[35px] top-1 grid size-5 place-items-center rounded-full", d.correct ? "bg-teal" : "bg-terra")} aria-hidden>
                  {d.correct ? <Check className="size-3 text-navy" /> : <X className="size-3 text-navy" />}
                </span>
                {d.kind && DKINDS.includes(d.kind) && (
                  <p className={cn("mb-1 inline-block rounded-sm border px-1.5 py-0.5 text-xs", d.kind === "action" ? "border-hairline text-gold" : "border-teal/50 text-teal")}>
                    {t(`dkind_${d.kind}`)}
                  </p>
                )}
                <p className="font-semibold">{d.chosen_label}<span className="sr-only">{d.correct ? " ✓" : " ✗"}</span></p>
                {!d.correct && <p className="text-sm text-ink-muted">{t("best")}: {d.best_label}.</p>}
                <p className="mt-1">{d.explanation}</p>
                {!d.correct && d.counterfactual && (
                  <div className="mt-2 rounded-md border-l-4 border-gold/70 bg-navy-2 px-3 py-2">
                    <p className="text-sm font-bold text-gold">{t("whatIf")}</p>
                    <p className="mt-0.5">{d.counterfactual}</p>
                  </div>
                )}
                <div className="mt-2 flex flex-wrap gap-2">{d.citation_ids.map((c) => <CitationChip key={c} id={c} label={short(c, locale)} date={legalDate} />)}</div>
              </li>
            ))}
          </ol>
        </section>

        <section className="mt-10" aria-labelledby="mistakes">
          <h2 id="mistakes" className="mb-4 text-xl font-bold">{t("mistakes")}</h2>
          {r.mistakes.length === 0 ? <p className="text-teal">{t("noMistakes")}</p> : (
            <ul className="grid gap-3">
              {r.mistakes.map((m, i) => (
                <li key={i} className="rounded-md border-l-4 border-terra bg-navy-2 p-4">
                  <p className="text-sm text-ink-muted">{t(`category_${m.category}` as "category_evidence")}</p>
                  <p className="font-semibold">{m.title}</p>
                  {m.correct_action && <p className="mt-1"><span className="text-ink-muted">{t("correctAction")}: </span>{m.correct_action}</p>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      <aside className="space-y-8 lg:pt-16">
        <div className="grid gap-2">
          <Button asChild size="lg" className="h-12 text-base"><Link href={`/mentor/${sessionId}`}>{t("askMentor")}</Link></Button>
          <Button asChild size="lg" variant="outline" className="h-12 text-base"><Link href={`/results/${sessionId}/posttest`}>{t("posttest")}</Link></Button>
          <div className="grid grid-cols-2 gap-2">
            <Button variant="ghost" size="lg" onClick={replay}>{t("replay")}</Button>
            <Button asChild variant="ghost" size="lg"><Link href="/dashboard">{nav("dashboard")}</Link></Button>
          </div>
        </div>
        <section aria-labelledby="norms">
          <h2 id="norms" className="mb-3 text-lg font-bold text-gold">{t("norms")}</h2>
          <ul className="grid gap-2">
            {r.citations.map((c) => (
              <li key={c.citation_id}><CitationChip id={c.citation_id!} label={`${short(c.citation_id!, locale)}, ${c.document_title}`} date={legalDate} /></li>
            ))}
          </ul>
        </section>
        {r.recommendations.length > 0 && (
          <section aria-labelledby="next">
            <h2 id="next" className="mb-3 text-lg font-bold text-gold">{t("next")}</h2>
            <ul className="grid gap-2">{r.recommendations.map((x) => <li key={x.topic}>{x.topic}</li>)}</ul>
          </section>
        )}
      </aside>
    </article>
  );
}
