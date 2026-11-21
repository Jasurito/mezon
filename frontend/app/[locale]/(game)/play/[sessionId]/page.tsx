"use client";
import { useLocale } from "next-intl";
import { useParams } from "next/navigation";
import { Loading } from "@/components/common/state";
import { PlayScreen } from "@/components/play/play-screen";
import { SituationScreen } from "@/components/play/situation-screen";
import { useLoad } from "@/hooks/use-load";
import { api, type Locale } from "@/lib/api";

/** Court cases play in the courtroom; life situations (audience "public") get the step-by-step situation screen. */
export default function PlayPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const locale = useLocale() as Locale;
  const { data: audience, error } = useLoad(
    () => api.session(sessionId, locale).then((s) => api.scenario(s.scenario_id, locale)).then((d) => d.audience ?? "professional"),
    [sessionId],
  );
  // on any error the court screen shows its own error / retry state
  if (error) return <PlayScreen sessionId={sessionId} />;
  if (!audience) return <Loading />;
  return audience === "public" ? <SituationScreen sessionId={sessionId} /> : <PlayScreen sessionId={sessionId} />;
}
