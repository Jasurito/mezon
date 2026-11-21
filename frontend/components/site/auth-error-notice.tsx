"use client";
import { useTranslations } from "next-intl";
import { useEffect } from "react";
import { toast } from "sonner";
import { useRouter } from "@/i18n/navigation";

/**
 * The backend ends every failed Google sign-in with a redirect to `/?auth_error=google`
 * (cancelled consent, expired or reused state, another browser, Google error). Explain it once and
 * offer the way forward, then drop the parameter so a reload or a shared link does not repeat it.
 */
export function AuthErrorNotice() {
  const t = useTranslations("auth");
  const router = useRouter();
  useEffect(() => {
    const url = new URL(window.location.href);
    const reason = url.searchParams.get("auth_error");
    if (!reason) return;
    url.searchParams.delete("auth_error");
    window.history.replaceState(window.history.state, "", url.pathname + url.search + url.hash);
    toast.error(reason === "google" ? t("googleErrorTitle") : t("errorTitle"), {
      id: "auth-error",
      description: t("googleErrorText"),
      duration: 15000,
      action: { label: t("tryAgain"), onClick: () => router.push("/auth/sign-in") },
    });
  }, [t, router]);
  return null;
}
