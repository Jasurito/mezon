/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Procedural pixel-art courtroom (Phaser 4). No external art: everything is drawn in code.
 * Text never lives in the canvas (spec: DOM overlay keeps i18n, wrapping and a11y simple).
 */
import type { CourtApi } from "@/store/game";

const W = 320, H = 180;
const hex = (s: string) => parseInt(s.slice(1), 16);

type Theme = Record<string, string>;
export const THEMES: Record<"night" | "ink", Theme> = {
  night: { bg: "#0F1B2D", wallA: "#1B2A41", wallB: "#182539", trim: "#2C4062", panel: "#4A321D", panelLight: "#6B4A2B",
    floorA: "#22324A", floorB: "#1C2A3F", wood: "#6B4A2B", woodDark: "#3F2A17", woodLight: "#8C653D",
    window: "#0A1424", windowGlow: "#21365A", star: "#C9A227", lamp: "#C9A227", emblem: "#C9A227", emblemDark: "#8A6E14",
    skin: "#D9A47A", skinShade: "#B9805A", hairDark: "#1E1A1A", hairBrown: "#5A3A22", hairGrey: "#9AA3AE",
    robe: "#121826", suitA: "#24406B", suitB: "#4B5563", casual: "#2F6D5F", coat: "#E6E2D8", shirt: "#F5F1E8",
    tie: "#C9A227", eye: "#141414", mouth: "#7A3B2E", paper: "#F5F1E8", bubble: "#F5F1E8", bubbleInk: "#0F1B2D", highlight: "#C9A227" },
  ink: { bg: "#E4E7DE", wallA: "#E4E7DE", wallB: "#D6DBE6", trim: "#B8C0D9", panel: "#6F7DB8", panelLight: "#9AA5CF",
    floorA: "#C9CFE0", floorB: "#B8C0D9", wood: "#6F7DB8", woodDark: "#2B3990", woodLight: "#9AA5CF",
    window: "#F1F3EE", windowGlow: "#D6DBE6", star: "#6F7DB8", lamp: "#6F7DB8", emblem: "#2B3990", emblemDark: "#141A2E",
    skin: "#E4E7DE", skinShade: "#B8C0D9", hairDark: "#141A2E", hairBrown: "#2B3990", hairGrey: "#9AA5CF",
    robe: "#141A2E", suitA: "#2B3990", suitB: "#6F7DB8", casual: "#9AA5CF", coat: "#F1F3EE", shirt: "#F1F3EE",
    tie: "#141A2E", eye: "#141A2E", mouth: "#2B3990", paper: "#F1F3EE", bubble: "#F1F3EE", bubbleInk: "#2B3990", highlight: "#B3261E" },
};

const CAST: Record<string, { x: number; y: number; suit: string; hair: string; style: string }> = {
  judge: { x: 160, y: 76, suit: "robe", hair: "hairGrey", style: "judge" },
  plaintiff: { x: 40, y: 136, suit: "casual", hair: "hairBrown", style: "casual" },
  plaintiff_rep: { x: 78, y: 136, suit: "suitA", hair: "hairDark", style: "suit" },
  defendant_rep: { x: 262, y: 136, suit: "suitB", hair: "hairDark", style: "long" },
  expert: { x: 236, y: 102, suit: "coat", hair: "hairBrown", style: "glasses" },
  secretary: { x: 88, y: 104, suit: "suitB", hair: "hairBrown", style: "long" },
};

function drawPerson(g: any, t: Theme, c: (typeof CAST)[string], frame: string) {
  const r = (k: string, x: number, y: number, w: number, h: number) => { g.fillStyle(hex(t[k]), 1); g.fillRect(x, y, w, h); };
  if (c.style === "long") r(c.hair, 3, 2, 10, 11);
  r("skin", 4, 2, 8, 8); r("skinShade", 4, 9, 8, 1);
  r(c.hair, 4, 1, 8, 2); r(c.hair, 3, 2, 1, 4); r(c.hair, 12, 2, 1, 4);
  if (c.style === "judge") { r(c.hair, 3, 2, 1, 6); r(c.hair, 12, 2, 1, 6); }
  r("eye", 6, 5, 1, 1); r("eye", 9, 5, 1, 1);
  if (c.style === "glasses") { r("eye", 5, 4, 3, 1); r("eye", 8, 4, 3, 1); }
  if (frame === "talk") r("mouth", 7, 7, 2, 2); else r("mouth", 7, 8, 2, 1);
  r("skin", 7, 10, 2, 1);
  r(c.suit, 3, 11, 10, 1); r(c.suit, 2, 12, 12, 10);
  if (c.style === "judge") { r("shirt", 6, 11, 4, 3); r("shirt", 7, 14, 2, 1); }
  else if (c.style === "casual") r("shirt", 7, 11, 2, 2);
  else if (c.style === "glasses") { r("shirt", 6, 11, 4, 4); r("suitA", 7, 12, 2, 4); }
  else { r("shirt", 6, 11, 4, 2); r("tie", 7, 12, 2, 6); }
  if (frame === "raise") { r(c.suit, 13, 5, 3, 8); r("skin", 13, 3, 3, 2); if (c.style !== "judge") { r("paper", 12, 0, 4, 4); r("trim", 13, 1, 2, 1); } }
}

function drawRoom(scene: any, t: Theme) {
  const g = scene.add.graphics();
  const f = (k: string, x: number, y: number, w: number, h: number) => { g.fillStyle(hex(t[k]), 1); g.fillRect(x, y, w, h); };
  f("wallA", 0, 0, W, 118);
  for (let x = 0; x < W; x += 16) f("wallB", x, 0, 8, 84);
  f("trim", 0, 84, W, 2); f("panel", 0, 86, W, 32);
  for (let x = 4; x < W; x += 20) f("panelLight", x, 90, 14, 24);
  [[34, 18], [262, 18]].forEach(([x, y]) => {
    f("trim", x - 2, y - 2, 28, 58); f("window", x, y, 24, 54); f("windowGlow", x, y + 30, 24, 24);
    f("trim", x + 11, y, 2, 54); f("trim", x, y + 26, 24, 2);
    f("star", x + 5, y + 6, 1, 1); f("star", x + 17, y + 12, 1, 1); f("star", x + 7, y + 19, 1, 1);
  });
  g.fillStyle(hex(t.emblemDark), 1); g.fillCircle(160, 26, 15);
  g.fillStyle(hex(t.emblem), 1); g.fillCircle(160, 26, 13);
  g.fillStyle(hex(t.wallA), 1); g.fillCircle(160, 26, 10);
  f("emblem", 159, 18, 2, 15); f("emblem", 151, 21, 18, 2); f("emblem", 156, 33, 8, 2);
  f("emblem", 150, 23, 1, 4); f("emblem", 169, 23, 1, 4); f("emblem", 147, 27, 7, 2); f("emblem", 166, 27, 7, 2);
  [[120, 44], [200, 44]].forEach(([x, y]) => { f("lamp", x - 2, y, 4, 6); f("emblemDark", x - 1, y + 6, 2, 1); });
  f("floorA", 0, 118, W, 62);
  for (let y = 118; y < H; y += 8) for (let x = ((y - 118) / 8) % 2 ? 8 : 0; x < W; x += 16) f("floorB", x, y, 8, 8);
  g.generateTexture("room", W, H); g.destroy();
}

function furniture(scene: any, key: string, t: Theme, w: number, h: number) {
  const g = scene.add.graphics();
  const f = (k: string, x: number, y: number, ww: number, hh: number) => { g.fillStyle(hex(t[k]), 1); g.fillRect(x, y, ww, hh); };
  f("woodLight", 0, 0, w, 3); f("wood", 0, 3, w, h - 3); f("woodDark", 0, h - 2, w, 2);
  for (let x = 4; x < w - 4; x += 14) { f("woodDark", x, 6, 10, h - 10); f("wood", x + 1, 7, 8, h - 12); }
  g.generateTexture(key, w, h); g.destroy();
}

function bubble(scene: any, key: string, t: Theme, symbol: string) {
  const g = scene.add.graphics();
  g.fillStyle(hex(t.bubble), 1); g.fillRect(1, 0, 7, 9); g.fillRect(0, 1, 9, 7); g.fillRect(3, 9, 2, 2);
  g.fillStyle(hex(t.bubbleInk), 1);
  if (symbol === "!") { g.fillRect(4, 2, 1, 4); g.fillRect(4, 7, 1, 1); }
  else if (symbol === "?") { g.fillRect(3, 2, 3, 1); g.fillRect(6, 3, 1, 2); g.fillRect(4, 5, 2, 1); g.fillRect(4, 7, 1, 1); }
  else { g.fillRect(2, 4, 1, 1); g.fillRect(4, 4, 1, 1); g.fillRect(6, 4, 1, 1); }
  g.generateTexture(key, 9, 11); g.destroy();
}

export interface MountOptions { theme: keyof typeof THEMES; mode: "hero" | "play"; onClick?: (id: string) => void }

/** Mounts the courtroom into `el`. Returns a CourtApi plus destroy(). */
export function mountCourt(Phaser: any, el: HTMLElement, opts: MountOptions): CourtApi & { destroy(): void } {
  const t = THEMES[opts.theme];
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let scene: any = null;
  const queue: [string, unknown[]][] = [];

  class CourtScene extends Phaser.Scene {
    sprites: Record<string, any> = {};
    gavelImg: any; bubbleImg: any;
    constructor() { super({ key: "court" }); }
    create() {
      drawRoom(this, t);
      furniture(this, "bench", t, 104, 46); furniture(this, "table", t, 90, 32); furniture(this, "stand", t, 30, 20); furniture(this, "desk", t, 34, 18);
      ["!", "?", "…"].forEach((s, i) => bubble(this, "bubble" + i, t, s));
      for (const [id, c] of Object.entries(CAST)) for (const fr of ["idle", "talk", "raise"]) {
        const g = this.add.graphics(); drawPerson(g, t, c, fr); g.generateTexture(`${id}_${fr}`, 16, 22); g.destroy();
      }
      { const g = this.add.graphics(); g.fillStyle(hex(t.woodDark), 1); g.fillRect(0, 2, 7, 3); g.fillStyle(hex(t.woodLight), 1); g.fillRect(6, 3, 6, 1); g.generateTexture("gavel", 12, 6); g.destroy(); }
      this.add.image(0, 0, "room").setOrigin(0);
      for (const [id, c] of Object.entries(CAST)) {
        const s = this.add.image(c.x, c.y, id + "_idle").setOrigin(0.5, 1).setDepth(2);
        s.baseY = c.y; this.sprites[id] = s;
        s.setInteractive({ useHandCursor: true }); s.on("pointerdown", () => opts.onClick?.(id));
      }
      this.add.image(160, 118, "bench").setOrigin(0.5, 1).setDepth(3);
      this.add.image(61, 166, "table").setOrigin(0.5, 1).setDepth(3);
      this.add.image(259, 166, "table").setOrigin(0.5, 1).setDepth(3);
      this.add.image(236, 118, "stand").setOrigin(0.5, 1).setDepth(3);
      this.add.image(88, 118, "desk").setOrigin(0.5, 1).setDepth(3);
      this.gavelImg = this.add.image(182, 73, "gavel").setOrigin(0.1, 0.5).setDepth(4);
      const ev = this.add.graphics().setDepth(3);
      ev.fillStyle(hex(t.woodDark), 1); ev.fillRect(142, 152, 36, 3); ev.fillRect(145, 155, 2, 12); ev.fillRect(173, 155, 2, 12);
      ev.fillStyle(hex(t.wood), 1); ev.fillRect(142, 150, 36, 3);
      ev.fillStyle(hex(t.paper), 1); ev.fillRect(147, 144, 9, 7); ev.fillRect(158, 145, 8, 6); ev.fillRect(167, 143, 7, 8);
      ev.fillStyle(hex(t.trim), 1); ev.fillRect(148, 146, 6, 1); ev.fillRect(159, 147, 5, 1); ev.fillRect(168, 145, 5, 1);
      const zone = this.add.zone(160, 156, 44, 28).setInteractive({ useHandCursor: true }).setDepth(5);
      zone.on("pointerdown", () => opts.onClick?.("evidence_table"));
      const marker = this.add.triangle(160, 136, 0, 0, 8, 0, 4, 5, hex(t.highlight)).setDepth(5).setAlpha(0);
      zone.on("pointerover", () => marker.setAlpha(1)); zone.on("pointerout", () => marker.setAlpha(0));
      this.bubbleImg = this.add.image(0, 0, "bubble0").setOrigin(0.5, 1).setDepth(6).setVisible(false);
      if (!reduce) Object.values(this.sprites).forEach((s: any, i) => this.tweens.add({ targets: s, y: s.baseY - 1, duration: 1400 + i * 170, yoyo: true, repeat: -1, ease: "Sine.easeInOut", delay: i * 230 }));
      if (opts.mode === "hero" && !reduce) this.ambient();
      // eslint-disable-next-line @typescript-eslint/no-this-alias -- the outer API forwards calls to the live scene
      scene = this; queue.splice(0).forEach(([fn, a]) => (this as any)[fn](...a));
    }
    talk(id: string, on: boolean) {
      const s = this.sprites[id]; if (!s) return;
      if (s.talkTimer) { s.talkTimer.remove(); s.talkTimer = null; }
      if (!on) { s.setTexture(id + "_idle"); return; }
      let open = false;
      s.talkTimer = this.time.addEvent({ delay: 120, loop: true, callback: () => { open = !open; s.setTexture(id + (open ? "_talk" : "_idle")); } });
    }
    focus(id: string | null) {
      if (reduce) return;
      const cam = this.cameras.main; const s = id && this.sprites[id];
      if (!s) { cam.pan(W / 2, H / 2, 300, "Sine.easeInOut"); cam.zoomTo(1, 300); return; }
      cam.pan(Phaser.Math.Clamp(s.x, 130, 190), Phaser.Math.Clamp(s.baseY - 20, 70, 110), 300, "Sine.easeInOut");
      cam.zoomTo(1.18, 300);
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
        const id = ids[i++ % ids.length]; this.talk(id, true);
        this.time.delayedCall(1300, () => this.talk(id, false));
        if (i % 5 === 0) this.time.delayedCall(1500, () => this.gavel());
        if (i % 4 === 2) this.react("defendant_rep", "object");
      } });
    }
  }

  const game = new Phaser.Game({
    type: Phaser.AUTO, parent: el, width: W, height: H, pixelArt: true, backgroundColor: t.bg, banner: false,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH }, scene: CourtScene,
  });
  const call = (fn: string, ...a: unknown[]) => (scene ? scene[fn](...a) : queue.push([fn, a]));
  return {
    talk: (id, on) => call("talk", id, on),
    focus: (id) => call("focus", id),
    react: (id, k) => call("react", id, k),
    gavel: () => call("gavel"),
    destroy: () => game.destroy(true),
  };
}
