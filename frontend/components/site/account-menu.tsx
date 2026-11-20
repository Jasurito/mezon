"use client";
import { LogOut, Settings, Trophy } from "lucide-react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import { useUser } from "@/store/user";

const initials = (name: string) => name.split(/\s+/).map((p) => p[0]).join("").slice(0, 2).toUpperCase();

/** Sign in / Sign up for guests, avatar menu for signed-in users. */
export function AccountArea({ tone = "app" }: { tone?: "app" | "desk" }) {
  const t = useTranslations();
  const { account, ready, signOut } = useUser();
  const router = useRouter();
  const pathname = usePathname();
  const next = encodeURIComponent(pathname);

  if (!ready) return <div className="h-9 w-40" aria-hidden />;
  if (!account) {
    return tone === "desk" ? (
      <>
        <Link className="desk-btn desk-btn--ghost" href={`/auth/sign-in?next=${next}`}>{t("nav.signIn")}</Link>
        <Link className="desk-btn desk-btn--solid" href={`/auth/sign-up?next=${next}`}>{t("nav.signUp")}</Link>
      </>
    ) : (
      <>
        <Button asChild variant="ghost" size="lg"><Link href={`/auth/sign-in?next=${next}`}>{t("nav.signIn")}</Link></Button>
        <Button asChild size="lg"><Link href={`/auth/sign-up?next=${next}`}>{t("nav.signUp")}</Link></Button>
      </>
    );
  }
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={cn("rounded-full", tone === "desk" && "ring-1 ring-[#4a5370]")} aria-label={t("nav.account")}>
        <Avatar className="size-9"><AvatarFallback className="bg-gold font-semibold text-navy">{initials(account.display_name)}</AvatarFallback></Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-60">
        <DropdownMenuLabel className="font-normal">
          <span className="block font-semibold text-foreground">{account.display_name}</span>
          <span className="block truncate text-xs text-muted-foreground">{account.email}</span>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild><Link href="/dashboard"><Trophy />{t("nav.dashboard")}</Link></DropdownMenuItem>
        <DropdownMenuItem asChild><Link href="/settings"><Settings />{t("nav.settings")}</Link></DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={async () => { await signOut(); toast(t("auth.signedOut")); router.push("/"); }}>
          <LogOut />{t("nav.signOut")}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
