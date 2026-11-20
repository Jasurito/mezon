"use client";
import { ExternalLink } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { api, type CitationView } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useUi } from "@/store/ui";
import { useLoad } from "@/hooks/use-load";

const fmt = (iso: string | null) => (iso ? iso.split("-").reverse().join(".") : "");

/** Shared article viewer (spec §4.5 LegalPanel): verbatim text, edition status, lex.uz link. Text comes from DB rows only. */
export function LegalPanel() {
  const t = useTranslations("legal");
  const locale = useLocale();
  const { legal, closeLegal } = useUi();
  const loaded = useLoad<CitationView>(legal ? () => api.citation(legal.id, legal.date, locale) : null, [legal, locale]);
  // show only the article that was asked for (never a stale one)
  const data = loaded.data && loaded.data.citation_id === legal?.id ? loaded.data : null;
  const failed = loaded.error;

  const status = data?.edition.status ?? "current";
  return (
    <Sheet open={!!legal} onOpenChange={(o) => !o && closeLegal()}>
      <SheetContent side="right" className="w-[min(28rem,94vw)] overflow-y-auto border-hairline bg-paper p-6 text-navy sm:max-w-none">
        <SheetHeader className="p-0">
          <SheetDescription className="text-[#42506a]">{data?.document_title ?? " "}</SheetDescription>
          <SheetTitle className="text-3xl font-extrabold text-navy">
            {data ? (locale === "ru" ? `Статья ${data.article_number}` : `${data.article_number}-modda`) : failed ? t("notFound") : "…"}
          </SheetTitle>
        </SheetHeader>
        {data && (
          <div className="mt-2 space-y-4">
            {data.article_title && <p className="text-[#42506a]">{data.article_title}</p>}
            <p className={cn("inline-block rounded px-2 py-1 text-sm font-semibold",
              status === "current" && "bg-teal/15 text-[#0f6e68]", status === "historical" && "bg-navy/10 text-[#42506a]", status === "unconfirmed" && "bg-[#f3d9c9] text-[#8a3a1f]")}>
              {t(`status_${status}`, { date: fmt(data.edition.effective_from) })}{legal?.date ? `, ${t("asOf", { date: fmt(legal.date) })}` : ""}
            </p>
            <div className="space-y-4">
              {data.parts.map((p) => (
                <div key={p.part_number} className="grid gap-1.5">
                  <span className="text-sm font-bold">{p.part_number}.</span>
                  {p.text ? <p className="whitespace-pre-line">{p.text}</p> : (
                    <>{[100, 100, 64].map((w, i) => <span key={i} className="skel" style={{ width: `${w - ((p.part_number * 7 + i * 11) % 30)}%` }} />)}<span className="sr-only">{t("pendingText")}</span></>
                  )}
                </div>
              ))}
            </div>
            {!data.text && <p className="text-sm text-[#42506a]">{t("pendingText")}</p>}
            {data.translation_note && <p className="text-sm text-[#42506a]">{data.translation_note}</p>}
            {data.source_url && (
              <Button asChild size="lg" className="mt-2">
                <a href={data.source_url} target="_blank" rel="noopener noreferrer">{t("openLex")}<ExternalLink /></a>
              </Button>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
