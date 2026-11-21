"use client";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Link, useRouter } from "@/i18n/navigation";
import { API_MODE } from "@/lib/api";
import { auth, AuthError, GOOGLE_ENABLED, type AuthErrorCode } from "@/lib/auth";
import { useUser } from "@/store/user";

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function GoogleG() {
  return (
    <svg viewBox="0 0 48 48" className="size-5" aria-hidden>
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
      <path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
    </svg>
  );
}

export function AuthForm({ mode }: { mode: "sign-in" | "sign-up" }) {
  const t = useTranslations("auth");
  const router = useRouter();
  const next = useSearchParams().get("next") || "/dashboard";
  const { userId, setAccount } = useUser();
  const [form, setForm] = useState({ name: "", email: "", password: "", consent: false });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [pending, setPending] = useState<"form" | "google" | null>(null);
  const up = mode === "sign-up";

  function validate() {
    const e: Record<string, string> = {};
    if (up && !form.name.trim()) e.name = t("err_name");
    if (!EMAIL.test(form.email)) e.email = t("err_email");
    if (form.password.length < 8) e.password = t("err_password");
    if (up && !form.consent) e.consent = t("err_consent");
    setErrors(e); return Object.keys(e).length === 0;
  }
  function done(name: string) {
    toast.success(t("welcome", { name }), { description: userId ? t("progressKept") : undefined });
    router.replace(next);
  }
  async function submit(ev: React.FormEvent) {
    ev.preventDefault(); if (!validate()) return;
    setPending("form");
    try {
      const a = up ? await auth.signUp(form.name, form.email, form.password, userId) : await auth.signIn(form.email, form.password, userId);
      setAccount(a); done(a.display_name);
    } catch (e) {
      const code: AuthErrorCode = e instanceof AuthError ? e.code : "network";
      const msg: Record<AuthErrorCode, string> = {
        credentials: t("err_credentials"), exists: t("err_exists"), rate_limited: t("err_rate_limited"),
        invalid: t("err_invalid"), network: t("err_network"),
      };
      setErrors({ form: msg[code] });
    } finally { setPending(null); }
  }
  async function google() {
    setPending("google");
    try { const a = await auth.google(next, userId); if (a) { setAccount(a); toast.info(t("googleDemo")); done(a.display_name); } }
    finally { setPending(null); }
  }

  const field = (id: "name" | "email" | "password", type: string, autoComplete: string) => (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{t(id)}</Label>
      <Input id={id} type={type} autoComplete={autoComplete} value={form[id]} aria-invalid={!!errors[id]} aria-describedby={errors[id] ? `${id}-err` : id === "password" ? "pw-hint" : undefined}
        onChange={(e) => setForm({ ...form, [id]: e.target.value })} className="h-11 bg-navy-2" />
      {id === "password" && !errors.password && <p id="pw-hint" className="text-xs text-ink-muted">{t("passwordHint")}</p>}
      {errors[id] && <p id={`${id}-err`} className="text-sm text-terra">{errors[id]}</p>}
    </div>
  );

  return (
    <div className="mx-auto max-w-md">
      <h1 className="text-3xl font-extrabold">{t(up ? "signUpTitle" : "signInTitle")}</h1>
      <p className="mt-2 text-ink-muted">{t(up ? "signUpLead" : "signInLead")}</p>
      {GOOGLE_ENABLED && (
        <>
          <Button type="button" variant="outline" size="lg" className="mt-8 h-12 w-full gap-3 bg-paper text-base text-navy hover:bg-white hover:text-navy" disabled={!!pending} onClick={google}>
            <GoogleG />{t("google")}
          </Button>
          {API_MODE === "mock" && <p className="mt-2 text-xs text-ink-muted">{t("googleDemo")}</p>}
          <div className="my-6 flex items-center gap-3 text-sm text-ink-muted"><span className="h-px flex-1 bg-paper/15" />{t("or")}<span className="h-px flex-1 bg-paper/15" /></div>
        </>
      )}
      <form noValidate onSubmit={submit} className={GOOGLE_ENABLED ? "grid gap-4" : "mt-8 grid gap-4"}>
        {up && field("name", "text", "name")}
        {field("email", "email", "email")}
        {field("password", "password", up ? "new-password" : "current-password")}
        {up && (
          <div className="grid gap-1.5">
            <div className="flex items-start gap-3">
              <Checkbox id="consent" checked={form.consent} onCheckedChange={(v) => setForm({ ...form, consent: v === true })} aria-invalid={!!errors.consent} className="mt-0.5" />
              <Label htmlFor="consent" className="font-normal leading-snug">{t("consent")}</Label>
            </div>
            {errors.consent && <p className="text-sm text-terra">{errors.consent}</p>}
          </div>
        )}
        {errors.form && <p role="alert" className="rounded-md border border-terra/40 bg-terra/10 px-3 py-2 text-sm">{errors.form}</p>}
        <Button type="submit" size="lg" className="h-12 text-base" disabled={!!pending}>{t(up ? "submitSignUp" : "submitSignIn")}</Button>
      </form>
      <div className="mt-6 flex flex-wrap justify-between gap-3 text-sm">
        <Link href={up ? `/auth/sign-in?next=${encodeURIComponent(next)}` : `/auth/sign-up?next=${encodeURIComponent(next)}`} className="text-gold underline underline-offset-4">{t(up ? "toSignIn" : "toSignUp")}</Link>
        <Link href="/cases" className="text-ink-muted underline underline-offset-4 hover:text-paper">{t("guest")}</Link>
      </div>
    </div>
  );
}
