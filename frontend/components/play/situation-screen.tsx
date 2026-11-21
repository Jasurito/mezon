"use client";
import { Check, ChevronLeft, FileText, FolderOpen, Scale } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { ErrorState, Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Link, useRouter } from "@/i18n/navigation";
import { api, ApiError, type ActionView, type GameEvent, type GameState, type Locale } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useUi } from "@/store/ui";

/*
 * Life situation (scenario audience "public") for non-lawyers: the same engine and API as a court case, shown as a
 * step-by-step story instead of a courtroom. Every action is a plain card: a question with answers, a document to
 * put in the folder, or "continue". Rules arrive as "the rule in plain words" with the official article one click away.
 */
type Entry =
  | { key: number; kind: "say"; speaker: string; text: string }
  | { key: number; kind: "note"; citation_id: string; text: string }
  | { key: number; kind: "stage"; title: string }
  | { key: number; kind: "score"; delta: number };

let seq = 0;
function toEntries(events: GameEvent[]): Entry[] {
  const out: Entry[] = [];
  let points = 0; // shown once, after the step's explanation, before the next stage starts
  const flush = () => { if (points > 0) out.push({ key: ++seq, kind: "score", delta: points }); points = 0; };
  for (const e of events) {
    if (e.type === "say") out.push({ key: ++seq, kind: "say", speaker: e.speaker, text: e.text });
    else if (e.type === "legal_note") out.push({ key: ++seq, kind: "note", citation_id: e.citation_id, text: e.text });
    else if (e.type === "stage_changed" && e.stage !== "RESULTS") { flush(); out.push({ key: ++seq, kind: "stage", title: e.title }); }
    else if (e.type === "score" && e.delta > 0) points += e.delta;
  }
  flush();
  return out;
}
const addedKey = (sid: string) => `mezon.situation.added.${sid}`;

export function SituationScreen({ sessionId }: { sessionId: string }) {
  const t = useTranslations("situation");
  const tc = useTranslations("common");
  const locale = useLocale() as Locale;
  const router = useRouter();
  const openLegal = useUi((s) => s.openLegal);
  const [state, setState] = useState<GameState | null>(null);
  const [log, setLog] = useState<Entry[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<"offline" | "load" | null>(null);
  const [names, setNames] = useState<Record<string, string>>({});
  const [player, setPlayer] = useState<string | null>(null);
  const [picked, setPicked] = useState<Record<string, string>>({});
  // documents the story added to the folder (e.g. the copy of the claim); kept for reloads of this session
  const [added, setAdded] = useState<string[]>(() => {
    try { return JSON.parse(sessionStorage.getItem(addedKey(sessionId)) || "[]"); } catch { return []; }
  });
  const endRef = useRef<HTMLDivElement>(null);
  const lastLocale = useRef(locale);

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        if (lastLocale.current !== locale) await api.setSessionLocale(sessionId, locale).catch(() => null);
        lastLocale.current = locale;
        const s = await api.session(sessionId, locale);
        if (!live) return;
        setState(s); setLog(toEntries(s.events)); setError(null);
        const sc = await api.scenario(s.scenario_id, locale).catch(() => null);
        if (sc && live) {
          setNames(Object.fromEntries(sc.characters.map((c) => [c.id, c.name])));
          setPlayer(sc.player_role.character_id);
        }
      } catch (e) {
        if (live) setError(e instanceof ApiError && e.status === 404 ? "load" : "offline");
      }
    })();
    return () => { live = false; };
  }, [sessionId, locale]);

  useEffect(() => { endRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" }); }, [log.length]);

  // finished: a short pause on the last line, then the result
  useEffect(() => {
    if (!state?.finished) return;
    const id = setTimeout(() => router.push(`/results/${sessionId}`), 2200);
    return () => clearTimeout(id);
  }, [state?.finished, router, sessionId]);

  async function act(actionId: string, params?: { option?: string }) {
    if (busy) return;
    setBusy(true);
    try {
      const next = await api.act(sessionId, actionId, params);
      const newly = next.events.flatMap((e) => (e.type === "evidence_added" ? [e.evidence_id] : []));
      if (newly.length) {
        const all = [...new Set([...added, ...newly])];
        setAdded(all);
        try { sessionStorage.setItem(addedKey(sessionId), JSON.stringify(all)); } catch { /* ignore */ }
      }
      setState(next);
      setLog((l) => [...l, ...toEntries(next.events)]);
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        toast.error(t("illegal"));
        const fresh = await api.session(sessionId, locale).catch(() => null);
        if (fresh) setState(fresh);
      } else toast.error(tc("networkError"));
    } finally { setBusy(false); }
  }

  if (error) return <div className="px-4 pt-10"><ErrorState message={error === "load" ? t("loadError") : undefined} onRetry={() => location.reload()} /></div>;
  if (!state) return <Loading />;

  const st = state;
  const actions = st.available_actions;
  const decisions = actions.filter((a) => a.kind === "decision" && a.options?.length);
  const keeps = actions.filter((a) => a.kind === "evidence" && a.evidence_id);
  const others = actions.filter((a) => !decisions.includes(a) && !keeps.includes(a));
  const folder = st.evidence.filter((e) => e.presented || added.includes(e.id));
  const evTitle = (id: string) => st.evidence.find((e) => e.id === id)?.title ?? id;
  const steps = Math.max(1, st.stage_count - 1); // RESULTS is not a step

  return (
    <div className="flex min-h-svh flex-col">
      <header className="border-b border-hairline px-4 py-3 sm:px-8">
        <div className="mx-auto flex max-w-6xl items-center gap-4">
          <Link href={`/cases/${st.scenario_id}`} className="flex items-center text-ink-muted no-underline hover:text-paper"><ChevronLeft className="size-4" />{t("exit")}</Link>
          <p className="min-w-0 flex-1 truncate">
            <span className="text-ink-muted">{t("kicker")} · {t("step", { index: Math.min(st.stage_index, steps), count: steps })}: </span>
            <strong>{st.stage_title}</strong>
          </p>
          <p className="num flex items-center gap-1.5 text-lg text-gold"><span className="sr-only">{t("score")}:</span><span className="star-icon" aria-hidden />{st.score}</p>
        </div>
        <ol className="mx-auto mt-3 flex max-w-6xl gap-1.5" aria-label={t("progress")}>
          {Array.from({ length: steps }, (_, i) => (
            <li key={i} aria-current={i + 1 === st.stage_index ? "step" : undefined}
              className={cn("h-1.5 flex-1 rounded-full", i + 1 < st.stage_index || st.finished ? "bg-gold" : i + 1 === st.stage_index ? "bg-gold/60" : "bg-paper/10")} />
          ))}
        </ol>
      </header>

      <main id="main" className="mx-auto grid w-full max-w-6xl flex-1 items-start gap-6 px-3 pb-24 pt-6 sm:px-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <div className="min-w-0">
          {/* the story so far */}
          <section aria-live="polite" aria-label={t("story")} className="grid gap-3">
            {log.map((e) => {
              if (e.kind === "stage") return (
                <h2 key={e.key} className="mt-4 flex items-center gap-3 text-sm font-bold uppercase tracking-wide text-gold first:mt-0">
                  <span className="h-px flex-1 bg-hairline" />{e.title}<span className="h-px flex-1 bg-hairline" />
                </h2>
              );
              if (e.kind === "score") return <p key={e.key} className="num justify-self-start rounded-full bg-teal/15 px-2.5 py-0.5 text-sm text-teal">+{e.delta}</p>;
              if (e.kind === "note") return (
                <aside key={e.key} className="rounded-md border-l-4 border-gold bg-paper px-4 py-3 text-navy">
                  <p className="flex items-center gap-1.5 text-sm font-bold text-[#7a5f0e]"><Scale className="size-4" aria-hidden />{t("rule")}</p>
                  <p className="mt-1">{e.text}</p>
                  <button type="button" className="mt-1.5 text-sm font-semibold text-[#7a5f0e] underline underline-offset-2" onClick={() => openLegal(e.citation_id, st.legal_date)}>{tc("openArticle")}</button>
                </aside>
              );
              if (e.speaker === "narrator") return <p key={e.key} className="max-w-[65ch] text-[1.05rem] leading-relaxed">{e.text}</p>;
              const mine = e.speaker === player;
              return (
                <figure key={e.key} className={cn("max-w-[34rem] rounded-xl px-4 py-2.5", mine ? "justify-self-end rounded-br-sm bg-gold/15" : "justify-self-start rounded-bl-sm bg-navy-3")}>
                  <figcaption className={cn("text-xs font-bold", mine ? "text-gold" : "text-ink-muted")}>{names[e.speaker] ?? e.speaker}</figcaption>
                  <blockquote className="mt-0.5">{e.text}</blockquote>
                </figure>
              );
            })}
            <div ref={endRef} />
          </section>

          {/* your move */}
          {!st.finished ? (
            <section aria-label={t("yourMove")} className={cn("mt-8 rounded-lg border border-gold/40 bg-navy-2 p-4 sm:p-6", busy && "opacity-60")} aria-busy={busy}>
              <p className="mb-4 text-sm font-bold uppercase tracking-wide text-gold">{t("yourMove")}</p>
              <div className="grid gap-6">
                {decisions.map((a) => <Question key={a.action_id} action={a} value={picked[a.action_id]} disabled={busy}
                  onPick={(o) => setPicked((p) => ({ ...p, [a.action_id]: o }))}
                  onAnswer={() => picked[a.action_id] && act(a.action_id, { option: picked[a.action_id] })}
                  onRule={(c) => openLegal(c, st.legal_date)} />)}

                {keeps.length > 0 && (
                  <fieldset>
                    <legend className="mb-3 font-semibold">{t("pickDocs")}</legend>
                    <ul className="grid gap-2 sm:grid-cols-2">
                      {keeps.map((a) => (
                        <li key={a.action_id}>
                          <button type="button" disabled={busy} onClick={() => act(a.action_id)}
                            className="flex min-h-14 w-full items-center gap-3 rounded-md border border-paper/20 bg-navy px-4 py-3 text-left hover:border-gold disabled:pointer-events-none">
                            <FileText className="size-5 shrink-0 text-gold" aria-hidden />
                            <span className="flex-1">{evTitle(a.evidence_id!)}</span>
                            <span className="rounded-sm border border-gold/50 px-2 py-0.5 text-xs text-gold">{t("toFolder")}</span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </fieldset>
                )}

                {others.map((a) => (
                  <Button key={a.action_id} size="lg" className="h-12 justify-self-start px-6 text-base" disabled={busy} onClick={() => act(a.action_id)}>{a.label}</Button>
                ))}
              </div>
            </section>
          ) : (
            <section className="mt-8 rounded-lg border border-teal/40 bg-navy-2 p-6">
              <p className="flex items-center gap-2 text-lg font-bold"><Check className="size-5 text-teal" aria-hidden />{t("finished")}</p>
              <Button asChild size="lg" className="mt-4 h-12 px-6 text-base"><Link href={`/results/${sessionId}`}>{t("seeResult")}</Link></Button>
            </section>
          )}
        </div>

        <Folder sessionId={sessionId} locale={locale} items={folder} />
      </main>
    </div>
  );
}

function Question({ action, value, disabled, onPick, onAnswer, onRule }: {
  action: ActionView; value?: string; disabled: boolean;
  onPick: (option: string) => void; onAnswer: () => void; onRule: (citation: string) => void;
}) {
  const t = useTranslations("situation");
  const tc = useTranslations("common");
  return (
    <fieldset>
      <legend className="mb-3 text-lg font-semibold">{action.label}</legend>
      <div role="radiogroup" aria-label={action.label} className="grid gap-2">
        {action.options!.map((o) => (
          <button key={o.id} type="button" role="radio" aria-checked={value === o.id} disabled={disabled} onClick={() => onPick(o.id)}
            className="min-h-12 rounded-md border border-paper/20 bg-navy px-4 py-3 text-left hover:border-gold aria-checked:border-gold aria-checked:bg-gold aria-checked:font-semibold aria-checked:text-navy">
            {o.label}
          </button>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-3">
        <Button disabled={disabled || !value} onClick={onAnswer} className="h-11 px-5">{t("answer")}</Button>
        {action.hint_citation_ids[0] && (
          <button type="button" className="flex items-center gap-1 text-sm text-gold underline-offset-4 hover:underline" onClick={() => onRule(action.hint_citation_ids[0])}>
            <Scale className="size-4" aria-hidden />{tc("whichRule")}
          </button>
        )}
      </div>
    </fieldset>
  );
}

/** "Your folder": the documents kept so far; each one opens in place on paper. */
function Folder({ sessionId, locale, items }: { sessionId: string; locale: Locale; items: GameState["evidence"] }) {
  const t = useTranslations("situation");
  const [open, setOpen] = useState<string | null>(null);
  const [texts, setTexts] = useState<Record<string, string[]>>({});
  async function toggle(id: string) {
    if (open === id) return setOpen(null);
    setOpen(id);
    if (!texts[id]) {
      const lines = await api.document(sessionId, id, locale).catch(() => [] as string[]);
      setTexts((all) => ({ ...all, [id]: lines }));
    }
  }
  return (
    <aside className="relative lg:sticky lg:top-6" aria-labelledby="folder-title">
      <div className="inline-flex items-center gap-2 rounded-t-md bg-gold px-4 py-1.5 font-bold text-navy">
        <FolderOpen className="size-4" aria-hidden /><h2 id="folder-title">{t("folder")}</h2>
        <span className="num text-sm">{items.length}</span>
      </div>
      <div className="rounded-b-md rounded-tr-md border border-gold/40 bg-navy-2 p-3">
        {items.length === 0 ? <p className="px-1 py-4 text-sm text-ink-muted">{t("folderEmpty")}</p> : (
          <ul className="grid gap-2">
            {items.map((e) => (
              <li key={e.id}>
                <button type="button" onClick={() => toggle(e.id)} aria-expanded={open === e.id}
                  className="flex w-full items-center gap-2 rounded-md bg-paper px-3 py-2.5 text-left text-navy hover:bg-white">
                  <FileText className="size-4 shrink-0 text-[#7a5f0e]" aria-hidden /><span className="flex-1 text-sm font-semibold">{e.title}</span>
                </button>
                {open === e.id && (
                  <div className="paper-doc doc-body -mt-1 space-y-1 rounded-b-md px-3 pb-3 pt-2 text-sm">
                    {texts[e.id] === undefined ? <p>…</p> : texts[e.id].length === 0 ? <p>{t("docEmpty")}</p> : texts[e.id].map((l, i) => <p key={i}>{l}</p>)}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </aside>
  );
}
