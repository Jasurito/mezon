"use client";
import { Printer } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

const DEMANDS = ["replace", "repair", "reduce", "refund"] as const;
type Demand = (typeof DEMANDS)[number];
type Field = "shop" | "name" | "contact" | "product" | "date" | "problem";
const FIELDS: Field[] = ["shop", "name", "contact", "product", "date", "problem"];

/**
 * After a life situation: the person's own written claim to a seller (consumer protection law, art. 13 remedies),
 * filled in on the page and printed in two copies. A blank stays a visible line, so a half-filled letter still prints.
 */
export function ClaimLetter() {
  const t = useTranslations("letter");
  const [v, setV] = useState<Record<Field, string>>({ shop: "", name: "", contact: "", product: "", date: "", problem: "" });
  const [demand, setDemand] = useState<Demand>("replace");
  const blank = (s: string) => s.trim() || "________________";

  return (
    <section className="mt-10" aria-labelledby="letter-title">
      <h2 id="letter-title" className="text-xl font-bold">{t("title")}</h2>
      <p className="mt-1 max-w-[62ch] text-ink-muted">{t("lead")}</p>

      <div className="mt-5 grid gap-6 xl:grid-cols-2">
        <div className="grid content-start gap-3 print:hidden">
          {FIELDS.map((f) => (
            <div key={f} className="grid gap-1.5">
              <Label htmlFor={`letter-${f}`}>{t(`f_${f}`)}</Label>
              <Input id={`letter-${f}`} value={v[f]} placeholder={t(`p_${f}`)} onChange={(e) => setV({ ...v, [f]: e.target.value })} className="h-11 bg-navy-2" />
            </div>
          ))}
          <fieldset className="grid gap-1.5">
            <legend className="mb-1.5 text-sm font-medium">{t("f_demand")}</legend>
            <div role="radiogroup" className="grid gap-2 sm:grid-cols-2">
              {DEMANDS.map((d) => (
                <button key={d} type="button" role="radio" aria-checked={demand === d} onClick={() => setDemand(d)}
                  className="min-h-11 rounded-md border border-paper/20 px-3 py-2 text-left text-sm hover:border-gold aria-checked:border-gold aria-checked:bg-gold aria-checked:font-semibold aria-checked:text-navy">
                  {t(`d_${d}`)}
                </button>
              ))}
            </div>
          </fieldset>
        </div>

        <div>
          <article className="letter-print paper-doc rounded-md px-6 py-6 leading-relaxed shadow-lg" aria-label={t("preview")}>
            <p className="text-right">{t("to")}: {blank(v.shop)}</p>
            <p className="text-right">{t("from")}: {blank(v.name)}, {blank(v.contact)}</p>
            <h3 className="my-5 text-center text-lg font-bold tracking-wide">{t("heading")}</h3>
            <p>{t("body1", { date: blank(v.date), product: blank(v.product) })}</p>
            <p className="mt-2">{t("body2", { problem: blank(v.problem) })}</p>
            <p className="mt-2">{t("body3", { demand: t(`text_${demand}`) })}</p>
            <p className="mt-2">{t("body4")}</p>
            <p className="mt-4 text-sm">{t("attachments")}</p>
            <div className="mt-8 grid grid-cols-2 gap-4 text-sm">
              <p>{t("dateLine")}: ____________</p><p>{t("signLine")}: ____________</p>
            </div>
            <p className={cn("mt-6 border-t border-dashed border-[#c3b89a] pt-3 text-sm")}>{t("receivedLine")}: ____________________</p>
          </article>
          <div className="mt-4 flex flex-wrap items-center gap-3 print:hidden">
            <Button onClick={() => window.print()} className="h-11 gap-2 px-5"><Printer className="size-4" aria-hidden />{t("print")}</Button>
            <p className="max-w-[42ch] text-sm text-ink-muted">{t("twoCopies")}</p>
          </div>
          <p className="mt-3 text-xs text-ink-muted print:hidden">{t("disclaimer")}</p>
        </div>
      </div>
    </section>
  );
}
