import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";

export default function NotFound() {
  const t = useTranslations("common");
  return (
    <main className="grid min-h-svh place-items-center p-6 text-center">
      <div><p className="pix text-6xl text-gold">404</p><Link href="/" className="mt-6 inline-block text-gold underline">{t("brand")}</Link></div>
    </main>
  );
}
