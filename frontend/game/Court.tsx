"use client";
import { useEffect, useRef } from "react";
import type { CourtApi } from "@/store/game";
import type { MountOptions } from "./courtroom";

/**
 * Client-only Phaser mount. Phaser is imported inside the effect, so it never runs on the server
 * and is code-split away from pages without a courtroom. The game is destroyed on unmount (spec §5).
 */
export function Court({ theme, mode, onClick, onReady, className, label }: MountOptions & { onReady?: (api: CourtApi | null) => void; className?: string; label?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const clickRef = useRef(onClick);
  const readyRef = useRef(onReady);
  useEffect(() => { clickRef.current = onClick; readyRef.current = onReady; });

  useEffect(() => {
    let destroyed = false;
    let handle: (CourtApi & { destroy(): void }) | null = null;
    Promise.all([import("phaser"), import("./courtroom")]).then(([Phaser, { mountCourt }]) => {
      if (destroyed || !ref.current) return;
      handle = mountCourt(Phaser.default ?? Phaser, ref.current, { theme, mode, onClick: (id) => clickRef.current?.(id) });
      readyRef.current?.(handle);
    });
    return () => { destroyed = true; readyRef.current?.(null); handle?.destroy(); };
  }, [theme, mode]);

  return <div ref={ref} className={"court-canvas " + (className ?? "")} role={label ? "img" : undefined} aria-label={label} aria-hidden={label ? undefined : true} />;
}
