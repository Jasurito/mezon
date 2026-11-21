/**
 * Character speech: plays the pre-generated MP3 of a line (backend docs/TTS.md). One line at a time: a new line
 * stops the previous one. Lines about to be spoken are preloaded, so playback starts at once.
 * A blocked autoplay or a broken file never stops the game: onEnd fires and the line stays text only.
 */
let current: HTMLAudioElement | null = null;
let queue: string[] = [];
const preloaded = new Map<string, HTMLAudioElement>();
const PRELOAD_MAX = 8;

const canPlay = () => typeof window !== "undefined" && typeof Audio !== "undefined";

export function preloadVoice(url: string | null | undefined) {
  if (!url || !canPlay() || preloaded.has(url)) return;
  const a = new Audio();
  a.preload = "auto";
  a.src = url;
  preloaded.set(url, a);
  if (preloaded.size > PRELOAD_MAX) preloaded.delete(preloaded.keys().next().value!);
}

/** Play one line; onEnd runs when it finishes, fails or is replaced by another line (not when stopped). */
export function playVoice(url: string, onEnd?: () => void) {
  stopVoice();
  if (!canPlay()) { onEnd?.(); return; }
  const a = preloaded.get(url) ?? new Audio(url);
  preloaded.delete(url);
  current = a;
  const done = () => {
    if (current !== a) return;
    current = null;
    onEnd?.();
  };
  a.onended = done;
  a.onerror = done;
  a.currentTime = 0;
  a.play().catch(done);
}

/** Play several lines one after another (the life-situation story). */
export function playVoices(urls: string[]) {
  queue = urls.slice(1);
  urls.slice(1, 3).forEach(preloadVoice);
  if (urls[0]) playVoice(urls[0], () => { if (queue.length) playVoices(queue); });
}

export function stopVoice() {
  queue = [];
  const a = current;
  current = null;
  if (a) { a.onended = null; a.onerror = null; a.pause(); }
}

export const isSpeaking = () => current !== null;
