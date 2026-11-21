"use client";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Link } from "@/i18n/navigation";
import { api, API_MODE, type HealthResponse, type Locale, type ScenarioCard, type ScenarioDetail } from "@/lib/api";

/*
 * The signed-in home page "desk" (spec FRONTEND.md §4.1): a case folder, the legal base and a shelf of other cases.
 * Live mode picks a random court case on every visit (any available case if there is no court case), shows its acts
 * (links to lex.uz) and the article count from /api/health; the shelf lists other real cases. Mock mode shows the
 * static demo content from the locale files.
 */
export interface Desk { card: ScenarioCard; num: number; detail: ScenarioDetail; health: HealthResponse | null; others: ScenarioCard[] }

const shuffle = <T,>(xs: T[]) => xs.map((x) => [Math.random(), x] as const).sort((a, b) => a[0] - b[0]).map(([, x]) => x);

async function loadDesk(locale: Locale): Promise<Desk | null> {
  const cards = await api.scenarios(locale);
  const open = cards.filter((c) => c.available);
  const courts = open.filter((c) => (c.kind ?? "court") === "court");
  const card = shuffle(courts.length ? courts : open)[0];
  if (!card) return null;
  const [detail, health] = await Promise.all([api.scenario(card.scenario_id, locale), api.health().catch(() => null)]);
  const others = shuffle(open.filter((c) => c.scenario_id !== card.scenario_id)).slice(0, 3);
  return { card, num: cards.indexOf(card) + 1, detail, health, others };
}

/** null: mock mode (static demo content) or the backend did not answer; undefined: still loading */
export function useDesk(): Desk | null | undefined {
  const locale = useLocale() as Locale;
  const [data, setData] = useState<{ locale: string; value: Desk | null } | null>(null);
  useEffect(() => {
    if (API_MODE !== "live") return;
    let live = true;
    loadDesk(locale).then((value) => { if (live) setData({ locale, value }); }, () => { if (live) setData({ locale, value: null }); });
    return () => { live = false; };
  }, [locale]);
  if (API_MODE !== "live") return null;
  return data?.locale === locale ? data.value : undefined;
}

const dmy = (iso: string) => iso.split("-").reverse().join(".");
const pad3 = (n: number) => String(n).padStart(3, "0");
/** "Представитель ООО «Ёркин Техно Савдо»" -> "ООО «Ёркин Техно Савдо»"; "“Yorqin Texno Savdo” MChJ vakili" -> "“Yorqin Texno Savdo” MChJ" */
const company = (role: string) => role.match(/(\S+\s)?[«“][^»”]+[»”](\s\S+)?/)?.[0]?.trim() ?? null;

export function CaseNumber({ desk }: { desk: Desk | null | undefined }) {
  const t = useTranslations("landing");
  return <div className="folder__tab">{t("caseNumber", { num: desk ? pad3(desk.num) : "001" })}</div>;
}

export function CaseCaption({ desk }: { desk: Desk | null | undefined }) {
  const t = useTranslations("landing");
  return <figcaption>{desk ? t("photoCaptionDate", { date: dmy(desk.detail.legal_date) }) : t("photoCaption")}</figcaption>;
}

export function CaseCover({ desk }: { desk: Desk | null | undefined }) {
  const t = useTranslations("landing");
  const common = useTranslations("common");
  const cases = useTranslations("cases");
  const loading = desk === undefined;

  let title = t("caseTitle"), href = "/cases/consumer_dispute_001";
  let rows: [string, string][] = [
    [t("fieldType"), t("fieldTypeValue")], [t("fieldCategory"), t("fieldCategoryValue")], [t("fieldParties"), t("fieldPartiesValue")],
    [t("fieldRole"), t("fieldRoleValue")], [t("fieldDuration"), t("fieldDurationValue")],
  ];
  if (desk) {
    const { card, detail } = desk;
    const who = (id: string) => detail.characters.find((c) => c.id === id);
    const plaintiff = who("plaintiff")?.name, defendant = who("defendant_rep");
    const parties = [plaintiff, defendant && (company(defendant.role) ?? defendant.name)].filter(Boolean).join(" — ");
    title = card.title; href = `/cases/${card.scenario_id}`;
    rows = [
      [t("fieldType"), (card.kind ?? "court") === "court" ? t("fieldTypeValue") : cases("kind_situation")], [t("fieldCategory"), card.category],
      ...(parties ? [[t("fieldParties"), parties] as [string, string]] : []),
      [t("fieldRole"), detail.player_role.title], [t("fieldDuration"), common("minutes", { count: card.minutes })],
    ];
  }
  return (
    <div className="cover-form fade-in" key={desk?.card.scenario_id ?? "demo"} aria-busy={loading}>
      <h2 id="case-title" className="desk-h">{loading ? "…" : title}</h2>
      <dl>
        {rows.map(([k, v]) => (<div key={k}><dt>{k}</dt><dd>{loading ? "…" : v}</dd></div>))}
      </dl>
      <Link className="btn-ink" href={href} aria-disabled={loading} tabIndex={loading ? -1 : undefined}>{t("open")}</Link>
    </div>
  );
}

export function LegalBase({ desk }: { desk: Desk | null | undefined }) {
  const t = useTranslations("landing");
  const acts = useTranslations("acts");
  const list = desk
    ? desk.detail.legal_acts.map((a) => ({ key: a.document_key, title: a.title, url: a.source_url ?? "https://lex.uz/" }))
    : (["CPRL", "CC", "CPC"] as const).map((k) => ({ key: k, title: acts(k), url: "https://lex.uz/" }));
  return (
    <>
      <ul>
        {list.map((a) => (
          <li key={a.key}><a href={a.url} target="_blank" rel="noopener noreferrer">{a.title}</a> <span>{t("actCurrent")}</span></li>
        ))}
      </ul>
      <p className="acts__checked">
        {t("actsChecked")}
        {desk?.health?.articles ? <> {t("actsArticles", { count: desk.health.articles })}</> : null}
      </p>
    </>
  );
}

/** Other cases on the shelf: real ones in live mode, the "coming soon" placeholders in mock mode. */
export function Shelf({ desk }: { desk: Desk | null | undefined }) {
  const soon = useTranslations("cases");
  const common = useTranslations("common");
  if (desk === undefined) return <ul aria-busy />;
  if (desk === null) {
    return (
      <ul>
        {(["soonCase2", "soonCase3", "soonCase4"] as const).map((k, i) => (
          <li key={k} className="mini-folder"><span>№ 00{i + 2}</span>{soon(k)}<em>{common("comingSoon")}</em></li>
        ))}
      </ul>
    );
  }
  if (!desk.others.length) return null;
  return (
    <ul>
      {desk.others.map((c) => (
        <li key={c.scenario_id} className="fade-in">
          <Link href={`/cases/${c.scenario_id}`} className="mini-folder mini-folder--open">
            <span>{soon(`kind_${c.kind ?? "court"}`)}</span>{c.title}<em>{common("minutes", { count: c.minutes })}</em>
          </Link>
        </li>
      ))}
    </ul>
  );
}
