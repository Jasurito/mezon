import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { ArticleCount } from "./pitch-facts";
import { ThemeStack } from "./theme-stack";

/** Public home page for guests: same case-file desk design, descriptive instead of a demo case. */
export function Pitch() {
  const t = useTranslations("pitch");
  return (
    <main id="main" className="pitch">
      <section className="pitch-hero" aria-labelledby="pitch-title">
        <div>
          <h1 id="pitch-title" className="desk-h">{t("heroTitle")}</h1>
          <p>{t("heroLead")}</p>
          <div className="pitch-cta">
            <Link className="desk-btn desk-btn--solid desk-btn--lg" href="/auth/sign-up">{t("ctaSignUp")}</Link>
            <Link className="desk-btn desk-btn--ghost desk-btn--lg" href="/cases">{t("ctaTry")}</Link>
          </div>
        </div>
        <ThemeStack />
      </section>

      <section aria-labelledby="pitch-for">
        <h2 id="pitch-for" className="desk-h pitch-title">{t("forTitle")}</h2>
        <div className="pitch-for">
          {/* two categories, open to everyone; each opens its section of the case list */}
          {(["situation", "court"] as const).map((k) => (
            <article key={k} className="sheet-paper pitch-sheet">
              <h3 className="desk-h">{t(`${k}Title`)}</h3>
              <p className="pitch-sheet__lead">{t(`${k}Lead`)}</p>
              <ul className="pitch-ticks">
                {([1, 2, 3] as const).map((i) => <li key={i}>{t(`${k}Point${i}`)}</li>)}
              </ul>
              <Link className="btn-ink" href={`/cases#track-${k}`}>{t(`${k}Cta`)}</Link>
            </article>
          ))}
        </div>
      </section>

      <section className="folder pitch-steps" aria-labelledby="pitch-steps">
        <div className="folder__tab">{t("stepsTab")}</div>
        <div className="folder__cover pitch-steps__cover">
          <div className="sheet-paper toc">
            <h2 id="pitch-steps" className="desk-h">{t("stepsTitle")}</h2>
            <ol>
              {([1, 2, 3, 4] as const).map((i) => (<li key={i}><b>{i}</b><span>{t(`step${i}`)}</span></li>))}
            </ol>
          </div>
          <p className="stamp" aria-hidden>{t("stamp")}</p>
        </div>
      </section>

      <section className="sheet-paper pitch-source" aria-labelledby="pitch-source">
        <h2 id="pitch-source" className="desk-h">{t("sourceTitle")}</h2>
        <ul className="pitch-ticks">
          <li><ArticleCount /></li>
          {([1, 2, 3] as const).map((i) => <li key={i}>{t(`source${i}`)}</li>)}
        </ul>
        <p className="acts__checked">{t("sourceNote")}</p>
      </section>

      <section className="pitch-close" aria-labelledby="pitch-close">
        <h2 id="pitch-close" className="desk-h">{t("closeTitle")}</h2>
        <p>{t("closeLead")}</p>
        <div className="pitch-cta">
          <Link className="desk-btn desk-btn--solid desk-btn--lg" href="/auth/sign-up">{t("ctaSignUp")}</Link>
          <Link className="desk-btn desk-btn--ghost desk-btn--lg" href="/cases">{t("ctaTry")}</Link>
        </div>
      </section>
    </main>
  );
}
