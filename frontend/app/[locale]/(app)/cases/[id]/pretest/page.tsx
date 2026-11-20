"use client";
import { useTranslations } from "next-intl";
import { useParams, useSearchParams } from "next/navigation";
import { Quiz } from "@/components/common/quiz";
import { Button } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";

export default function PretestPage() {
  const t = useTranslations("quiz");
  const { id } = useParams<{ id: string }>();
  const session = useSearchParams().get("session");
  const play = session ? `/play/${session}` : `/cases/${id}`;
  return (
    <Quiz scenarioId={id} kind="pre" footer={(r) => r
      ? <Button asChild size="lg" className="h-11 px-5"><Link href={play}>{t("toGame")}</Link></Button>
      : <Link href={play} className="text-sm text-ink-muted underline underline-offset-4 hover:text-paper">{t("skip")}</Link>} />
  );
}
