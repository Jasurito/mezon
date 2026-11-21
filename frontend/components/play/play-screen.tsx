"use client";
import { ChevronLeft, FileText, MessagesSquare, Scale } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { ErrorState, Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Court } from "@/game/Court";
import { Link, useRouter } from "@/i18n/navigation";
import { api, type ActionView, type Locale } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useGame } from "@/store/game";
import { useUi } from "@/store/ui";
import { NpcPanel, type Askable } from "./npc-panel";

const NAMES: Record<string, string> = {};

export function PlayScreen({ sessionId }: { sessionId: string }) {
  const t = useTranslations();
  const locale = useLocale() as Locale;
  const router = useRouter();
  const g = useGame();
  const openLegal = useUi((s) => s.openLegal);
  const [drawer, setDrawer] = useState(false);
  const [doc, setDoc] = useState<{ id: string; title: string; lines: string[] } | null>(null);
  const [decision, setDecision] = useState<ActionView | null>(null);
  const [names, setNames] = useState<Record<string, { name: string; role: string }>>({});
  const [askable, setAskable] = useState<Askable[]>([]);
  const [asking, setAsking] = useState(false);
  const actionsRef = useRef<HTMLDivElement>(null);
  const secretary = t("play.secretary");
  const tagNames = useMemo(() => ({ secretary, ...Object.fromEntries(Object.entries(names).map(([id, n]) => [id, n.name])) }), [names, secretary]);
  const lastLocale = useRef(locale);

  // load / reload on locale switch (PATCH session, then GET: spec §4.5)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (lastLocale.current !== locale && g.state) await api.setSessionLocale(sessionId, locale).catch(() => null);
      lastLocale.current = locale;
      if (!cancelled) await g.load(sessionId, locale);
      const s = useGame.getState().state;
      if (s && !cancelled) {
        const sc = await api.scenario(s.scenario_id, locale).catch(() => null);
        if (sc) {
          setNames(Object.fromEntries(sc.characters.map((c) => [c.id, { name: c.id === sc.player_role.character_id ? (locale === "ru" ? "Вы" : t("case.you")) : c.name, role: c.role }])));
          // free questions go to the other participants; the judge runs the hearing and is not questioned
          setAskable(sc.characters.filter((c) => c.id !== sc.player_role.character_id && c.id !== "judge").map((c) => ({ id: c.id, name: c.name, role: c.role })));
        }
      }
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId, locale]);
  useEffect(() => () => useGame.getState().reset(), []);

  // preparation stage: evidence drawer opens by default (spec §4.5)
  const stage = g.state?.stage;
  const [prepOpened, setPrepOpened] = useState(false);
  if (stage === "PREPARATION" && !g.busy && !prepOpened) { setPrepOpened(true); setDrawer(true); }

  // finished: after the gavel, go to results
  useEffect(() => {
    if (g.state?.finished && !g.busy && g.queue.length === 0) {
      const id = setTimeout(() => router.push(`/results/${sessionId}`), 1200);
      return () => clearTimeout(id);
    }
  }, [g.state?.finished, g.busy, g.queue.length, router, sessionId]);

  useEffect(() => { if (g.illegal) toast.error(t("play.illegal")); }, [g.illegal, t]);

  // Space / Enter advance the dialogue when focus is not on a control
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.key === " " || e.key === "Enter") && !(e.target as HTMLElement).closest("button, a, input, textarea, [role=dialog]")) { e.preventDefault(); useGame.getState().advance(); }
    };
    window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey);
  }, []);

  const onSceneClick = useCallback((id: string) => {
    if (id === "evidence_table") return setDrawer(true);
    const a = useGame.getState().state?.available_actions.find((x) => x.target_character === id);
    if (a) actionsRef.current?.querySelector<HTMLButtonElement>(`[data-action="${a.action_id}"]`)?.focus();
  }, []);

  async function openDoc(id: string, title: string) {
    const lines = await api.document(g.state!.scenario_id, id, locale).catch(() => []);
    setDoc({ id, title, lines });
    g.markReviewed(id);
    g.review(id);
  }

  if (g.error) return <div className="px-4"><ErrorState message={g.error === "load" ? t("play.loadError") : t("play.offline")} onRetry={() => g.load(sessionId, locale)} /></div>;
  if (!g.state) return <Loading />;
  const st = g.state;
  const who = g.current ? names[g.current.speaker] ?? NAMES[g.current.speaker] : null;
  const actions = g.busy ? [] : st.available_actions;
  const kindLabel = (k: string) => t(`common.kind_${k}` as "common.kind_evidence");

  return (
    <div className="flex min-h-svh flex-col">
      <header className="grid grid-cols-[auto_1fr_auto] items-center gap-x-6 gap-y-2 border-b border-hairline px-4 py-3 sm:px-8">
        <Link href={`/cases/${st.scenario_id}`} className="flex items-center text-ink-muted no-underline hover:text-paper"><ChevronLeft className="size-4" />{t("play.exit")}</Link>
        <p className="truncate">{t("play.stage", { index: st.stage_index, count: st.stage_count })}: <strong>{st.stage_title}</strong></p>
        <p className="relative flex items-center gap-2 text-xl text-gold">
          <span className="sr-only">{t("play.score")}:</span><span className="star-icon" aria-hidden /><span className="pix">{st.score}</span>
          {g.scorePop && <span key={g.scorePop.key} className="score-pop is-on pix" aria-live="polite">+{g.scorePop.delta}</span>}
        </p>
        <div className="stage-track col-span-3" aria-hidden><span style={{ width: `${(st.stage_index / st.stage_count) * 100}%` }} /></div>
      </header>

      <main id="main" className="mx-auto w-full max-w-6xl flex-1 px-2 pb-24 pt-4 sm:px-6">
        <div className="frame">
          <Court theme="night" mode="play" className="frame__scene" onClick={onSceneClick} onReady={g.setCourt} names={tagNames} label={t("play.evidenceTable")} />
          <div className="frame__tools">
            <Button variant="outline" className={cn("bg-navy/85", g.newEvidence.length > 0 && "has-new")} onClick={() => setDrawer(true)} aria-expanded={drawer}>
              <FileText />{t("play.evidence")}
            </Button>
            {!st.finished && askable.length > 0 && (
              <Button variant="outline" className="bg-navy/85" onClick={() => setAsking(true)} aria-expanded={asking}>
                <MessagesSquare />{t("npc.open")}
              </Button>
            )}
          </div>
          {g.note && (
            <div className="note-card" role="status">
              <p className="mb-2 text-[0.95rem]">{g.note.text}</p>
              <button type="button" className="font-bold text-[#7a5f0e] underline" onClick={() => openLegal(g.note!.citation_id, st.legal_date)}>{t("common.openArticle")}</button>
            </div>
          )}
          {g.toast && <div key={g.toast.key} className="stage-toast is-on" aria-live="polite">{g.toast.title}</div>}
        </div>
        {/* below the scene, never over it: nametags, speech bubbles and the evidence table stay visible */}
        <div className="dialogue" onClick={() => g.advance()} aria-live="polite">
          {g.current && (
            <>
              {who?.name && <p className="mb-1 font-bold text-gold">{who.name} <span className="text-sm font-normal text-ink-muted">{who.role}</span></p>}
              <p className="max-w-[70ch] text-[1.1em]">{g.typed}</p>
              {g.waiting && <span className="dialogue__next">{t("play.continueHint")}</span>}
            </>
          )}
        </div>

        <div ref={actionsRef} aria-busy={g.busy} aria-label={t("common.kind_continue")}
          className={cn("mx-auto mt-4 flex min-h-14 max-w-5xl flex-wrap justify-center gap-2 transition-opacity", g.busy && "opacity-40")}>
          {actions.map((a, i) => (
            <div key={a.action_id} className="flex overflow-hidden rounded-md border border-paper/20 bg-navy-2">
              <button type="button" data-action={a.action_id} autoFocus={i === 0}
                onClick={() => (a.kind === "decision" ? setDecision(a) : a.action_id.startsWith("review_") && a.evidence_id ? openDoc(a.evidence_id, a.label) : g.dispatch(a.action_id))}
                onKeyDown={(e) => {
                  if (!["ArrowRight", "ArrowLeft", "ArrowDown", "ArrowUp"].includes(e.key)) return;
                  const list = Array.from(actionsRef.current?.querySelectorAll<HTMLButtonElement>("[data-action]") ?? []);
                  const d = e.key === "ArrowRight" || e.key === "ArrowDown" ? 1 : -1; e.preventDefault();
                  list[(list.indexOf(e.currentTarget) + d + list.length) % list.length]?.focus();
                }}
                className={cn("flex min-h-12 items-center gap-2.5 px-4 py-2 text-left hover:bg-navy-3", a.kind === "continue" && "text-ink-muted")}>
                <span className={cn("rounded-sm border border-hairline px-1.5 py-0.5 text-xs", a.kind === "motion" ? "text-teal" : "text-gold")}>{kindLabel(a.kind)}</span>
                {a.label}
              </button>
              {a.hint_citation_ids[0] && (
                <button type="button" className="w-11 border-l border-paper/10 font-bold text-gold hover:bg-navy-3" aria-label={t("common.whichRule")} title={t("common.whichRule")}
                  onClick={() => openLegal(a.hint_citation_ids[0], st.legal_date)}>§</button>
              )}
            </div>
          ))}
        </div>
      </main>

      <Sheet open={drawer} onOpenChange={setDrawer}>
        <SheetContent side="left" className="w-[min(26rem,92vw)] border-hairline bg-navy-2 sm:max-w-none">
          <SheetHeader><SheetTitle>{t("play.evidence")}</SheetTitle></SheetHeader>
          <ul className="grid gap-2 px-4">
            {st.evidence.map((e) => (
              <li key={e.id}>
                <button type="button" onClick={() => openDoc(e.id, e.title)}
                  className={cn("flex min-h-12 w-full items-center justify-between gap-3 rounded-md border bg-navy px-4 py-3 text-left hover:border-gold",
                    g.newEvidence.includes(e.id) ? "border-terra" : "border-paper/15")}>
                  <span>{e.title}</span>
                  <span className="text-xs text-teal">{g.newEvidence.includes(e.id) ? <span className="text-terra">{t("play.newEvidence")}</span> : e.reviewed ? t("play.reviewed") : ""}</span>
                </button>
              </li>
            ))}
          </ul>
        </SheetContent>
      </Sheet>

      <Dialog open={!!doc} onOpenChange={(o) => !o && setDoc(null)}>
        {/* one document style for every piece of evidence: same font (the user's UI font), left-aligned title */}
        <DialogContent className="paper-doc border-0">
          <DialogHeader className="text-left"><DialogTitle className="border-b border-[#d8cfb8] pb-2 text-navy">{doc?.title}</DialogTitle><DialogDescription className="sr-only">{t("play.docTitle")}</DialogDescription></DialogHeader>
          <div className="doc-body space-y-1.5">{doc?.lines.map((l, i) => <p key={i}>{l}</p>)}</div>
        </DialogContent>
      </Dialog>

      <NpcPanel open={asking && !st.finished} onOpenChange={setAsking} sessionId={sessionId} characters={askable} />

      <DecisionDialog key={decision?.action_id ?? "none"} action={decision} onClose={() => setDecision(null)} onConfirm={(option) => { const id = decision!.action_id; setDecision(null); g.dispatch(id, { option }); }} legalDate={st.legal_date} />
    </div>
  );
}

function DecisionDialog({ action, onClose, onConfirm, legalDate }: { action: ActionView | null; onClose: () => void; onConfirm: (option: string) => void; legalDate: string }) {
  const t = useTranslations();
  const openLegal = useUi((s) => s.openLegal);
  const [choice, setChoice] = useState<string | null>(null);
  return (
    <Dialog open={!!action} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="border-hairline bg-navy-2 sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="text-2xl">{t("play.decisionTitle")}</DialogTitle>
          <DialogDescription>{t("play.decisionLead")}</DialogDescription>
        </DialogHeader>
        <div className="grid gap-2" role="radiogroup">
          {action?.options?.map((o) => (
            <div key={o.id} className="flex overflow-hidden rounded-md border border-paper/20">
              <button type="button" role="radio" aria-checked={choice === o.id} onClick={() => setChoice(o.id)}
                className="min-h-12 flex-1 px-4 py-3 text-left aria-checked:bg-gold aria-checked:font-bold aria-checked:text-navy">{o.label}</button>
              {action.hint_citation_ids[0] && (
                <button type="button" className="flex items-center gap-1 border-l border-paper/15 px-3 text-sm text-gold" onClick={() => openLegal(action.hint_citation_ids[0], legalDate)}>
                  <Scale className="size-4" aria-hidden />{t("common.whichRule")}
                </button>
              )}
            </div>
          ))}
        </div>
        <DialogFooter><Button size="lg" className="h-11 px-6" disabled={!choice} onClick={() => choice && onConfirm(choice)}>{t("play.confirm")}</Button></DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
