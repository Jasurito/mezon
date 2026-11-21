"use client";
import { useLocale, useTranslations } from "next-intl";
import { ErrorState, Loading, PageTitle } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { api, type DashboardOut } from "@/lib/api";
import { isUnknownUser, useUser } from "@/store/user";
import { useLoad } from "@/hooks/use-load";

const fmt = (iso: string) => new Date(iso).toLocaleDateString(undefined, { day: "2-digit", month: "2-digit", year: "numeric" });

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const tr = useTranslations("results");
  const nav = useTranslations("nav");
  const common = useTranslations("common");
  const locale = useLocale();
  const { userId, account, ready } = useUser();
  // an unknown guest id (e.g. after a database reset) means "no progress yet", not an error
  const { data: d, error: failed, retry: load } = useLoad<DashboardOut>(
    userId ? () => api.dashboard(userId, locale).catch((e) => { if (isUnknownUser(e)) useUser.getState().dropGuest(); throw e; }) : null,
    [userId, locale],
  );

  if (!ready) return <Loading />;
  if (!userId || (d && d.completed.length === 0)) {
    return (
      <>
        <PageTitle title={t("title")} />
        <div className="rounded-lg border border-hairline bg-navy-2 p-8 text-center">
          <p className="text-lg">{t("empty")}</p>
          <Button asChild size="lg" className="mt-5 h-11 px-5"><Link href="/cases">{t("chooseCase")}</Link></Button>
        </div>
      </>
    );
  }
  if (failed) return <ErrorState onRetry={load} />;
  if (!d) return <Loading />;
  const level = d.knowledge_level.score;
  return (
    <>
      <PageTitle title={t("title")} />
      {!account && <p className="mb-8 rounded-md border border-hairline bg-gold/10 px-4 py-3">{t("guestNote")} <Link href="/auth/sign-up?next=/dashboard" className="font-semibold text-gold">{nav("signUp")}</Link></p>}
      <div className="grid gap-6 lg:grid-cols-3">
        <section className="rounded-lg border border-hairline bg-navy-2 p-6" aria-labelledby="lvl">
          <h2 id="lvl" className="text-sm font-semibold text-ink-muted">{t("level")}</h2>
          <div className="mt-4 flex items-center gap-5">
            <div className="grid size-28 place-items-center rounded-full" style={{ background: `conic-gradient(var(--gold) ${(level ?? 0) * 3.6}deg, rgb(245 241 232 / .1) 0)` }}>
              <div className="grid size-22 place-items-center rounded-full bg-navy-2"><span className="num text-3xl text-gold">{level ?? "–"}</span></div>
            </div>
            <p className="text-xl font-bold">{level === null ? t("levelNone") : d.knowledge_level.label}</p>
          </div>
        </section>

        <section className="rounded-lg border border-hairline bg-navy-2 p-6" aria-labelledby="gain">
          <h2 id="gain" className="text-sm font-semibold text-ink-muted">{t("gain")}</h2>
          {d.learning_gain.length === 0 ? <p className="mt-4 text-ink-muted">—</p> : d.learning_gain.map((g) => (
            <div key={g.scenario_id} className="mt-4">
              {([["pre", g.pre], ["post", g.post]] as const).map(([k, v]) => (
                <div key={k} className="mb-2 grid grid-cols-[4rem_1fr_3rem] items-center gap-3 text-sm">
                  <span className="text-ink-muted">{t(k)}</span>
                  <span className="h-3 rounded-sm bg-paper/10"><span className="block h-full rounded-sm" style={{ width: `${(v / g.max) * 100}%`, background: k === "pre" ? "var(--muted-ink)" : "var(--teal)" }} /></span>
                  <span className="tabular-nums">{v}/{g.max}</span>
                </div>
              ))}
              <p className="text-xs text-ink-muted">{t("gainNote")}</p>
            </div>
          ))}
        </section>

        <section className="rounded-lg border border-hairline bg-navy-2 p-6" aria-labelledby="mis">
          <h2 id="mis" className="text-sm font-semibold text-ink-muted">{t("mistakes")}</h2>
          <ul className="mt-4 grid gap-2">
            {d.mistake_categories.length === 0 ? <li className="text-teal">{tr("noMistakes")}</li> : d.mistake_categories.map((m) => (
              <li key={m.category} className="flex justify-between gap-3"><span>{tr(`category_${m.category}` as "category_evidence")}</span><span className="num text-terra">{m.count}</span></li>
            ))}
          </ul>
        </section>
      </div>

      <section className="mt-10" aria-labelledby="done">
        <h2 id="done" className="mb-4 text-xl font-bold">{t("completed")}</h2>
        <ul className="grid gap-2">
          {d.completed.map((c) => (
            <li key={c.session_id}>
              <Link href={`/results/${c.session_id}`} className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-md border border-paper/10 px-4 py-3 no-underline hover:border-gold sm:grid-cols-[1fr_auto_auto]">
                <span><span className="block font-semibold">{c.title}</span><span className="text-sm text-ink-muted">{c.outcome_title}</span></span>
                <span className="num text-lg text-gold">{c.score}/{c.max_score}</span>
                <span className="hidden text-sm text-ink-muted sm:block">{fmt(c.finished_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      {d.recommended.length > 0 && <section className="mt-10" aria-labelledby="rec">
        <h2 id="rec" className="mb-4 text-xl font-bold">{t("recommended")}</h2>
        <ul className="grid gap-3 md:grid-cols-3">
          {d.recommended.map((c) => (
            <li key={c.scenario_id} className="rounded-md border border-paper/10 p-4 opacity-80">
              <span className="block text-sm text-ink-muted">{c.category}</span>
              <span className="block font-semibold">{c.title}</span>
              {!c.available && <span className="text-sm text-ink-muted">{common("comingSoon")}</span>}
            </li>
          ))}
        </ul>
      </section>}
    </>
  );
}
