/** User display settings (v1: fonts). Applied as data-attributes / CSS vars on <html>; see app/globals.css. */
export const FONT_FAMILIES = ["commissioner", "onest", "plex", "serif", "nunito"] as const;
export const LINE_HEIGHTS = ["compact", "normal", "relaxed"] as const;
export const SIZE_MIN = 0.875, SIZE_MAX = 1.375, SIZE_STEP = 0.0625;

export interface Settings { family: (typeof FONT_FAMILIES)[number]; size: number; lineHeight: (typeof LINE_HEIGHTS)[number] }
export const DEFAULT_SETTINGS: Settings = { family: "commissioner", size: 1, lineHeight: "normal" };
export const SETTINGS_KEY = "mezon.settings";

export function applySettings(s: Settings) {
  const el = document.documentElement;
  el.dataset.font = s.family;
  el.dataset.lh = s.lineHeight;
  el.style.setProperty("--ui-scale", String(s.size));
}

/** Runs in <head> before first paint, so the chosen font/size never flashes. Keep in sync with applySettings. */
export const SETTINGS_BOOT_SCRIPT = `try{var s=JSON.parse(localStorage.getItem(${JSON.stringify(SETTINGS_KEY)})||"null");s=s&&s.state;if(s){var e=document.documentElement;if(s.family)e.dataset.font=s.family;if(s.lineHeight)e.dataset.lh=s.lineHeight;if(s.size)e.style.setProperty("--ui-scale",String(s.size));}}catch(_){}`;
