"use client";
import { FileText } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useState } from "react";
import { useLoad } from "@/hooks/use-load";
import { ErrorState, Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { useRouter } from "@/i18n/navigation";
import { api, type ScenarioDetail } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useUser } from "@/store/user";

const fmt = (iso: string) => iso.split("-").reverse().join(".");

export default function CasePage() {
  const t = useTranslations("case");
  const locale = useLocale();
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const ensureUser = useUser((s) => s.ensureUser);
  const { data, error, retry: load } = useLoad<ScenarioDetail>(() => api.scenario(id, locale), [id, locale]);
  const [startFailed, setStartFailed] = useState(false);
  const failed = error || startFailed;
  const [starting, setStarting] = useState<"test" | "play" | null>(null);


  async function start(withTest: boolean) {
    setStarting(withTest ? "test" : "play");
    try {
      const user_id = await ensureUser();
      const s = await api.createSession({ user_id, scenario_id: id, locale });
      router.push(withTest ? `/cases/${id}/pretest?session=${s.session_id}` : `/play/${s.session_id}`);
    } catch { setStarting(null); setStartFailed(true); }
  }

  if (failed) return <ErrorState onRetry={load} />;
  if (!data) return <Loading />;
  return (
    <article className="grid gap-10 lg:grid-cols-[1.4fr_1fr]">
      <div>
        <p className="text-sm text-ink-muted">{data.fictional_notice}</p>
        <h1 className="mt-2 text-4xl font-extrabold">{data.title}</h1>
        <section className="mt-8" aria-labelledby="story">
          <h2 id="story" className="mb-2 text-lg font-bold text-gold">{t("story")}</h2>
          <p className="max-w-[62ch] text-lg">{data.story}</p>
        </section>
        <section className="mt-8" aria-labelledby="parts">
          <h2 id="parts" className="mb-3 text-lg font-bold text-gold">{t("participants")}</h2>
          <ul className="grid gap-2 sm:grid-cols-2">
            {data.characters.map((c) => {
              const me = c.id === data.player_role.character_id;
              return (
                <li key={c.id} className={cn("rounded-md border px-4 py-3", me ? "border-gold bg-gold/10" : "border-paper/10")}>
                  <span className="block font-semibold">{me ? data.player_role.title : c.name}</span>
                  <span className="text-sm text-ink-muted">{c.role}</span>
                </li>
              );
            })}
          </ul>
        </section>
        <section className="mt-8" aria-labelledby="claims">
          <h2 id="claims" className="mb-3 text-lg font-bold text-gold">{t("claims")}</h2>
          <dl className="grid gap-3">
            {data.claims.map((c) => (
              <div key={c.side} className="border-l-2 border-hairline pl-4">
                <dt className="text-sm text-ink-muted">{t(c.side)}</dt><dd>{c.text}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>

      <aside className="space-y-8">
        <div className="rounded-lg border border-hairline bg-navy-2 p-6">
          <p className="mb-4 text-sm text-ink-muted">{t("testHint")}</p>
          <div className="grid gap-2">
            <Button size="lg" className="h-12 text-base" disabled={!!starting} onClick={() => start(true)}>{t("withTest")}</Button>
            <Button size="lg" variant="outline" className="h-12 text-base" disabled={!!starting} onClick={() => start(false)}>{t("withoutTest")}</Button>
          </div>
        </div>
        <section aria-labelledby="docs">
          <h2 id="docs" className="mb-3 text-lg font-bold text-gold">{t("documents")}</h2>
          <ul className="grid gap-1.5">
            {data.documents.map((d) => (<li key={d.id} className="flex items-center gap-2"><FileText className="size-4 text-ink-muted" aria-hidden />{d.title}</li>))}
          </ul>
        </section>
        <section aria-labelledby="acts">
          <h2 id="acts" className="mb-3 text-lg font-bold text-gold">{t("acts")}</h2>
          <ul className="grid gap-2">
            {data.legal_acts.map((a) => (
              <li key={a.document_key}>{a.source_url ? <a href={a.source_url} target="_blank" rel="noopener noreferrer" className="hover:text-gold">{a.title}</a> : a.title}</li>
            ))}
          </ul>
          <p className="mt-3 text-sm text-ink-muted">{t("legalDate", { date: fmt(data.legal_date) })}</p>
        </section>
      </aside>
    </article>
  );
}
