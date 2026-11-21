"use client";
import { Check, X } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useState } from "react";
import { useLoad } from "@/hooks/use-load";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { api, type QuizAttemptOut, type QuizKind, type QuizOut } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useUser } from "@/store/user";
import { CitationChip, ErrorState, Loading } from "./state";

/** One question per screen, then a summary with explanations and article chips (spec §4.4). */
export function Quiz({ scenarioId, kind, footer }: { scenarioId: string; kind: QuizKind; footer: (r: QuizAttemptOut | null) => React.ReactNode }) {
  const t = useTranslations("quiz");
  const common = useTranslations("common");
  const locale = useLocale();
  const withUser = useUser((s) => s.withUser);
  const { data: quiz, error: loadFailed, retry: load } = useLoad<QuizOut>(() => api.quiz(scenarioId, kind, locale), [scenarioId, kind, locale]);
  const [i, setI] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizAttemptOut | null>(null);
  const [sendFailed, setFailed] = useState(false);
  const failed = loadFailed || sendFailed;
  const [sending, setSending] = useState(false);


  async function submit() {
    if (!quiz) return; setSending(true);
    try { setResult(await withUser((user_id) => api.submitQuiz(scenarioId, { user_id, kind, answers }, locale))); }
    catch { setFailed(true); } finally { setSending(false); }
  }

  if (failed) return <ErrorState onRetry={load} />;
  if (!quiz) return <Loading />;
  const q = quiz.questions[i];
  const last = i === quiz.questions.length - 1;

  if (result) {
    return (
      <section aria-live="polite" className="max-w-3xl">
        <h1 className="text-3xl font-extrabold">{t(kind === "pre" ? "preTitle" : "postTitle")}</h1>
        <p className="mt-2 text-2xl text-gold">{t("result", { score: result.score, max: result.max })}</p>
        {result.learning_gain && (
          <div className="mt-6 rounded-lg border border-hairline bg-navy-2 p-5">
            <h2 className="font-bold">{t("gainTitle")}</h2>
            <p className="mt-1 text-xl">{t("gainValue", { pre: result.learning_gain.pre, post: result.learning_gain.post, max: result.learning_gain.max })}</p>
            <p className="mt-1 text-sm text-ink-muted">{t("gainNote")}</p>
          </div>
        )}
        <ol className="mt-8 grid gap-3">
          {result.review.map((r, n) => {
            const qq = quiz.questions[n];
            const opt = (id: string | null) => qq.options.find((o) => o.id === id)?.text ?? "—";
            return (
              <li key={r.question_id} className={cn("rounded-md border-l-4 bg-navy-2 p-4", r.correct ? "border-teal" : "border-terra")}>
                <p className="flex items-start gap-2 font-semibold">
                  {r.correct ? <Check className="mt-1 size-4 shrink-0 text-teal" aria-label={t("correct")} /> : <X className="mt-1 size-4 shrink-0 text-terra" aria-label={t("wrong")} />}
                  {qq.text}
                </p>
                {!r.correct && <p className="mt-1 text-sm text-ink-muted">{t("yourAnswer")}: {opt(r.chosen_option)}. {t("rightAnswer")}: {opt(r.correct_option)}.</p>}
                <p className="mt-1">{r.explanation}</p>
                <div className="mt-2 flex flex-wrap gap-2">{r.citation_ids.map((c) => <CitationChip key={c} id={c} />)}</div>
              </li>
            );
          })}
        </ol>
        <div className="mt-8 flex flex-wrap gap-3">{footer(result)}</div>
      </section>
    );
  }

  return (
    <section className="max-w-2xl">
      <h1 className="text-3xl font-extrabold">{t(kind === "pre" ? "preTitle" : "postTitle")}</h1>
      <div className="mt-6 flex items-center gap-4">
        <Progress value={((i + 1) / quiz.total) * 100} className="h-1.5" aria-label={t("progress", { current: i + 1, total: quiz.total })} />
        <span className="shrink-0 text-sm text-ink-muted">{t("progress", { current: i + 1, total: quiz.total })}</span>
      </div>
      <fieldset className="mt-8">
        <legend className="text-xl font-semibold">{q.text}</legend>
        <div className="mt-5 grid gap-2">
          {q.options.map((o) => (
            <button key={o.id} type="button" aria-pressed={answers[q.question_id] === o.id}
              onClick={() => setAnswers({ ...answers, [q.question_id]: o.id })}
              className="min-h-12 rounded-md border border-paper/20 px-4 py-3 text-left hover:border-gold aria-pressed:border-gold aria-pressed:bg-gold aria-pressed:font-semibold aria-pressed:text-navy">
              {o.text}
            </button>
          ))}
        </div>
      </fieldset>
      <div className="mt-8 flex flex-wrap items-center gap-3">
        {i > 0 && <Button variant="ghost" size="lg" onClick={() => setI(i - 1)}>{common("back")}</Button>}
        {last ? (
          <Button size="lg" className="h-11 px-5" disabled={!answers[q.question_id] || sending} onClick={submit}>{t("finish")}</Button>
        ) : (
          <Button size="lg" className="h-11 px-5" disabled={!answers[q.question_id]} onClick={() => setI(i + 1)}>{t("next")}</Button>
        )}
        <span className="ml-auto">{footer(null)}</span>
      </div>
    </section>
  );
}
