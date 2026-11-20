"use client";
import { Send } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { CitationChip } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { api, type CitationView, type Locale, type SessionResult } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Block { text: string; source_ids: string[]; verified: boolean }
interface Msg { role: "user" | "assistant"; text: string; blocks?: Block[]; sources?: Record<string, CitationView>; status?: "streaming" | "done" | "insufficient" | "ai_unavailable" | "error"; disclaimer?: string }

const label = (c: CitationView, locale: string) => (locale === "ru" ? `ст. ${c.article_number}` : `${c.article_number}-modda`);

/** AI Legal Mentor (spec §4.7): streamed answer blocks, each followed by source chips that open the LegalPanel. */
export default function MentorPage() {
  const t = useTranslations("mentor");
  const tr = useTranslations("results");
  const common = useTranslations("common");
  const locale = useLocale() as Locale;
  const { sessionId } = useParams<{ sessionId: string }>();
  const [result, setResult] = useState<SessionResult | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const abort = useRef<AbortController | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const busy = msgs.at(-1)?.status === "streaming";

  useEffect(() => { api.result(sessionId, locale).then(setResult).catch(() => setResult(null)); }, [sessionId, locale]);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth", block: "end" }); }, [msgs]);
  useEffect(() => () => abort.current?.abort(), []);

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    const history = msgs.slice(-6).map((m) => ({ role: m.role, text: m.text || (m.blocks ?? []).map((b) => b.text).join(" ") }));
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: question }, { role: "assistant", text: "", blocks: [], sources: {}, status: "streaming" }]);
    const patch = (fn: (m: Msg) => Msg) => setMsgs((all) => [...all.slice(0, -1), fn(all[all.length - 1])]);
    abort.current = new AbortController();
    try {
      for await (const ev of api.mentor({ session_id: sessionId, question, locale, history }, abort.current.signal)) {
        if (ev.event === "sources") patch((m) => ({ ...m, sources: Object.fromEntries(ev.data.map((s) => [s.source_id, s.citation])) }));
        else if (ev.event === "block") patch((m) => ({ ...m, blocks: [...(m.blocks ?? []), ev.data] }));
        else if (ev.event === "done") patch((m) => ({ ...m, status: ev.data.insufficient_sources ? "insufficient" : ev.data.ai_unavailable ? "ai_unavailable" : "done", disclaimer: ev.data.disclaimer }));
        else if (ev.event === "error") patch((m) => ({ ...m, status: "error" }));
      }
    } catch { patch((m) => ({ ...m, status: "error" })); }
  }

  const quick = [t("quick1"), t("quick2"), t("quick3"), t("quick4")];
  return (
    <div className="grid gap-8 lg:grid-cols-[18rem_1fr]">
      <aside className="h-fit rounded-lg border border-hairline bg-navy-2 p-5 lg:sticky lg:top-6">
        <h2 className="text-sm font-semibold text-ink-muted">{t("caseSummary")}</h2>
        {result ? (
          <>
            <p className="mt-2 text-lg font-bold">{result.outcome_title}</p>
            <p className="pix text-2xl text-gold">{result.score}/{result.max_score}</p>
            <ul className="mt-3 grid gap-1.5 text-sm">
              {result.mistakes.map((m, i) => <li key={i} className="border-l-2 border-terra pl-2">{m.title}</li>)}
            </ul>
            <Link href={`/results/${sessionId}`} className="mt-4 inline-block text-sm text-gold underline">{tr("kicker")}</Link>
          </>
        ) : <p className="mt-2 text-sm text-ink-muted">…</p>}
      </aside>

      <section className="flex min-h-[70svh] flex-col">
        <h1 className="text-3xl font-extrabold">{t("title")}</h1>
        <p className="mt-1 text-ink-muted">{t("lead")}</p>

        <div className="mt-6 flex-1 space-y-5" aria-live="polite">
          {msgs.length === 0 && <p className="text-ink-muted">{t("empty")}</p>}
          {msgs.map((m, i) => m.role === "user" ? (
            <p key={i} className="ml-auto w-fit max-w-[80%] rounded-lg bg-navy-3 px-4 py-2">{m.text}</p>
          ) : (
            <div key={i} className="max-w-[72ch] space-y-3">
              {m.status === "streaming" && !m.blocks?.length && <p className="text-ink-muted" role="status">{t("thinking")}</p>}
              {m.blocks?.map((b, j) => (
                <div key={j} className={cn(!b.verified && "opacity-70")}>
                  <p>{b.text}</p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-2">
                    {b.source_ids.map((sid) => { const c = m.sources?.[sid]; return c?.citation_id ? <CitationChip key={sid} id={c.citation_id} label={`[${sid.slice(1)}] ${label(c, locale)}`} /> : null; })}
                    {!b.verified && <span className="text-xs text-terra">{t("unverified")}</span>}
                  </div>
                </div>
              ))}
              {m.status === "insufficient" && <p className="rounded-md border border-hairline bg-navy-2 p-4">{t("insufficient")}</p>}
              {m.status === "ai_unavailable" && (
                <div className="rounded-md border border-hairline bg-navy-2 p-4">
                  <p>{t("aiUnavailable")}</p>
                  <div className="mt-2 flex flex-wrap gap-2">{Object.values(m.sources ?? {}).map((c) => c.citation_id && <CitationChip key={c.citation_id} id={c.citation_id} label={label(c, locale)} />)}</div>
                </div>
              )}
              {m.status === "error" && <p className="text-terra">{common("networkError")}</p>}
              {m.status && m.status !== "streaming" && <p className="text-xs text-ink-muted">{t("disclaimer")}</p>}
            </div>
          ))}
          <div ref={end} />
        </div>

        <div className="sticky bottom-0 mt-6 bg-background pb-4 pt-2">
          <div className="mb-2 flex flex-wrap gap-2">
            {quick.map((q) => <Button key={q} variant="outline" size="lg" disabled={busy} onClick={() => ask(q)}>{q}</Button>)}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); ask(input); }} className="flex gap-2">
            <label htmlFor="q" className="sr-only">{t("placeholder")}</label>
            <input id="q" value={input} onChange={(e) => setInput(e.target.value)} placeholder={t("placeholder")} maxLength={500}
              className="min-h-12 flex-1 rounded-md border border-input bg-navy-2 px-4 placeholder:text-ink-muted focus-visible:outline-2 focus-visible:outline-gold" />
            <Button type="submit" size="lg" className="h-12 px-5" disabled={busy || !input.trim()}><Send />{t("send")}</Button>
          </form>
        </div>
      </section>
    </div>
  );
}
