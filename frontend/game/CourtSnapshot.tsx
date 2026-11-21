"use client";
import { useEffect, useState } from "react";
import type { CourtTheme } from "@/lib/settings";

/*
 * A still picture of a courtroom theme for galleries (home page, settings): the scene is mounted once off-screen,
 * captured and destroyed, so a page with several themes keeps at most one extra WebGL context alive at a time.
 * Pictures are cached per theme for the session.
 */
const cache = new Map<CourtTheme, string>();
let chain: Promise<unknown> = Promise.resolve();

function capture(theme: CourtTheme): Promise<string | null> {
  const hit = cache.get(theme);
  if (hit) return Promise.resolve(hit);
  const job = chain.then(async () => {
    if (cache.has(theme)) return cache.get(theme)!;
    const [Phaser, { mountCourt }] = await Promise.all([import("phaser"), import("./courtroom")]);
    const el = document.createElement("div");
    el.style.cssText = "position:fixed;left:-10000px;top:0;width:640px;height:360px;pointer-events:none";
    document.body.appendChild(el);
    const handle = mountCourt(Phaser.default ?? Phaser, el, { theme, mode: "hero", motion: "reduced" });
    try {
      const url = await handle.snapshot();
      if (url) cache.set(theme, url);
      return url;
    } finally { handle.destroy(); el.remove(); }
  });
  chain = job.catch(() => null);
  return job;
}

export function CourtSnapshot({ theme, className, alt }: { theme: CourtTheme; className?: string; alt: string }) {
  const [src, setSrc] = useState<string | null>(() => cache.get(theme) ?? null);
  useEffect(() => {
    let live = true;
    if (!cache.has(theme)) capture(theme).then((u) => { if (live && u) setSrc(u); });
    return () => { live = false; };
  }, [theme]);
  const shown = src ?? cache.get(theme) ?? null;
  return shown
    // a data: URL captured in the browser, nothing for next/image to optimise
    // eslint-disable-next-line @next/next/no-img-element
    ? <img src={shown} alt={alt} className={className} draggable={false} />
    : <span role="img" aria-label={alt} className={"block animate-pulse bg-black/10 " + (className ?? "")} />;
}
