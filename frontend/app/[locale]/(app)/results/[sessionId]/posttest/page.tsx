"use client";
import { useTranslations } from "next-intl";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Quiz } from "@/components/common/quiz";
import { Loading } from "@/components/common/state";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { api } from "@/lib/api";

export default function PosttestPage() {
  const t = useTranslations("quiz");
  const { sessionId } = useParams<{ sessionId: string }>();
  const [scenarioId, setScenarioId] = useState<string | null>(null);
  useEffect(() => { api.session(sessionId).then((s) => setScenarioId(s.scenario_id)).catch(() => setScenarioId("consumer_dispute_001")); }, [sessionId]);
  if (!scenarioId) return <Loading />;
  return (
    <Quiz scenarioId={scenarioId} kind="post" footer={(r) => r
      ? <Button asChild size="lg" className="h-11 px-5"><Link href="/dashboard">{t("toDashboard")}</Link></Button>
      : <Link href={`/results/${sessionId}`} className="text-sm text-ink-muted underline underline-offset-4 hover:text-paper">{t("skip")}</Link>} />
  );
}
