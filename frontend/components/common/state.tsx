"use client";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { useUi } from "@/store/ui";

export function Loading() {
  const t = useTranslations("common");
  return <p role="status" className="py-16 text-center text-ink-muted">{t("loading")}</p>;
}

export function ErrorState({ onRetry, message }: { onRetry?: () => void; message?: string }) {
  const t = useTranslations("common");
  return (
    <div role="alert" className="mx-auto my-16 max-w-md rounded-lg border border-terra/40 bg-terra/10 p-6 text-center">
      <p className="mb-4">{message ?? t("networkError")}</p>
      {onRetry && <Button onClick={onRetry}>{t("retry")}</Button>}
    </div>
  );
}

/** Small chip that opens the shared LegalPanel. */
export function CitationChip({ id, label, date }: { id: string; label?: string; date?: string | null }) {
  const open = useUi((s) => s.openLegal);
  const text = label ?? id.split(".").pop();
  return (
    <button type="button" onClick={() => open(id, date ?? null)}
      className="inline-flex min-h-8 items-center gap-1 rounded border border-hairline px-2 py-1 text-left text-sm text-gold underline-offset-2 hover:underline">
      § {text}
    </button>
  );
}

export function PageTitle({ title, lead }: { title: string; lead?: string }) {
  return (
    <div className="mb-8">
      <h1 className="text-3xl font-extrabold sm:text-4xl">{title}</h1>
      {lead && <p className="mt-3 max-w-[60ch] text-ink-muted">{lead}</p>}
    </div>
  );
}
