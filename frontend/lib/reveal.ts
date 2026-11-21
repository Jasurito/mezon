/**
 * After an answer, new content (dialogue, the next choices, the next question) can land below the fold.
 * reveal() scrolls the page down just enough to show `bottom` in full, but never so far that the top of `top`
 * (the first new line) leaves the screen, and never up: if the user has scrolled past, nothing moves.
 */
export function reveal(top: Element | null | undefined, bottom: Element | null | undefined, pad = 16) {
  if (!bottom || typeof window === "undefined") return;
  const vh = window.innerHeight;
  const b = bottom.getBoundingClientRect();
  if (b.bottom <= vh - pad || b.bottom <= 0) return;   // already visible, or above the screen (user scrolled on)
  let delta = b.bottom - (vh - pad);
  if (top) delta = Math.min(delta, top.getBoundingClientRect().top - pad);
  if (delta < 2) return;
  const reduced = document.documentElement.dataset.motion === "reduced" || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  window.scrollBy({ top: delta, behavior: reduced ? "auto" : "smooth" });
}
