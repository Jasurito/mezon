"use client";
import { useEffect, useRef } from "react";
import type { CourtTheme } from "@/lib/settings";
import { useSettings } from "@/store/settings";
import type { CourtApi } from "@/store/game";
import type { CourtHandle, MountOptions } from "./courtroom";

type Props = Omit<MountOptions, "motion" | "fontFamily" | "theme"> & {
  /** fixed look; by default the user's choice (Settings, "Courtroom theme") */
  theme?: CourtTheme;
  onReady?: (api: CourtApi | null) => void;
  /** nametags: character id -> display name (localized) */
  names?: Record<string, string>;
  className?: string;
  label?: string;
};

/**
 * Client-only Phaser mount. Phaser is imported inside the effect, so it never runs on the server
 * and is code-split away from pages without a courtroom. The game is destroyed on unmount (spec §5).
 */
export function Court({ theme, mode, onClick, onReady, names, className, label }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const handleRef = useRef<CourtHandle | null>(null);
  const clickRef = useRef(onClick);
  const readyRef = useRef(onReady);
  const namesRef = useRef(names);
  const motion = useSettings((s) => s.motion);
  const family = useSettings((s) => s.family);
  const chosen = useSettings((s) => s.courtTheme);
  const look = theme ?? chosen ?? "pixel";
  useEffect(() => { clickRef.current = onClick; readyRef.current = onReady; namesRef.current = names; });

  useEffect(() => {
    let destroyed = false;
    Promise.all([import("phaser"), import("./courtroom"), document.fonts?.ready]).then(([Phaser, { mountCourt }]) => {
      if (destroyed || !ref.current) return;
      const fontFamily = getComputedStyle(document.body).fontFamily;
      const handle = mountCourt(Phaser.default ?? Phaser, ref.current, { theme: look, mode, motion, fontFamily, onClick: (id) => clickRef.current?.(id) });
      handleRef.current = handle;
      if (namesRef.current) handle.setNames(namesRef.current);
      readyRef.current?.(handle);
    });
    return () => { destroyed = true; readyRef.current?.(null); handleRef.current?.destroy(); handleRef.current = null; };
    // the font family and theme are read at mount; remount when the user changes them
  }, [look, mode, motion, family]);

  useEffect(() => { if (names) handleRef.current?.setNames(names); }, [names]);

  return <div ref={ref} className={"court-canvas " + (className ?? "")} role={label ? "img" : undefined} aria-label={label} aria-hidden={label ? undefined : true} />;
}
