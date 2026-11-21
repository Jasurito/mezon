"use client";
import { ChevronLeft, FileText, MessagesSquare, Palette, Scale } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { ErrorState, Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuLabel, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Court } from "@/game/Court";
import { Link, useRouter } from "@/i18n/navigation";
import { api, type ActionView, type Locale } from "@/lib/api";
import { reveal } from "@/lib/reveal";
import { COURT_THEMES, type CourtTheme } from "@/lib/settings";
import { cn } from "@/lib/utils";
import { useGame } from "@/store/game";
import { useSettings } from "@/store/settings";
import { useUi } from "@/store/ui";
import { CaseFile } from "./case-file";
import { NpcPanel, type Askable } from "./npc-panel";
import { SoundToggle } from "./sound-toggle";

const NAMES: Record<string, string> = {};

export function PlayScreen({ sessionId }: { sessionId: string }) {
  const t = useTranslations();
  const locale = useLocale() as Locale;
  const router = useRouter();
  const g = useGame();
  const openLegal = useUi((s) => s.openLegal);
  const [docId, setDocId] = useState<string | null>(null);
  const caseRef = useRef<HTMLElement>(null);
  const [decision, setDecision] = useState<ActionView | null>(null);
  const [names, setNames] = useState<Record<string, { name: string; role: string }>>({});
  const [askable, setAskable] = useState<Askable[]>([]);
  const [asking, setAsking] = useState(false);
  const actionsRef = useRef<HTMLDivElement>(null);
  const dialogueRef = useRef<HTMLDivElement>(null);
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

  // preparation stage: the case materials are the task, so the panel is highlighted until a document is open (spec §4.5)
  const stage = g.state?.stage;

  // finished: after the gavel, go to results
  useEffect(() => {
    if (g.state?.finished && !g.busy && g.queue.length === 0) {
      const id = setTimeout(() => router.push(`/results/${sessionId}`), 1200);
      return () => clearTimeout(id);
    }
  }, [g.state?.finished, g.busy, g.queue.length, router, sessionId]);

  useEffect(() => { if (g.illegal) toast.error(t("play.illegal")); }, [g.illegal, t]);

  // short screens: the dialogue and the choices sit under the scene; scroll them into view when they change
  const line = g.current;
  const choiceKey = g.busy ? "" : (g.state?.available_actions ?? []).map((a) => a.action_id).join("|");
  useEffect(() => { if (line) reveal(dialogueRef.current, dialogueRef.current); }, [line]);
  useEffect(() => { if (choiceKey) reveal(dialogueRef.current, actionsRef.current); }, [choiceKey]);

  // Space / Enter advance the dialogue when focus is not on a control
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.key === " " || e.key === "Enter") && !(e.target as HTMLElement).closest("button, a, input, textarea, [role=dialog]")) { e.preventDefault(); useGame.getState().advance(); }
    };
    window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey);
  }, []);

  const showCaseFile = useCallback(() => {
    const el = caseRef.current; if (!el) return;
    el.scrollIntoView({ block: "nearest", behavior: useSettings.getState().motion === "reduced" ? "auto" : "smooth" });
    el.focus({ preventScroll: true });
  }, []);

  const openDoc = useCallback((id: string) => {
    setDocId(id);
    const g0 = useGame.getState(); g0.markReviewed(id); g0.review(id);
    if (window.matchMedia("(max-width: 1023px)").matches) showCaseFile(); // stacked layout: the reader is below
  }, [showCaseFile]);

  const onSceneClick = useCallback((id: string) => {
    if (id === "evidence_table") {
      const ev = useGame.getState().state?.evidence ?? [];
      if (!docId && ev.length) openDoc((ev.find((e) => !e.reviewed) ?? ev[0]).id);
      return showCaseFile();
    }
    const a = useGame.getState().state?.available_actions.find((x) => x.target_character === id);
    if (a) actionsRef.current?.querySelector<HTMLButtonElement>(`[data-action="${a.action_id}"]`)?.focus();
  }, [docId, openDoc, showCaseFile]);

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
        <p className="relative flex items-center gap-2 text-xl text-gold" title={t("common.scoreHint")}>
          <span className="sr-only">{t("common.scoreHint")}</span><span className="star-icon" aria-hidden /><span className="num">{st.score}</span><span className="num text-sm text-ink-muted">/{st.max_score}</span>
          {g.scorePop && <span key={g.scorePop.key} className="score-pop is-on num" aria-live="polite">+{g.scorePop.delta}</span>}
        </p>
        <div className="stage-track col-span-3" aria-hidden><span style={{ width: `${(st.stage_index / st.stage_count) * 100}%` }} /></div>
      </header>

      <main id="main" className="mx-auto grid w-full max-w-[88rem] flex-1 items-start gap-6 px-2 pb-24 pt-4 sm:px-6 lg:grid-cols-[minmax(0,1fr)_minmax(19rem,24rem)]">
        <div className="min-w-0">
        <div className="frame">
          <Court mode="play" className="frame__scene" onClick={onSceneClick} onReady={g.setCourt} names={tagNames} label={t("play.evidenceTable")} />
          <div className="frame__tools">
            {/* the case materials sit next to the scene on wide screens; on narrow ones this jumps to them */}
            <Button variant="outline" className={cn("bg-navy/85 lg:hidden", g.newEvidence.length > 0 && "has-new")} onClick={showCaseFile}>
              <FileText />{t("play.evidence")}
            </Button>
            <ThemeMenu />
            <SoundToggle />
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
        <div ref={dialogueRef} className="dialogue" onClick={() => g.advance()} aria-live="polite">
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
                onClick={() => (a.kind === "decision" ? setDecision(a) : a.action_id.startsWith("review_") && a.evidence_id ? openDoc(a.evidence_id) : g.dispatch(a.action_id))}
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
        </div>

        <CaseFile ref={caseRef} sessionId={sessionId} locale={locale} evidence={st.evidence} fresh={g.newEvidence}
          selected={docId} onSelect={openDoc} highlight={stage === "PREPARATION" && !docId}
          className="max-lg:h-[32rem] lg:sticky lg:top-4 lg:h-[calc(100svh-8rem)]" />
      </main>

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

/** Courtroom theme switch in the game toolbar (same setting as in Settings). */
function ThemeMenu() {
  const t = useTranslations("settings");
  const theme = useSettings((s) => s.courtTheme);
  const set = useSettings((s) => s.set);
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="bg-navy/85" aria-label={t("theme")}><Palette /><span className="max-sm:hidden">{t(`theme_${theme}`)}</span></Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-52">
        <DropdownMenuLabel>{t("theme")}</DropdownMenuLabel>
        <DropdownMenuRadioGroup value={theme} onValueChange={(v) => set({ courtTheme: v as CourtTheme })}>
          {COURT_THEMES.map((id) => <DropdownMenuRadioItem key={id} value={id}>{t(`theme_${id}`)}</DropdownMenuRadioItem>)}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
