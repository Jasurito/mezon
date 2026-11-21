import { Gavel, Send } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { api, ApiError, NPC_MAX_LEN, type NpcAnswer } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useGame } from "@/store/game";

export interface Askable { id: string; name: string; role: string }
type Msg = { id: number; from: "me"; text: string } | { id: number; from: "npc"; answer: NpcAnswer };

/** example questions per character id; the scenario's own questions stay hidden (asking is the exercise) */
const EXAMPLES = {
  plaintiff: ["ex_plaintiff_1", "ex_plaintiff_2"],
  defendant_rep: ["ex_defendant_1", "ex_defendant_2"],
} as const;

/**
 * Free questions to the characters (backend §5.6): the answer is built only from the scenario's facts and does
 * not change the game. A key question comes back with `suggested_action_id`: the player can then ask it
 * officially in court, which is a normal scored game action.
 */
export function NpcPanel({ open, onOpenChange, sessionId, characters }: {
  open: boolean; onOpenChange: (o: boolean) => void; sessionId: string; characters: Askable[];
}) {
  const t = useTranslations("npc");
  const [who, setWho] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [threads, setThreads] = useState<Record<string, Msg[]>>({});
  const listRef = useRef<HTMLOListElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const seq = useRef(0);
  const current = who ?? characters[0]?.id ?? null;
  const person = characters.find((c) => c.id === current);
  const thread = current ? threads[current] ?? [] : [];
  const examples = current && current in EXAMPLES ? EXAMPLES[current as keyof typeof EXAMPLES] : null;
  const available = useGame((s) => s.state?.available_actions);

  useEffect(() => { listRef.current?.lastElementChild?.scrollIntoView({ block: "nearest" }); }, [thread.length, sending]);

  // the scene follows the conversation: camera on the person asked, back to the room when the panel closes
  useEffect(() => {
    const { court, busy: queueBusy } = useGame.getState();
    if (queueBusy) return;
    court?.focus(open ? current : null);
  }, [open, current]);

  const push = (id: string, m: Msg) => setThreads((all) => ({ ...all, [id]: [...(all[id] ?? []), m] }));

  async function ask(e?: { preventDefault(): void }) {
    e?.preventDefault();
    const q = text.trim();
    if (!current || !q || sending) return;
    push(current, { id: ++seq.current, from: "me", text: q });
    setText(""); setSending(true);
    try {
      const answer = await api.askNpc(sessionId, current, q);
      push(current, { id: ++seq.current, from: "npc", answer });
      const { court, busy: queueBusy } = useGame.getState();
      if (!queueBusy && court) { court.focus(answer.speaker); court.talk(answer.speaker, true); setTimeout(() => court.talk(answer.speaker, false), 1400); }
    } catch (err) {
      setText(q);
      toast.error(err instanceof ApiError && err.code === "SESSION_FINISHED" ? t("finished") : t("error"));
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  function askInCourt(actionId: string) {
    onOpenChange(false);
    useGame.getState().enqueue(actionId); // after the current dialogue, if one is playing
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" overlay={false} className="flex w-[min(28rem,94vw)] shadow-2xl flex-col gap-0 border-hairline bg-navy-2 sm:max-w-none">
        <SheetHeader className="border-b border-hairline">
          <SheetTitle>{t("title")}</SheetTitle>
          <SheetDescription>{t("lead")}</SheetDescription>
          <div role="radiogroup" aria-label={t("who")} className="mt-2 flex flex-wrap gap-2">
            {characters.map((c) => (
              <button key={c.id} type="button" role="radio" aria-checked={c.id === current} onClick={() => setWho(c.id)}
                className="min-h-10 rounded-md border border-paper/20 px-3 py-1.5 text-left text-sm hover:border-gold aria-checked:border-gold aria-checked:bg-gold aria-checked:font-bold aria-checked:text-navy">
                {c.name}<span className="block text-xs font-normal opacity-75">{c.role}</span>
              </button>
            ))}
          </div>
        </SheetHeader>

        <ol ref={listRef} className="grid flex-1 content-start gap-3 overflow-y-auto px-4 py-4" aria-live="polite">
          {thread.length === 0 && examples && (
            <li className="grid gap-2">
              <p className="text-sm text-ink-muted">{t("examples")}</p>
              {examples.map((k) => (
                <button key={k} type="button" onClick={() => { setText(t(k)); inputRef.current?.focus(); }}
                  className="rounded-md border border-dashed border-paper/25 px-3 py-2 text-left text-sm hover:border-gold">{t(k)}</button>
              ))}
            </li>
          )}
          {thread.map((m) => m.from === "me" ? (
            <li key={m.id} className="ml-8 justify-self-end rounded-md rounded-br-none bg-navy-3 px-3 py-2">{m.text}</li>
          ) : (
            <li key={m.id} className="mr-6 rounded-md rounded-bl-none bg-paper px-3 py-2 text-navy">
              <p className="mb-0.5 text-sm font-bold">{person?.name}</p>
              <p>{m.answer.text}</p>
              <p className="mt-1.5 text-xs text-[#5b5544]">
                {m.answer.question_id === "unknown" ? t("unknown") : m.answer.ai_generated ? t("aiNote") : t("scriptNote")}
              </p>
              {m.answer.suggested_action_id && available?.some((a) => a.action_id === m.answer.suggested_action_id) && (
                <Button size="sm" className="mt-2 gap-1.5" onClick={() => askInCourt(m.answer.suggested_action_id!)}>
                  <Gavel className="size-4" aria-hidden />{t("askInCourt")}
                </Button>
              )}
            </li>
          ))}
          {sending && <li className="mr-6 w-16 rounded-md bg-paper px-3 py-2 text-center font-bold tracking-widest text-navy" aria-label={t("thinking")}>…</li>}
        </ol>

        <form onSubmit={ask} className="grid gap-2 border-t border-hairline p-4">
          <label htmlFor="npc-q" className="sr-only">{t("placeholder")}</label>
          <textarea id="npc-q" ref={inputRef} rows={2} maxLength={NPC_MAX_LEN} value={text} disabled={!current}
            placeholder={t("placeholder")}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) { e.preventDefault(); ask(); } }}
            className="min-h-16 w-full resize-none rounded-md border border-paper/20 bg-navy px-3 py-2 outline-none placeholder:text-ink-muted focus-visible:border-gold focus-visible:ring-2 focus-visible:ring-gold/40" />
          <div className="flex items-center justify-between gap-3">
            <span className={cn("text-xs text-ink-muted", text.length > NPC_MAX_LEN - 50 && "text-terra")}>{text.length}/{NPC_MAX_LEN}</span>
            <Button type="submit" disabled={!text.trim() || sending || !current} className="gap-1.5"><Send className="size-4" aria-hidden />{t("send")}</Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  );
}
