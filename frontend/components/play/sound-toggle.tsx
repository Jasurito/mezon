"use client";
import { Volume2, VolumeX } from "lucide-react";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { stopVoice } from "@/lib/voice";
import { useSettings } from "@/store/settings";

/** Character speech on/off in the game toolbar (same setting as in Settings); turning it off stops the current line. */
export function SoundToggle() {
  const t = useTranslations("settings");
  const sound = useSettings((s) => s.sound);
  const set = useSettings((s) => s.set);
  const label = sound ? t("soundTurnOff") : t("soundTurnOn");
  return (
    <Button variant="outline" size="icon" className="bg-navy/85" aria-pressed={sound} aria-label={label} title={label}
      onClick={() => { if (sound) stopVoice(); set({ sound: !sound }); }}>
      {sound ? <Volume2 /> : <VolumeX />}
    </Button>
  );
}
