import { ChevronLeft, ChevronRight, FileText } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState, type Ref } from "react";
import { api, type EvidenceView, type Locale } from "@/lib/api";
import { cn } from "@/lib/utils";

/**
 * The case materials as part of the game screen (no drawer, no modal): every document is one click away and
 * opens in place, with previous / next to flip through the file. Opening a document counts as reviewing it.
 */
export function CaseFile({ ref, sessionId, locale, evidence, fresh, selected, onSelect, highlight, className }: {
  ref?: Ref<HTMLElement>; className?: string; sessionId: string; locale: Locale; evidence: EvidenceView[]; fresh: string[];
  selected: string | null; onSelect: (id: string) => void; highlight: boolean;
}) {
  const t = useTranslations("play");
  const [texts, setTexts] = useState<Record<string, string[]>>({});
  const doc = evidence.find((e) => e.id === selected) ?? null;
  const index = doc ? evidence.indexOf(doc) : -1;
  // read = reviewed by the game, or opened here (some documents have no scored review action)
  const opened = new Set(Object.keys(texts).map((k) => k.slice(k.indexOf(":") + 1)));
  const isRead = (e: EvidenceView) => e.reviewed || opened.has(e.id);
  const read = evidence.filter(isRead).length;
  const key = `${locale}:${selected}`;
  const lines = selected ? texts[key] : undefined;

  useEffect(() => {
    if (!selected || texts[key]) return;
    let live = true;
    api.document(sessionId, selected, locale).catch(() => [] as string[])
      .then((l) => { if (live) setTexts((all) => ({ ...all, [key]: l })); });
    return () => { live = false; };
  }, [sessionId, selected, locale, key, texts]);

  const step = (d: number) => { if (index >= 0) onSelect(evidence[(index + d + evidence.length) % evidence.length].id); };

  return (
    <section ref={ref} tabIndex={-1} aria-labelledby="case-file-title"
      onKeyDown={(e) => {
        if (!doc || (e.target as HTMLElement).closest("input, textarea")) return;
        if (e.key === "ArrowRight") { e.preventDefault(); step(1); }
        if (e.key === "ArrowLeft") { e.preventDefault(); step(-1); }
      }}
      className={cn("case-file flex min-h-0 flex-col rounded-md border border-hairline bg-navy-2 outline-none focus-visible:ring-2 focus-visible:ring-gold/50", highlight && "is-highlight", className)}>
      <header className="flex items-baseline justify-between gap-3 border-b border-hairline px-4 py-3">
        <h2 id="case-file-title" className="font-bold">{t("caseFile")}</h2>
        <p className="text-xs text-ink-muted">{t("readCount", { read, total: evidence.length })}</p>
      </header>

      <ul className="flex flex-wrap gap-1.5 px-3 py-3" aria-label={t("evidence")}>
        {evidence.map((e) => {
          const isNew = fresh.includes(e.id);
          return (
            <li key={e.id}>
              <button type="button" aria-current={e.id === selected ? "true" : undefined} onClick={() => onSelect(e.id)}
                className={cn(
                  "flex min-h-9 items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-left text-sm hover:border-gold",
                  e.id === selected ? "border-gold bg-gold font-semibold text-navy" : isNew ? "border-terra bg-navy" : "border-paper/15 bg-navy",
                )}>
                <FileText className="size-3.5 shrink-0 opacity-70" aria-hidden />
                <span>{e.title}</span>
                {isNew ? <span className="text-xs text-terra">{t("newEvidence")}</span>
                  : isRead(e) && e.id !== selected ? <span className="text-xs text-teal" aria-label={t("reviewed")}>✓</span> : null}
              </button>
            </li>
          );
        })}
      </ul>

      <div className="flex min-h-0 flex-1 flex-col px-3 pb-3">
        {doc ? (
          <article className="paper-doc flex min-h-0 flex-1 flex-col rounded-md shadow-lg" aria-live="polite">
            <div className="flex items-center gap-1 border-b border-[#d8cfb8] px-2 py-1.5">
              <button type="button" onClick={() => step(-1)} aria-label={t("prevDoc")} className="grid size-9 place-items-center rounded hover:bg-navy/10"><ChevronLeft className="size-4" /></button>
              <h3 className="flex-1 text-center font-bold">{doc.title}</h3>
              <span className="text-xs text-[#5b5544]">{index + 1}/{evidence.length}</span>
              <button type="button" onClick={() => step(1)} aria-label={t("nextDoc")} className="grid size-9 place-items-center rounded hover:bg-navy/10"><ChevronRight className="size-4" /></button>
            </div>
            <div className="doc-body min-h-0 flex-1 space-y-1.5 overflow-y-auto px-4 py-3">
              {lines === undefined ? <p className="text-[#5b5544]">…</p>
                : lines.length === 0 ? <p className="text-[#5b5544]">{t("docEmpty")}</p>
                : lines.map((l, i) => <p key={i}>{l}</p>)}
            </div>
          </article>
        ) : (
          <p className="grid flex-1 place-items-center rounded-md border border-dashed border-paper/20 px-6 py-8 text-center text-sm text-ink-muted">{t("pickDoc")}</p>
        )}
      </div>
    </section>
  );
}
