"use client";
import { useTranslations } from "next-intl";
import { Court } from "@/game/Court";
import { Link } from "@/i18n/navigation";
import { CaseCaption, CaseCover, CaseNumber, LegalBase, Shelf, useDesk } from "./featured-case";

/** The case desk for signed-in users: a random case folder (a different one on each visit), the legal base and the shelf. */
export function CaseDesk() {
  const t = useTranslations("landing");
  const desk = useDesk();
  return (
    <main id="main" className="desk">
      <section className="desk-intro">
        <h1 className="desk-h">{t("headline")}</h1>
        <p>{t("lead")}</p>
      </section>

      <article className="folder" aria-labelledby="case-title">
        <CaseNumber desk={desk} />
        <div className="folder__cover">
          <figure className="photo">
            <span className="clip" aria-hidden />
            {/* the signed-in user's own courtroom theme (Settings) */}
            <Court mode="hero" className="photo__scene" />
            <CaseCaption desk={desk} />
          </figure>
          <CaseCover desk={desk} />
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
        <LegalBase desk={desk} />
      </section>

      <section className="shelf" aria-labelledby="shelf-title">
        <h2 id="shelf-title" className="desk-h">{t("shelfTitle")}</h2>
        <Shelf desk={desk} />
        <Link className="shelf__all" href="/cases">{t("allCases")}</Link>
      </section>
    </main>
  );
}
