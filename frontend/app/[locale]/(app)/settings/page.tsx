"use client";
import { RotateCcw } from "lucide-react";
import { useTranslations } from "next-intl";
import { PageTitle } from "@/components/common/state";
import { LanguageSwitcher } from "@/components/site/language-switcher";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import { FONT_FAMILIES, LINE_HEIGHTS, MOTIONS, SIZE_MAX, SIZE_MIN, SIZE_STEP } from "@/lib/settings";
import { cn } from "@/lib/utils";
import { useSettings } from "@/store/settings";
import { useMounted } from "@/hooks/use-load";

const FONT_VAR: Record<(typeof FONT_FAMILIES)[number], string> = {
  commissioner: "var(--font-commissioner)", onest: "var(--font-onest)", plex: "var(--font-plex)", serif: "var(--font-serif)", nunito: "var(--font-nunito)",
};

export default function SettingsPage() {
  const t = useTranslations("settings");
  const s = useSettings();
  const mounted = useMounted(); // persisted values are only known on the client
  if (!mounted) return <PageTitle title={t("title")} lead={t("lead")} />;

  return (
    <>
      <PageTitle title={t("title")} lead={t("lead")} />
      <div className="grid gap-10 lg:grid-cols-[1fr_24rem]">
        <section aria-labelledby="fonts" className="space-y-9">
          <h2 id="fonts" className="text-xl font-bold">{t("fonts")}</h2>

          <fieldset>
            <legend className="mb-3 font-semibold">{t("family")}</legend>
            <RadioGroup value={s.family} onValueChange={(v) => s.set({ family: v as typeof s.family })} className="grid gap-2 sm:grid-cols-2">
              {FONT_FAMILIES.map((f) => (
                <Label key={f} htmlFor={`f-${f}`}
                  className={cn("flex min-h-14 cursor-pointer items-center gap-3 rounded-md border px-4 py-3 font-normal", s.family === f ? "border-gold bg-gold/10" : "border-paper/15 hover:border-paper/40")}>
                  <RadioGroupItem id={`f-${f}`} value={f} />
                  <span style={{ fontFamily: FONT_VAR[f] }} className="text-lg">{t(`family_${f}`)}</span>
                </Label>
              ))}
            </RadioGroup>
          </fieldset>

          <div>
            <div className="mb-3 flex items-baseline justify-between">
              <Label htmlFor="size" className="text-base font-semibold">{t("size")}</Label>
              <span className="tabular-nums text-ink-muted">{Math.round(s.size * 100)}%</span>
            </div>
            <Slider id="size" min={SIZE_MIN} max={SIZE_MAX} step={SIZE_STEP} value={[s.size]} onValueChange={([v]) => s.set({ size: v })} aria-label={t("size")} />
            <div className="mt-2 flex justify-between text-ink-muted" aria-hidden><span className="text-sm">A</span><span className="text-xl">A</span></div>
          </div>

          <fieldset>
            <legend className="mb-3 font-semibold">{t("lineHeight")}</legend>
            <div className="inline-flex rounded-md border border-paper/15 p-1" role="radiogroup">
              {LINE_HEIGHTS.map((lh) => (
                <button key={lh} type="button" role="radio" aria-checked={s.lineHeight === lh} onClick={() => s.set({ lineHeight: lh })}
                  className="min-h-10 rounded px-4 text-sm aria-checked:bg-gold aria-checked:font-semibold aria-checked:text-navy">{t(`lh_${lh}`)}</button>
              ))}
            </div>
          </fieldset>

          <fieldset>
            <legend className="mb-3 font-semibold">{t("motion")}</legend>
            <div className="inline-flex rounded-md border border-paper/15 p-1" role="radiogroup">
              {MOTIONS.map((m) => (
                <button key={m} type="button" role="radio" aria-checked={s.motion === m} onClick={() => s.set({ motion: m })}
                  className="min-h-10 rounded px-4 text-sm aria-checked:bg-gold aria-checked:font-semibold aria-checked:text-navy">{t(`motion_${m}`)}</button>
              ))}
            </div>
            <p className="mt-2 text-sm text-ink-muted">{t("motionHint")}</p>
          </fieldset>

          <p className="text-sm text-ink-muted">{t("scope")}</p>
          <Button variant="outline" size="lg" onClick={s.reset}><RotateCcw />{t("reset")}</Button>
        </section>

        <aside className="space-y-8">
          <section aria-labelledby="preview" className="rounded-lg border border-hairline bg-navy-2 p-6 lg:sticky lg:top-6">
            <h2 id="preview" className="mb-3 text-sm font-semibold text-ink-muted">{t("preview")}</h2>
            <p className="text-[1.1em]">{t("previewText")}</p>
          </section>
          <section aria-labelledby="lang">
            <h2 id="lang" className="mb-3 font-semibold">{t("language")}</h2>
            <LanguageSwitcher className="w-fit rounded-md border border-paper/15 p-1" />
          </section>
        </aside>
      </div>
    </>
  );
}
