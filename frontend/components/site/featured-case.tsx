"use client";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Link } from "@/i18n/navigation";
import { api, API_MODE, type HealthResponse, type Locale, type ScenarioCard, type ScenarioDetail } from "@/lib/api";

/*
 * Landing "case folder" and legal base (spec FRONTEND.md §4.1). Mock mode shows the demo case from the locale files;
 * live mode shows the first available scenario, its acts (links to lex.uz) and the article count from /api/health.
 * One request set per locale, shared by the three blocks.
 */
interface Featured { card: ScenarioCard; detail: ScenarioDetail; health: HealthResponse | null }
const cache = new Map<string, Promise<Featured | null>>();

function loadFeatured(locale: Locale): Promise<Featured | null> {
  let p = cache.get(locale);
  if (!p) {
    p = (async () => {
      const card = (await api.scenarios(locale)).find((c) => c.available);
      if (!card) return null;
      const [detail, health] = await Promise.all([api.scenario(card.scenario_id, locale), api.health().catch(() => null)]);
      return { card, detail, health };
    })().catch(() => null);
    cache.set(locale, p);
  }
  return p;
}

/** null: mock mode (static demo content) or the backend did not answer; undefined: still loading */
function useFeatured(): Featured | null | undefined {
  const locale = useLocale() as Locale;
  const [data, setData] = useState<{ locale: string; value: Featured | null } | null>(null);
  useEffect(() => {
    if (API_MODE !== "live") return;
    let live = true;
    loadFeatured(locale).then((value) => { if (live) setData({ locale, value }); });
    return () => { live = false; };
  }, [locale]);
  if (API_MODE !== "live") return null;
  return data?.locale === locale ? data.value : undefined;
}

const dmy = (iso: string) => iso.split("-").reverse().join(".");
/** "Представитель ООО «Ёркин Техно Савдо»" -> "ООО «Ёркин Техно Савдо»"; "“Yorqin Texno Savdo” MChJ vakili" -> "“Yorqin Texno Savdo” MChJ" */
const company = (role: string) => role.match(/(\S+\s)?[«“][^»”]+[»”](\s\S+)?/)?.[0]?.trim() ?? null;

export function CaseCaption() {
  const t = useTranslations("landing");
  const f = useFeatured();
  return <figcaption>{f ? t("photoCaptionDate", { date: dmy(f.detail.legal_date) }) : t("photoCaption")}</figcaption>;
}

export function CaseCover() {
  const t = useTranslations("landing");
  const common = useTranslations("common");
  const f = useFeatured();
  const loading = f === undefined;

  let title = t("caseTitle"), href = "/cases/consumer_dispute_001";
  let rows: [string, string][] = [
    [t("fieldType"), t("fieldTypeValue")], [t("fieldCategory"), t("fieldCategoryValue")], [t("fieldParties"), t("fieldPartiesValue")],
    [t("fieldRole"), t("fieldRoleValue")], [t("fieldDuration"), t("fieldDurationValue")],
  ];
  if (f) {
    const { card, detail } = f;
    const who = (id: string) => detail.characters.find((c) => c.id === id);
    const plaintiff = who("plaintiff")?.name, defendant = who("defendant_rep");
    const parties = [plaintiff, defendant && (company(defendant.role) ?? defendant.name)].filter(Boolean).join(" — ");
    title = card.title; href = `/cases/${card.scenario_id}`;
    rows = [
      [t("fieldType"), t("fieldTypeValue")], [t("fieldCategory"), card.category],
      ...(parties ? [[t("fieldParties"), parties] as [string, string]] : []),
      [t("fieldRole"), detail.player_role.title], [t("fieldDuration"), common("minutes", { count: card.minutes })],
    ];
  }
  return (
    <div className="cover-form" aria-busy={loading}>
      <h2 id="case-title" className="desk-h">{loading ? "…" : title}</h2>
      <dl>
        {rows.map(([k, v]) => (<div key={k}><dt>{k}</dt><dd>{loading ? "…" : v}</dd></div>))}
      </dl>
      <Link className="btn-ink" href={href} aria-disabled={loading} tabIndex={loading ? -1 : undefined}>{t("open")}</Link>
    </div>
  );
}

export function LegalBase() {
  const t = useTranslations("landing");
  const acts = useTranslations("acts");
  const f = useFeatured();
  const list = f
    ? f.detail.legal_acts.map((a) => ({ key: a.document_key, title: a.title, url: a.source_url ?? "https://lex.uz/" }))
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
        {f?.health?.articles ? <> {t("actsArticles", { count: f.health.articles })}</> : null}
      </p>
    </>
  );
}
