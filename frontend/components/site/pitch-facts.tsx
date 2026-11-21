"use client";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

/** "N articles of Uzbek law from lex.uz": the live count from /api/health, a plain line while it loads or offline. */
export function ArticleCount() {
  const t = useTranslations("pitch");
  const [count, setCount] = useState<number | null>(null);
  useEffect(() => {
    let live = true;
    api.health().then((h) => { if (live && h.articles) setCount(h.articles); }).catch(() => {});
    return () => { live = false; };
  }, []);
  return <>{count ? t("articles", { count }) : t("articlesPlain")}</>;
}
