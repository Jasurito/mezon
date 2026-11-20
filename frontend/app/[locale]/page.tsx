import { useTranslations } from "next-intl";
import { setRequestLocale } from "next-intl/server";
import { use } from "react";
import { DeskHeader } from "@/components/site/desk-header";
import { Court } from "@/game/Court";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";

export default function Landing({ params }: { params: Promise<{ locale: string }> }) {
  const { locale } = use(params);
  setRequestLocale(locale as Locale);
  const t = useTranslations("landing");
  const acts = useTranslations("acts");
  const fields = [
    ["fieldType", "fieldTypeValue"], ["fieldCategory", "fieldCategoryValue"], ["fieldParties", "fieldPartiesValue"],
    ["fieldRole", "fieldRoleValue"], ["fieldDuration", "fieldDurationValue"],
  ] as const;
  const soon = useTranslations("cases");
  const common = useTranslations("common");
  return (
    <div className="desk-page">
      <DeskHeader />
      <main id="main" className="desk">
        <section className="desk-intro">
          <h1 className="desk-h">{t("headline")}</h1>
          <p>{t("lead")}</p>
        </section>

        <article className="folder" aria-labelledby="case-title">
          <div className="folder__tab">{t("caseNumber")}</div>
          <div className="folder__cover">
            <figure className="photo">
              <span className="clip" aria-hidden />
              <Court theme="ink" mode="hero" className="photo__scene" />
              <figcaption>{t("photoCaption")}</figcaption>
            </figure>
            <div className="cover-form">
              <h2 id="case-title" className="desk-h">{t("caseTitle")}</h2>
              <dl>
                {fields.map(([k, v]) => (<div key={k}><dt>{t(k)}</dt><dd>{t(v)}</dd></div>))}
              </dl>
              <Link className="btn-ink" href="/cases/consumer_dispute_001">{t("open")}</Link>
            </div>
            <p className="stamp" aria-hidden>{t("stamp")}</p>
          </div>
        </article>

        <section className="sheet-paper toc" aria-labelledby="toc-title">
          <h2 id="toc-title" className="desk-h">{t("tocTitle")}</h2>
          <ol>
            {(["toc1", "toc2", "toc3"] as const).map((k, i) => (<li key={k}><span>{t(k)}</span><i /><b>{i + 1}</b></li>))}
          </ol>
        </section>

        <section className="sheet-paper acts" aria-labelledby="acts-title">
          <h2 id="acts-title" className="desk-h">{t("actsTitle")}</h2>
          <ul>
            {(["CPRL", "CC", "CPC"] as const).map((k) => (
              <li key={k}><a href="https://lex.uz/" target="_blank" rel="noopener noreferrer">{acts(k)}</a> <span>{t("actCurrent")}</span></li>
            ))}
          </ul>
          <p className="acts__checked">{t("actsChecked")}</p>
        </section>

        <section className="shelf" aria-labelledby="shelf-title">
          <h2 id="shelf-title" className="desk-h">{t("shelfTitle")}</h2>
          <ul>
            {(["soonCase2", "soonCase3", "soonCase4"] as const).map((k, i) => (
              <li key={k} className="mini-folder"><span>№ 00{i + 2}</span>{soon(k)}<em>{common("comingSoon")}</em></li>
            ))}
          </ul>
          <Link className="shelf__all" href="/cases">{t("allCases")}</Link>
        </section>
      </main>
      <footer className="desk-foot">{common("disclaimer")} LexHackathon 2026.</footer>
    </div>
  );
}
