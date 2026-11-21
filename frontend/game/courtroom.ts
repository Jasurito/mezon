/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Procedural courtroom (Phaser 4) in several themes. No external art: everything is drawn in code.
 * One layout (320x180 world units, camera zoom 4 = 1280x720) and four looks:
 *   pixel    - pixel art at 2 art pixels per unit (twice the old detail), night palette
 *   daylight - the same pixel art in daylight colours
 *   flat     - smooth vector illustration (arched windows, soft shadows)
 *   ink      - line drawing on paper, the site's case-file style
 * Every theme has the flag of Uzbekistan by the bench. Text never lives in the canvas except the nametags.
 */
import type { CourtApi } from "@/store/game";

const W = 320, H = 180;          // world size in units
const ZOOM = 4;                   // rendered at 1280x720
const FOCUS_ZOOM = ZOOM * 1.35;   // camera zoom on the current speaker
const hex = (s: string) => parseInt(s.slice(1), 16);

export type CourtThemeId = "pixel" | "daylight" | "flat" | "ink";
export const COURT_THEMES: CourtThemeId[] = ["pixel", "daylight", "flat", "ink"];
/** older names still accepted by <Court theme=...> */
const ALIASES: Record<string, CourtThemeId> = { night: "pixel" };
type Style = "pixel" | "flat" | "ink";
type Pal = Record<string, string>;

/** lighten (f > 0) or darken (f < 0) a #rrggbb colour */
function mix(c: string, f: number): string {
  const n = hex(c); const ch = [n >> 16, (n >> 8) & 255, n & 255];
  const out = ch.map((v) => Math.round(f >= 0 ? v + (255 - v) * f : v * (1 + f)));
  return "#" + out.map((v) => v.toString(16).padStart(2, "0")).join("");
}

const FLAG = { blue: "#0099B5", white: "#FFFFFF", green: "#1EB53A", red: "#CE1126" };

const PEOPLE_NIGHT = {
  skin: "#D9A47A", hairDark: "#1E1A1A", hairBrown: "#5A3A22", hairGrey: "#AEB6C0",
  robe: "#141A28", suitA: "#24406B", suitB: "#4B5563", casual: "#2F6D5F", coat: "#E6E2D8", shirt: "#F5F1E8",
  tie: "#C9A227", eye: "#141414", eyeWhite: "#F5F1E8", mouth: "#7A3B2E",
};
const SPECS: Record<CourtThemeId, { style: Style; p: number; pal: Pal }> = {
  pixel: { style: "pixel", p: 2, pal: { ...PEOPLE_NIGHT,
    bg: "#0F1B2D", wallA: "#1B2A41", wallB: "#182539", trim: "#2C4062", panel: "#4A321D",
    floorA: "#22324A", floorB: "#1C2A3F", carpet: "#5B1E28", wood: "#6B4A2B",
    sky: "#0A1424", skyLow: "#21365A", moon: "#F2E6B8", star: "#C9A227", curtain: "#6B1F2A", lamp: "#E8C55A",
    emblem: "#C9A227", pole: "#C9A227", paper: "#F5F1E8", bubble: "#F5F1E8", bubbleInk: "#0F1B2D", highlight: "#C9A227" } },
  daylight: { style: "pixel", p: 2, pal: { ...PEOPLE_NIGHT,
    bg: "#EADFC8", wallA: "#EFE4CE", wallB: "#E6D9BE", trim: "#B08A5B", panel: "#8B5A2B",
    floorA: "#D6C4A2", floorB: "#C8B48F", carpet: "#8C2F39", wood: "#9A6634",
    sky: "#8FCBEA", skyLow: "#CDEBF7", moon: "#FFF4C2", star: "#FFFFFF", curtain: "#1F5E73", lamp: "#C9A227",
    emblem: "#B8860B", pole: "#B8860B", paper: "#FFFDF6", bubble: "#FFFDF6", bubbleInk: "#2A1E10", highlight: "#B8860B", day: "1",
    robe: "#151515", suitA: "#22406E", suitB: "#5A6472" } },
  flat: { style: "flat", p: 4, pal: { ...PEOPLE_NIGHT,
    bg: "#13233A", wallA: "#1F3354", wallB: "#172944", trim: "#C9A227", panel: "#2B4468",
    floorA: "#24395A", floorB: "#203352", carpet: "#7A2A36", wood: "#8A5A35",
    sky: "#0E1C33", skyLow: "#2C4A78", moon: "#F2E6B8", star: "#E8C55A", curtain: "#7A2A36", lamp: "#F2D27A",
    emblem: "#E0B93A", pole: "#E0B93A", paper: "#F5F1E8", bubble: "#F5F1E8", bubbleInk: "#13233A", highlight: "#E0B93A",
    skin: "#E0AE86", casual: "#2F8C78", suitA: "#2D5591", suitB: "#5B6678" } },
  ink: { style: "ink", p: 4, pal: {
    bg: "#E4E7DE", wallA: "#E4E7DE", wallB: "#DCE1DD", trim: "#2B3990", panel: "#D3D8E6",
    floorA: "#E4E7DE", floorB: "#D6DBE6", carpet: "#C9CFE6", wood: "#C6CCE2",
    sky: "#F1F3EE", skyLow: "#E1E6F0", moon: "#F1F3EE", star: "#2B3990", curtain: "#B8C0D9", lamp: "#2B3990",
    emblem: "#2B3990", pole: "#2B3990", paper: "#FBFCF8", bubble: "#FBFCF8", bubbleInk: "#2B3990", highlight: "#B3261E",
    skin: "#F1F3EE", hairDark: "#2B3990", hairBrown: "#6F7DB8", hairGrey: "#C6CCE2",
    robe: "#2B3990", suitA: "#9AA5CF", suitB: "#B8C0D9", casual: "#C6CCE2", coat: "#FBFCF8", shirt: "#FBFCF8",
    tie: "#2B3990", eye: "#141A2E", eyeWhite: "#FBFCF8", mouth: "#2B3990", ink: "#2B3990" } },
};

const CAST: Record<string, { x: number; y: number; suit: string; hair: string; style: string }> = {
  judge: { x: 160, y: 76, suit: "robe", hair: "hairGrey", style: "judge" },
  plaintiff: { x: 40, y: 136, suit: "casual", hair: "hairBrown", style: "casual" },
  plaintiff_rep: { x: 78, y: 136, suit: "suitA", hair: "hairDark", style: "suit" },
  defendant_rep: { x: 262, y: 136, suit: "suitB", hair: "hairDark", style: "long" },
  expert: { x: 236, y: 102, suit: "coat", hair: "hairBrown", style: "glasses" },
  secretary: { x: 88, y: 104, suit: "suitB", hair: "hairBrown", style: "long" },
};

/* ------------------------------------------------------------------------------------------------ painter */

/** Draws in world units onto a Graphics that becomes a texture of (w*p) x (h*p) pixels. */
class Painter {
  constructor(public g: any, public style: Style, public p: number, public t: Pal) {}
  col(k: string) { return hex(k.startsWith("#") ? k : this.t[k] ?? "#ff00ff"); }
  tone(k: string, f: number) { return hex(mix(k.startsWith("#") ? k : this.t[k], f)); }
  /** structural box: pixel = crisp rect with a lit top and a dark bottom, flat = rounded, ink = paper fill + ink outline */
  box(x: number, y: number, w: number, h: number, k: string, o: { r?: number; bevel?: boolean; line?: boolean; alpha?: number } = {}) {
    const { g, p } = this; const X = x * p, Y = y * p, Wd = w * p, Hd = h * p;
    g.fillStyle(this.col(k), o.alpha ?? 1);
    if (this.style === "pixel") {
      g.fillRect(Math.round(X), Math.round(Y), Math.round(Wd), Math.round(Hd));
      if (o.bevel) { g.fillStyle(this.tone(k, 0.18), 1); g.fillRect(Math.round(X), Math.round(Y), Math.round(Wd), 1); g.fillStyle(this.tone(k, -0.3), 1); g.fillRect(Math.round(X), Math.round(Y + Hd - 1), Math.round(Wd), 1); }
      return;
    }
    const r = Math.min((o.r ?? 0) * p, Wd / 2, Hd / 2);
    if (r > 0) g.fillRoundedRect(X, Y, Wd, Hd, r); else g.fillRect(X, Y, Wd, Hd);
    if (this.style === "ink" && o.line !== false) { g.lineStyle(0.45 * p, this.col("ink"), 1); if (r > 0) g.strokeRoundedRect(X, Y, Wd, Hd, r); else g.strokeRect(X, Y, Wd, Hd); }
  }
  /** a filled pixel-grid rect (pixel themes only use this for fine detail) */
  px(x: number, y: number, w: number, h: number, k: string, a = 1) { this.g.fillStyle(this.col(k), a); this.g.fillRect(x, y, w, h); }
  circle(x: number, y: number, r: number, k: string, o: { line?: boolean; alpha?: number } = {}) {
    const { g, p } = this; g.fillStyle(this.col(k), o.alpha ?? 1); g.fillCircle(x * p, y * p, r * p);
    if (this.style === "ink" && o.line !== false) { g.lineStyle(0.4 * p, this.col("ink"), 1); g.strokeCircle(x * p, y * p, r * p); }
  }
  ellipse(x: number, y: number, w: number, h: number, k: string, alpha = 1) { this.g.fillStyle(this.col(k), alpha); this.g.fillEllipse(x * this.p, y * this.p, w * this.p, h * this.p); }
  line(x1: number, y1: number, x2: number, y2: number, k: string, w = 0.5, a = 1) { this.g.lineStyle(w * this.p, this.col(k), a); this.g.lineBetween(x1 * this.p, y1 * this.p, x2 * this.p, y2 * this.p); }
  poly(pts: number[], k: string, line = false) {
    const { g, p } = this; const P = []; for (let i = 0; i < pts.length; i += 2) P.push({ x: pts[i] * p, y: pts[i + 1] * p });
    g.fillStyle(this.col(k), 1); g.fillPoints(P, true);
    if (line && this.style === "ink") { g.lineStyle(0.4 * p, this.col("ink"), 1); g.strokePoints(P, true); }
  }
  star(x: number, y: number, r: number, k: string) {
    const pts: number[] = [];
    for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 ? r * 0.45 : r; pts.push(x + Math.cos(a) * rr, y + Math.sin(a) * rr); }
    this.poly(pts, k);
  }
}

/* ------------------------------------------------------------------------------------------------ room */

function flag(pt: Painter, x: number, y: number) {
  // pole with a finial, then the flag of Uzbekistan: blue / red / white / red / green, crescent and 12 stars
  const fw = 30, fh = 15, blue = fh * 0.33, green = fh * 0.33, red = fh * 0.04;
  pt.box(x - 0.6, y - 2, 1.4, 62, "pole", { line: true });
  pt.circle(x + 0.1, y - 2.6, 1.4, "pole");
  pt.box(x - 2.5, y + 58, 5, 2.4, "pole", { r: 0.8 });
  const fx = x + 0.8, fy = y;
  if (pt.style === "pixel") {
    const p = pt.p, X = Math.round(fx * p), Y = Math.round(fy * p), FW = fw * p, FH = fh * p;
    const b = Math.round(blue * p), gr = Math.round(green * p), rd = Math.max(1, Math.round(red * p));
    pt.px(X, Y, FW, FH, FLAG.white);
    pt.px(X, Y, FW, b, FLAG.blue); pt.px(X, Y + b, FW, rd, FLAG.red);
    pt.px(X, Y + FH - gr - rd, FW, rd, FLAG.red); pt.px(X, Y + FH - gr, FW, gr, FLAG.green);
    // wave: every other 6px column a touch darker
    for (let i = 6; i < FW; i += 12) pt.px(X + i, Y, 6, FH, "#000000", 0.08);
    // crescent (white disk minus blue disk) and stars as single pixels in rows of 3/4/5
    pt.g.fillStyle(hex(FLAG.white), 1); pt.g.fillCircle(X + 5, Y + 5, 3.2); pt.g.fillStyle(hex(FLAG.blue), 1); pt.g.fillCircle(X + 6.4, Y + 4.6, 2.9);
    [[3, 1], [4, 4], [5, 7]].forEach(([n, ry]) => { for (let i = 0; i < n; i++) pt.px(X + 12 + (5 - n) + i * 2, Y + ry, 1, 1, FLAG.white); });
    return;
  }
  // smooth flag with a gentle wave
  const wave = (yy: number) => [fx, fy + yy, fx + fw * 0.35, fy + yy - 1.2, fx + fw * 0.7, fy + yy + 0.8, fx + fw, fy + yy - 0.6];
  const band = (y0: number, y1: number, k: string) => { const a = wave(y0), b = wave(y1); pt.poly([...a, b[6], b[7], b[4], b[5], b[2], b[3], b[0], b[1]], k); };
  band(0, blue, FLAG.blue); band(blue, blue + red, FLAG.red); band(blue + red, fh - green - red, FLAG.white);
  band(fh - green - red, fh - green, FLAG.red); band(fh - green, fh, FLAG.green);
  pt.circle(fx + 2.8, fy + 2.4, 1.6, FLAG.white, { line: false }); pt.circle(fx + 3.4, fy + 2.2, 1.45, FLAG.blue, { line: false });
  [[3, 1.4], [4, 2.6], [5, 3.8]].forEach(([n, ry]) => { for (let i = 0; i < n; i++) pt.star(fx + 6.2 + (5 - n) * 0.9 + i * 1.8, fy + ry - 0.6, 0.42, FLAG.white); });
  if (pt.style === "ink") { const a = wave(0), b = wave(fh); pt.g.lineStyle(0.4 * pt.p, pt.col("ink"), 1); pt.g.strokePoints([...[0, 2, 4, 6].map((i) => ({ x: a[i] * pt.p, y: a[i + 1] * pt.p })), ...[6, 4, 2, 0].map((i) => ({ x: b[i] * pt.p, y: b[i + 1] * pt.p }))], true); }
}

/** rectangle with a semicircular top (vector themes); ink adds the outline */
function archShape(pt: Painter, x: number, y: number, w: number, h: number, k: string) {
  const { g, p } = pt; const r = w / 2;
  g.fillStyle(pt.col(k), 1); g.fillRect(x * p, (y + r) * p, w * p, (h - r) * p); g.fillCircle((x + r) * p, (y + r) * p, r * p);
  if (pt.style === "ink") {
    g.lineStyle(0.45 * p, pt.col("ink"), 1); g.beginPath(); g.moveTo(x * p, (y + h) * p); g.lineTo(x * p, (y + r) * p);
    g.arc((x + r) * p, (y + r) * p, r * p, Math.PI, Math.PI * 2, false); g.lineTo((x + w) * p, (y + h) * p); g.closePath(); g.strokePath();
  }
}

function windowAt(pt: Painter, x: number, y: number) {
  const arch = pt.style !== "pixel";
  // curtains
  pt.box(x - 7, y - 4, 6, 60, "curtain", { r: 2 }); pt.box(x + 25, y - 4, 6, 60, "curtain", { r: 2 });
  if (pt.style === "pixel") for (let i = 0; i < 3; i++) { pt.box(x - 6 + i * 2, y - 4, 0.5, 60, mix(pt.t.curtain, -0.25)); pt.box(x + 26 + i * 2, y - 4, 0.5, 60, mix(pt.t.curtain, -0.25)); }
  pt.box(x - 9, y - 6, 42, 3, "trim", { r: 1, bevel: true });
  // frame and glass (vector themes: an arch, round only at the top)
  if (arch) { archShape(pt, x - 2, y - 2, 28, 58, "trim"); archShape(pt, x, y, 24, 54, "sky"); }
  else { pt.box(x - 2, y - 2, 28, 58, "trim", { bevel: true }); pt.box(x, y, 24, 54, "sky"); }
  if (pt.style === "flat") { pt.g.fillGradientStyle(pt.col("sky"), pt.col("sky"), pt.col("skyLow"), pt.col("skyLow"), 1); pt.g.fillRect(x * pt.p, (y + 12) * pt.p, 24 * pt.p, 42 * pt.p); }
  else { pt.box(x, y + 30, 24, 24, "skyLow", { line: false }); if (pt.style === "pixel") pt.box(x, y + 24, 24, 6, mix(pt.t.sky, 0.12)); }
  const day = !!pt.t.day;
  pt.circle(x + 17, y + 13, 3.2, "moon");
  if (day) { [[6, 10, 7], [12, 20, 6], [4, 34, 5]].forEach(([cx, cy, w]) => { pt.ellipse(x + cx, y + cy, w, 2.6, "#FFFFFF", 0.9); pt.ellipse(x + cx + 2, y + cy - 1, w * 0.6, 2.4, "#FFFFFF", 0.9); }); }
  else {
    if (pt.style === "pixel") pt.circle(x + 18.2, y + 12.2, 2.6, "sky", { line: false });
    [[5, 6], [9, 18], [20, 23], [4, 26], [14, 4]].forEach(([sx, sy]) => (pt.style === "pixel" ? pt.box(x + sx, y + sy, 0.5, 0.5, "star") : pt.star(x + sx, y + sy, 0.7, "star")));
  }
  pt.box(x + 11, y + (arch ? 6 : 0), 2, arch ? 48 : 54, "trim", { line: pt.style === "ink" }); pt.box(x, y + 26, 24, 2, "trim", { line: pt.style === "ink" });
  pt.box(x - 3, y + 54, 30, 3, "trim", { r: 1, bevel: true });
}

function emblem(pt: Painter, cx: number, cy: number) {
  // ring with the scales of justice
  pt.circle(cx, cy, 15, pt.style === "ink" ? "paper" : mix(pt.t.emblem, -0.35));
  pt.circle(cx, cy, 13.2, "emblem", { line: false });
  pt.circle(cx, cy, 10.6, "wallA");
  if (pt.style === "pixel") for (let a = 0; a < 16; a++) { const ang = (a / 16) * Math.PI * 2; pt.box(cx + Math.cos(ang) * 11.9 - 0.25, cy + Math.sin(ang) * 11.9 - 0.25, 0.5, 0.5, mix(pt.t.emblem, 0.35)); }
  const k = "emblem";
  pt.box(cx - 0.8, cy - 8, 1.6, 15, k, { line: false });                       // post
  pt.box(cx - 8, cy - 5.5, 16, 1.3, k, { r: 0.6, line: false });               // beam
  pt.circle(cx, cy - 8.6, 1.2, k, { line: false });
  for (const s of [-1, 1]) {
    const px = cx + s * 7;
    pt.line(px, cy - 4.6, px - 2.6, cy + 1, k, 0.35); pt.line(px, cy - 4.6, px + 2.6, cy + 1, k, 0.35);
    pt.poly([px - 3.6, cy + 1, px + 3.6, cy + 1, px + 2.2, cy + 2.8, px - 2.2, cy + 2.8], k);
  }
  pt.box(cx - 4, cy + 6.2, 8, 1.6, k, { r: 0.6, line: false });                // base
}

function drawRoom(scene: any, sp: { style: Style; p: number; pal: Pal }) {
  const g = scene.add.graphics();
  const pt = new Painter(g, sp.style, sp.p, sp.pal);
  const t = sp.pal, P = sp.p;
  // wall
  if (sp.style === "flat") { g.fillGradientStyle(pt.col("wallA"), pt.col("wallA"), pt.col("wallB"), pt.col("wallB"), 1); g.fillRect(0, 0, W * P, 118 * P); }
  else pt.box(0, 0, W, 118, "wallA", { line: false });
  if (sp.style === "pixel") {
    for (let x = 0; x < W; x += 16) { pt.box(x, 0, 8, 84, "wallB"); pt.box(x + 8, 0, 0.5, 84, mix(t.wallA, 0.06)); }
    for (let y = 6; y < 84; y += 12) for (let x = 4; x < W; x += 16) pt.box(x, y, 0.5, 0.5, mix(t.wallB, 0.12));   // damask dots
  } else if (sp.style === "ink") {
    for (let x = 8; x < W; x += 16) pt.line(x, 4, x, 82, "ink", 0.18, 0.35);
  }
  // crown moulding and wainscot
  pt.box(0, 0, W, 4, "trim", { bevel: true, line: false });
  pt.box(0, 84, W, 2.5, "trim", { bevel: true });
  pt.box(0, 86.5, W, 31.5, "panel", { line: false });
  for (let x = 4; x < W; x += 20) {
    if (sp.style === "pixel") { pt.box(x, 90, 14, 24, mix(t.panel, 0.16)); pt.box(x, 90, 14, 0.5, mix(t.panel, 0.32)); pt.box(x, 113.5, 14, 0.5, mix(t.panel, -0.35)); pt.box(x + 13.5, 90, 0.5, 24, mix(t.panel, -0.25)); pt.box(x + 3, 94, 8, 16, mix(t.panel, 0.08)); }
    else pt.box(x, 90, 14, 24, sp.style === "ink" ? "paper" : mix(t.panel, 0.1), { r: 2 });
  }
  windowAt(pt, 34, 18); windowAt(pt, 262, 18);
  emblem(pt, 160, 27);
  // sconces with a warm glow
  [[120, 44], [200, 44]].forEach(([x, y]) => {
    if (sp.style !== "ink") for (let r = 12; r > 2; r -= 3) pt.circle(x, y + 3, r, "lamp", { alpha: 0.05, line: false });
    pt.box(x - 2, y, 4, 6, "lamp", { r: 1 }); pt.box(x - 1, y + 6, 2, 1.2, mix(t.lamp, -0.4), { line: false });
  });
  flag(pt, 120, 54);
  // floor: tiles, a carpet runner to the bench, perspective lines
  pt.box(0, 118, W, 62, "floorA", { line: false });
  if (sp.style === "pixel") {
    for (let y = 118; y < H; y += 8) for (let x = ((y - 118) / 8) % 2 ? 8 : 0; x < W; x += 16) { pt.box(x, y, 8, 8, "floorB"); pt.box(x, y, 8, 0.5, mix(t.floorB, 0.1)); }
  } else if (sp.style === "flat") {
    for (let y = 126; y < H; y += 10) pt.line(0, y, W, y, mix(t.floorA, 0.08), 0.3);
  } else {
    for (let x = -60; x < W; x += 7) pt.line(x, H, x + 62, 118, "ink", 0.15, 0.35);
  }
  pt.box(138, 118, 44, 62, "carpet", { line: sp.style === "ink" });
  if (sp.style === "pixel") { pt.box(140, 118, 0.5, 62, mix(t.carpet, 0.3)); pt.box(179.5, 118, 0.5, 62, mix(t.carpet, 0.3)); for (let y = 122; y < H; y += 6) pt.box(146, y, 28, 0.5, mix(t.carpet, -0.25)); }
  else if (sp.style === "flat") { pt.box(141, 118, 38, 62, mix(t.carpet, 0.08), { line: false }); }
  // soft shadows where the furniture stands
  [[160, 118, 110], [61, 166, 96], [259, 166, 96], [236, 118, 34], [88, 118, 38]].forEach(([x, y, w]) => pt.ellipse(x, y + 0.5, w, 5, "#000000", sp.style === "ink" ? 0.06 : 0.22));
  g.generateTexture("room", W * P, H * P); g.destroy();
}

function furniture(scene: any, key: string, sp: { style: Style; p: number; pal: Pal }, w: number, h: number) {
  const g = scene.add.graphics(); const pt = new Painter(g, sp.style, sp.p, sp.pal); const t = sp.pal;
  pt.box(0, 3, w, h - 3, "wood", { r: sp.style === "flat" ? 1.5 : 0 });
  pt.box(-0.0, 0, w, 3.2, mix(t.wood, sp.style === "ink" ? 0 : 0.22), { r: sp.style === "flat" ? 1.2 : 0, bevel: true });
  pt.box(0, h - 2, w, 2, mix(t.wood, -0.35), { line: false });
  for (let x = 4; x < w - 4; x += 14) {
    if (sp.style === "pixel") {
      pt.box(x, 6, 10, h - 10, mix(t.wood, -0.3)); pt.box(x + 1, 7, 8, h - 12, "wood"); pt.box(x + 1, 7, 8, 0.5, mix(t.wood, 0.2));
      for (let gy = 10; gy < h - 6; gy += 5) pt.box(x + 2, gy, 5, 0.5, mix(t.wood, -0.12));    // grain
    } else pt.box(x + 0.5, 6.5, 9, h - 11, sp.style === "ink" ? "paper" : mix(t.wood, -0.12), { r: 1.2 });
  }
  g.generateTexture(key, w * sp.p, h * sp.p); g.destroy();
}

/* ------------------------------------------------------------------------------------------------ people */

/** Pixel person on a 32x44 grid (16x22 units at 2 art pixels per unit). */
function pixelPerson(pt: Painter, c: (typeof CAST)[string], frame: string) {
  const r = (x: number, y: number, w: number, h: number, k: string) => pt.px(x, y, w, h, k);
  const t = pt.t, suit = t[c.suit], hair = t[c.hair], skin = t.skin;
  const sk = mix(skin, -0.16), skl = mix(skin, 0.12), hl = mix(hair, 0.22), sl = mix(suit, 0.16), sd = mix(suit, -0.3);
  if (c.style === "long") { r(6, 4, 20, 22, hair); r(7, 25, 18, 2, mix(hair, -0.2)); }
  // head
  r(10, 4, 12, 1, skin); r(8, 5, 16, 14, skin); r(10, 19, 12, 1, skin); r(9, 6, 2, 10, skl); r(22, 6, 2, 12, sk); r(10, 18, 12, 1, sk);
  r(7, 10, 1, 4, skin); r(24, 10, 1, 4, sk);                                                     // ears
  // hair
  r(8, 2, 16, 4, hair); r(7, 4, 1, 7, hair); r(24, 4, 1, 7, hair); r(8, 6, 6, 2, hair); r(18, 6, 6, 1, hair); r(11, 3, 5, 1, hl);
  if (c.style === "judge") { r(6, 5, 2, 9, hair); r(24, 5, 2, 9, hair); r(8, 2, 16, 2, mix(hair, 0.12)); }
  // brows, eyes, nose, mouth
  r(11, 9, 3, 1, mix(t.hairDark, 0.1)); r(18, 9, 3, 1, mix(t.hairDark, 0.1));
  r(11, 11, 3, 2, t.eyeWhite); r(18, 11, 3, 2, t.eyeWhite); r(12, 11, 2, 2, t.eye); r(19, 11, 2, 2, t.eye);
  if (c.style === "glasses") { pt.g.lineStyle(1, hex(t.eye), 1); pt.g.strokeRect(10.5, 10.5, 5, 3); pt.g.strokeRect(17.5, 10.5, 5, 3); r(15, 11, 2, 1, t.eye); }
  r(15, 13, 2, 2, sk); r(16, 15, 1, 1, mix(skin, -0.28));
  if (frame === "talk") { r(14, 16, 4, 2, t.mouth); r(15, 17, 2, 1, mix(t.mouth, -0.4)); } else r(14, 17, 4, 1, t.mouth);
  r(11, 15, 2, 1, mix(skin, -0.05)); r(19, 15, 2, 1, mix(skin, -0.05));                          // cheeks
  // neck and body
  r(13, 20, 6, 2, sk);
  r(8, 22, 16, 1, suit); r(6, 23, 20, 1, suit); r(4, 24, 24, 20, suit);
  r(5, 24, 3, 20, sl); r(10, 28, 1, 16, sd); r(21, 28, 1, 16, sd); r(4, 43, 24, 1, sd);
  if (c.style === "judge") {
    r(11, 22, 10, 3, t.shirt); r(14, 25, 4, 4, t.shirt); r(15, 29, 2, 1, mix(t.shirt, -0.12));    // collar and jabot
    r(12, 30, 1, 14, sl); r(19, 30, 1, 14, sl);
  } else if (c.style === "casual") {
    r(13, 22, 6, 3, t.shirt); r(14, 25, 4, 1, mix(t.shirt, -0.1)); r(6, 33, 20, 1, sl);
  } else if (c.style === "glasses") {
    r(12, 22, 8, 8, t.shirt); r(15, 23, 2, 9, t.suitA); r(14, 23, 4, 2, t.suitA); r(11, 22, 1, 10, mix(suit, -0.18)); r(20, 22, 1, 10, mix(suit, -0.18));
  } else {
    r(12, 22, 8, 2, t.shirt); r(13, 24, 6, 3, t.shirt); r(14, 27, 4, 2, t.shirt);                 // V of the shirt
    r(15, 23, 2, 11, t.tie); r(14, 23, 4, 2, t.tie); r(16, 25, 1, 9, mix(t.tie, -0.25));         // tie
    r(11, 24, 1, 6, sd); r(12, 30, 1, 2, sd); r(20, 24, 1, 6, sd); r(19, 30, 1, 2, sd);            // lapels
    r(15, 36, 2, 1, sd); r(15, 40, 2, 1, sd);                                                      // buttons
  }
  if (frame === "raise") {
    r(26, 10, 6, 16, suit); r(26, 10, 2, 16, sl); r(26, 6, 6, 5, skin);
    if (c.style !== "judge") { r(24, 0, 8, 8, t.paper); r(25, 2, 6, 1, mix(t.paper, -0.3)); r(25, 4, 5, 1, mix(t.paper, -0.3)); }
  }
}

/** Smooth person (flat and ink) in units on a 16x22 box. */
function smoothPerson(pt: Painter, c: (typeof CAST)[string], frame: string) {
  const t = pt.t, ink = pt.style === "ink";
  if (c.style === "long") pt.box(3.1, 2.6, 9.8, 11.4, c.hair, { r: 4.5 });
  // body
  pt.box(2, 11.6, 12, 11, c.suit, { r: 4 });
  if (!ink) pt.box(2.4, 12.6, 2.4, 9.4, mix(t[c.suit], 0.14), { r: 1.2, line: false });
  if (c.style === "judge") { pt.poly([5.4, 11.4, 10.6, 11.4, 9.4, 15.6, 6.6, 15.6], "shirt", true); }
  else if (c.style === "casual") pt.poly([6.4, 11.4, 9.6, 11.4, 8, 13.6], "shirt", true);
  else if (c.style === "glasses") { pt.poly([5.6, 11.4, 10.4, 11.4, 8, 16.5], "shirt", true); pt.poly([7.4, 12, 8.6, 12, 8.4, 16.4, 7.6, 16.4], "suitA"); }
  else { pt.poly([5.8, 11.4, 10.2, 11.4, 8, 15.4], "shirt", true); pt.poly([7.4, 11.8, 8.6, 11.8, 8.9, 16.6, 8, 17.6, 7.1, 16.6], "tie"); }
  // neck, head, ears
  pt.box(6.8, 9.4, 2.4, 2.6, mix(t.skin, -0.12), { r: 0.8, line: false });
  pt.circle(3.9, 7, 0.9, "skin"); pt.circle(12.1, 7, 0.9, "skin");
  pt.circle(8, 6.6, 4.1, "skin");
  // hair cap with a fringe
  const hairK = c.hair;
  pt.g.fillStyle(pt.col(hairK), 1); pt.g.beginPath(); pt.g.arc(8 * pt.p, 6.4 * pt.p, 4.35 * pt.p, Math.PI * 1.02, Math.PI * 1.98, false); pt.g.closePath(); pt.g.fillPath();
  pt.box(4, 3.8, 3.6, 1.6, hairK, { r: 0.8, line: false }); pt.box(8.6, 3.6, 3.4, 1.3, hairK, { r: 0.6, line: false });
  if (c.style === "judge") { pt.box(3.4, 4.6, 1.2, 4.6, hairK, { r: 0.6, line: false }); pt.box(11.4, 4.6, 1.2, 4.6, hairK, { r: 0.6, line: false }); }
  if (ink) { pt.g.lineStyle(0.4 * pt.p, pt.col("ink"), 1); pt.g.beginPath(); pt.g.arc(8 * pt.p, 6.4 * pt.p, 4.35 * pt.p, Math.PI * 1.02, Math.PI * 1.98, false); pt.g.strokePath(); }
  // face
  pt.circle(6.5, 7.1, 0.5, "eye", { line: false }); pt.circle(9.5, 7.1, 0.5, "eye", { line: false });
  pt.line(5.7, 5.9, 7.2, 5.7, "eye", 0.3); pt.line(8.8, 5.7, 10.3, 5.9, "eye", 0.3);
  if (c.style === "glasses") { pt.g.lineStyle(0.3 * pt.p, pt.col("eye"), 1); pt.g.strokeCircle(6.5 * pt.p, 7.1 * pt.p, 1.25 * pt.p); pt.g.strokeCircle(9.5 * pt.p, 7.1 * pt.p, 1.25 * pt.p); pt.line(7.7, 7.1, 8.3, 7.1, "eye", 0.3); }
  if (!ink) { pt.circle(5.6, 8.6, 0.7, "#E58E7A", { alpha: 0.35, line: false }); pt.circle(10.4, 8.6, 0.7, "#E58E7A", { alpha: 0.35, line: false }); }
  if (frame === "talk") pt.ellipse(8, 9.2, 1.8, 1.2, "mouth"); else pt.line(7.2, 9.2, 8.8, 9.2, "mouth", 0.35);
  if (frame === "raise") {
    pt.box(12.6, 5.2, 2.8, 8, c.suit, { r: 1.2 }); pt.circle(14, 4.6, 1.3, "skin");
    if (c.style !== "judge") { pt.box(12.2, 0.2, 4.2, 4.4, "paper", { r: 0.4 }); pt.line(12.9, 1.6, 15.7, 1.6, mix(t.paper, -0.35), 0.25); pt.line(12.9, 2.8, 15.2, 2.8, mix(t.paper, -0.35), 0.25); }
  }
}

function bubble(scene: any, key: string, sp: { style: Style; p: number; pal: Pal }, symbol: string) {
  const g = scene.add.graphics(); const pt = new Painter(g, sp.style, sp.p, sp.pal);
  pt.box(0, 0, 9, 9, "bubble", { r: 2.4 }); pt.poly([2.6, 8.6, 5, 8.6, 3, 11], "bubble", true);
  const k = "bubbleInk";
  if (symbol === "!") { pt.box(4, 1.8, 1, 4, k, { line: false }); pt.box(4, 6.8, 1, 1, k, { line: false }); }
  else if (symbol === "?") { pt.box(3, 1.8, 3, 1, k, { line: false }); pt.box(6, 2.6, 1, 2, k, { line: false }); pt.box(4, 4.6, 2, 1, k, { line: false }); pt.box(4, 6.8, 1, 1, k, { line: false }); }
  else { [2, 4.5, 7].forEach((x) => pt.circle(x, 4.4, 0.6, k, { line: false })); }
  g.generateTexture(key, 9 * sp.p, 11 * sp.p); g.destroy();
}

/** Where each nametag sits (just under the visible part of the person, on the furniture in front). */
const TAG_Y: Record<string, number> = { judge: 80, plaintiff: 140, plaintiff_rep: 140, defendant_rep: 140, expert: 105, secretary: 106 };

export interface MountOptions {
  theme: CourtThemeId | "night";
  mode: "hero" | "play";
  onClick?: (id: string) => void;
  /** "reduced": no camera moves, shake or idle motion (user setting) */
  motion?: "full" | "reduced";
  /** CSS font stack for nametags (the user's UI font) */
  fontFamily?: string;
}

export type CourtHandle = CourtApi & { setNames(names: Record<string, string>): void; destroy(): void; snapshot(): Promise<string | null> };

/** Mounts the courtroom into `el`. Returns a CourtApi plus setNames(), snapshot() and destroy(). */
export function mountCourt(Phaser: any, el: HTMLElement, opts: MountOptions): CourtHandle {
  const themeId: CourtThemeId = ALIASES[opts.theme] ?? (opts.theme as CourtThemeId);
  const sp = SPECS[themeId] ?? SPECS.pixel;
  const t = sp.pal, P = sp.p;
  const reduce = opts.motion === "reduced";
  const font = opts.fontFamily || "system-ui, sans-serif";
  let scene: any = null;
  const queue: [string, unknown[]][] = [];

  class CourtScene extends Phaser.Scene {
    sprites: Record<string, any> = {};
    tags: Record<string, { box: any; text: any }> = {};
    names: Record<string, string> = {};
    speaker: string | null = null;
    speech: any; speechDots: any[] = [];
    gavelImg: any; bubbleImg: any;
    constructor() { super({ key: "court" }); }
    img(x: number, y: number, key: string) { return this.add.image(x, y, key).setScale(1 / P); }
    create() {
      drawRoom(this, sp);
      furniture(this, "bench", sp, 104, 46); furniture(this, "table", sp, 90, 32); furniture(this, "stand", sp, 30, 20); furniture(this, "desk", sp, 34, 18);
      ["!", "?", "…"].forEach((s, i) => bubble(this, "bubble" + i, sp, s));
      for (const [id, c] of Object.entries(CAST)) for (const fr of ["idle", "talk", "raise"]) {
        const g = this.add.graphics(); const pt = new Painter(g, sp.style, P, t);
        if (sp.style === "pixel") pixelPerson(pt, c, fr); else smoothPerson(pt, c, fr);
        g.generateTexture(`${id}_${fr}`, 16 * P, 22 * P); g.destroy();
      }
      { const g = this.add.graphics(); const pt = new Painter(g, sp.style, P, t); pt.box(0, 2, 7, 3, mix(t.wood, -0.35), { r: 1 }); pt.box(6, 3, 6, 1, mix(t.wood, 0.2), { r: 0.4 }); g.generateTexture("gavel", 12 * P, 6 * P); g.destroy(); }
      this.img(0, 0, "room").setOrigin(0);
      for (const [id, c] of Object.entries(CAST)) {
        const s = this.img(c.x, c.y, id + "_idle").setOrigin(0.5, 1).setDepth(2);
        s.baseY = c.y; this.sprites[id] = s;
        s.setInteractive({ useHandCursor: true }); s.on("pointerdown", () => opts.onClick?.(id));
      }
      this.img(160, 118, "bench").setOrigin(0.5, 1).setDepth(3);
      this.img(61, 166, "table").setOrigin(0.5, 1).setDepth(3);
      this.img(259, 166, "table").setOrigin(0.5, 1).setDepth(3);
      this.img(236, 118, "stand").setOrigin(0.5, 1).setDepth(3);
      this.img(88, 118, "desk").setOrigin(0.5, 1).setDepth(3);
      this.gavelImg = this.img(182, 73, "gavel").setOrigin(0.1, 0.5).setDepth(4);
      // evidence table with papers
      { const g = this.add.graphics().setDepth(3); const pt = new Painter(g, sp.style, 1, t);
        pt.box(142, 150, 36, 3, "wood", { r: 0.8 }); pt.box(142, 152.5, 36, 0.8, mix(t.wood, -0.35), { line: false });
        pt.box(145, 153, 2, 14, mix(t.wood, -0.3)); pt.box(173, 153, 2, 14, mix(t.wood, -0.3));
        pt.box(147, 144, 9, 7, "paper", { r: 0.4 }); pt.box(158, 145, 8, 6, "paper", { r: 0.4 }); pt.box(167, 143, 7, 8, "paper", { r: 0.4 });
        pt.box(148, 146, 6, 0.6, "bubbleInk", { line: false, alpha: 0.6 }); pt.box(159, 147, 5, 0.6, "bubbleInk", { line: false, alpha: 0.6 }); pt.box(168, 145, 5, 0.6, "bubbleInk", { line: false, alpha: 0.6 }); }
      const zone = this.add.zone(160, 156, 44, 28).setInteractive({ useHandCursor: true }).setDepth(5);
      zone.on("pointerdown", () => opts.onClick?.("evidence_table"));
      const marker = this.add.triangle(160, 136, 0, 0, 8, 0, 4, 5, hex(t.highlight)).setDepth(5).setAlpha(0);
      zone.on("pointerover", () => marker.setAlpha(1)); zone.on("pointerout", () => marker.setAlpha(0));
      this.bubbleImg = this.img(0, 0, "bubble0").setOrigin(0.5, 1).setDepth(8).setVisible(false);
      this.cameras.main.setZoom(ZOOM).centerOn(W / 2, H / 2);
      this.buildSpeech();
      if (!reduce) Object.values(this.sprites).forEach((s: any, i) => this.tweens.add({ targets: s, y: s.baseY - 1, duration: 1400 + i * 170, yoyo: true, repeat: -1, ease: "Sine.easeInOut", delay: i * 230 }));
      if (opts.mode === "hero" && !reduce) this.ambient();
      // eslint-disable-next-line @typescript-eslint/no-this-alias -- the outer API forwards calls to the live scene
      scene = this; queue.splice(0).forEach(([fn, a]) => (this as any)[fn](...a));
    }
    /** Rounded speech bubble with a tail and three "typing" dots (no text: the line is shown in the DOM dialogue). */
    buildSpeech() {
      const g = this.add.graphics();
      const w = 17, h = 9, r = 3.2;
      g.fillStyle(hex(t.bubble), 1); g.lineStyle(0.6, hex(t.bubbleInk), 0.9);
      g.fillRoundedRect(-w / 2, -h, w, h, r); g.strokeRoundedRect(-w / 2, -h, w, h, r);
      g.fillTriangle(-5.5, -0.6, -1.8, -0.6, -7.5, 3.6);
      g.lineBetween(-5.5, -0.3, -7.5, 3.6); g.lineBetween(-7.5, 3.6, -1.8, -0.3);
      const dots = [-4, 0, 4].map((x) => this.add.circle(x, -h / 2, 1.05, hex(t.bubbleInk)));
      this.speechDots = dots;
      this.speech = this.add.container(0, 0, [g, ...dots]).setDepth(7).setVisible(false);
      dots.forEach((d, i) => this.tweens.add({ targets: d, alpha: { from: 0.25, to: 1 }, y: { from: -h / 2, to: -h / 2 - 1 },
        duration: 360, yoyo: true, repeat: -1, delay: i * 140, ease: "Sine.easeInOut" }));
    }
    showSpeech(id: string | null) {
      const s = id && this.sprites[id];
      if (!s) { this.speech.setVisible(false); return; }
      this.speech.setPosition(s.x + 12, s.baseY - 22).setVisible(true);
      if (!reduce) this.tweens.add({ targets: this.speech, scale: { from: 0.55, to: 1 }, duration: 180, ease: "Back.easeOut" });
    }
    setNames(names: Record<string, string>) {
      this.names = names;
      for (const [id, tag] of Object.entries(this.tags)) { tag.box.destroy(); tag.text.destroy(); delete this.tags[id]; }
      for (const [id, name] of Object.entries(names)) {
        const s = this.sprites[id]; if (!s || !name || TAG_Y[id] === undefined) continue;
        const text = this.add.text(s.x, TAG_Y[id], name, { fontFamily: font, fontSize: "4.2px", fontStyle: "600", color: t.paper, resolution: 8 })
          .setOrigin(0.5, 0.5).setDepth(6);
        const box = this.add.graphics().setDepth(5);
        this.tags[id] = { box, text };
      }
      this.paintTags();
    }
    paintTags() {
      for (const [id, { box, text }] of Object.entries(this.tags)) {
        const active = id === this.speaker;
        const w = text.width + 4, h = 6.2;
        box.clear();
        box.fillStyle(hex(active ? t.highlight : t.bubbleInk), active ? 1 : 0.82);
        box.fillRoundedRect(text.x - w / 2, text.y - h / 2, w, h, 1.8);
        text.setColor(active ? t.bubbleInk : t.bubble);
      }
    }
    talk(id: string, on: boolean) {
      const s = this.sprites[id]; if (!s) return;
      if (s.talkTimer) { s.talkTimer.remove(); s.talkTimer = null; }
      if (!on) { s.setTexture(id + "_idle"); return; }
      let open = false;
      s.talkTimer = this.time.addEvent({ delay: 120, loop: true, callback: () => { open = !open; s.setTexture(id + (open ? "_talk" : "_idle")); } });
    }
    /** Current speaker: highlight the nametag, show the speech bubble, ease the camera onto them (null = wide shot). */
    focus(id: string | null) {
      const s = id ? this.sprites[id] : null;
      const next = s ? id : null;
      if (next === this.speaker) return;
      this.speaker = next;
      this.paintTags();
      this.showSpeech(next);
      if (reduce) return;
      const cam = this.cameras.main;
      if (!s) { cam.pan(W / 2, H / 2, 650, "Sine.easeInOut", true); cam.zoomTo(ZOOM, 650, "Sine.easeInOut", true); return; }
      const halfW = (W * ZOOM) / FOCUS_ZOOM / 2, halfH = (H * ZOOM) / FOCUS_ZOOM / 2;
      const x = Phaser.Math.Clamp(s.x, halfW, W - halfW), y = Phaser.Math.Clamp(s.baseY - 12, halfH, H - halfH);
      cam.pan(x, y, 650, "Sine.easeInOut", true);
      cam.zoomTo(FOCUS_ZOOM, 650, "Sine.easeInOut", true);
    }
    react(id: string, kind: string) {
      const s = this.sprites[id]; if (!s) return;
      if (kind === "nod") { this.tweens.add({ targets: s, y: s.baseY + 2, duration: 120, yoyo: true, repeat: 1 }); return; }
      if (kind === "object") { s.setTexture(id + "_raise"); this.time.delayedCall(900, () => s.setTexture(id + "_idle")); }
      const sym = kind === "think" ? 2 : kind === "surprised" ? 1 : 0;
      this.bubbleImg.setTexture("bubble" + sym).setPosition(s.x + 9, s.baseY - 22).setVisible(true);
      this.time.delayedCall(1100, () => this.bubbleImg.setVisible(false));
    }
    gavel() {
      this.tweens.add({ targets: this.gavelImg, angle: { from: -55, to: 0 }, duration: 160, ease: "Quad.easeIn",
        onComplete: () => { if (!reduce) this.cameras.main.shake(140, 0.006); } });
    }
    ambient() {
      const ids = ["judge", "plaintiff_rep", "defendant_rep", "plaintiff", "expert"]; let i = 0;
      this.time.addEvent({ delay: 2600, loop: true, callback: () => {
        const id = ids[i++ % ids.length]; this.talk(id, true); this.showSpeech(id);
        this.time.delayedCall(1300, () => { this.talk(id, false); this.showSpeech(null); });
        if (i % 5 === 0) this.time.delayedCall(1500, () => this.gavel());
        if (i % 4 === 2) this.react("defendant_rep", "object");
      } });
    }
  }

  const game = new Phaser.Game({
    // pixel themes: blocky art pixels with smooth edges (no shimmer on camera moves); vector themes: antialiased
    type: Phaser.AUTO, parent: el, width: W * ZOOM, height: H * ZOOM, smoothPixelArt: sp.style === "pixel", antialias: true,
    backgroundColor: t.bg, banner: false, preserveDrawingBuffer: true,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH }, scene: CourtScene,
  });
  const call = (fn: string, ...a: unknown[]) => (scene ? scene[fn](...a) : queue.push([fn, a]));
  return {
    setNames: (names) => call("setNames", names),
    talk: (id, on) => call("talk", id, on),
    focus: (id) => call("focus", id),
    react: (id, k) => call("react", id, k),
    gavel: () => call("gavel"),
    /** a still image of the current frame (used for the theme gallery on the home page) */
    snapshot: () => new Promise((resolve) => {
      const take = () => { try { game.renderer.snapshot((img: HTMLImageElement) => resolve(img?.src ?? null)); } catch { resolve(null); } };
      const wait = (n: number) => (scene || n <= 0 ? setTimeout(take, 120) : setTimeout(() => wait(n - 1), 100));
      wait(40);
    }),
    destroy: () => game.destroy(true),
  };
}
