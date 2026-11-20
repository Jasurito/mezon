/**
 * Uzbek Latin -> Uzbek Cyrillic transliteration (deterministic).
 * Used for UI strings (scripts/gen-uz-cyrl.mts) and mock scenario texts.
 * Law text is never transliterated: it always comes verbatim from the corpus.
 * Output must be spot-checked by the legal/content member (spec, ARCHITECTURE §9).
 */

const LETTERS: Record<string, string> = {
  a: "а", b: "б", c: "с", d: "д", f: "ф", g: "г", h: "ҳ", i: "и", j: "ж", k: "к", l: "л", m: "м",
  n: "н", o: "о", p: "п", q: "қ", r: "р", s: "с", t: "т", u: "у", v: "в", w: "в", x: "х", y: "й", z: "з",
};
const IOTATED: Record<string, string> = { a: "я", o: "ё", u: "ю", e: "е" };
const VOWELS = "aeiouAEIOU";
const OKINA = /[ʻ‘'`]/; // oʻ / gʻ marker (U+02BB and look-alikes)

/** Russian loanwords whose Cyrillic spelling cannot be derived letter by letter. */
const WORDS: Record<string, string> = {
  sudya: "судья", sudyaning: "судьянинг", sudyaga: "судьяга",
  yanvar: "январь", fevral: "февраль", aprel: "апрель", iyun: "июнь", iyul: "июль",
  sentabr: "сентябрь", oktabr: "октябрь", noyabr: "ноябрь", dekabr: "декабрь",
};

/** Tokens left untouched (brands, domains, ICU placeholders). */
const KEEP = /(\{[^}]*\}|https?:\/\/\S+|[a-z0-9-]+\.(?:uz|cc|com)\b|Google|SSO|PDF|Mezon|Commissioner|Onest|IBM Plex Sans|Source Serif|Nunito|LexHackathon)/g;

const isUpper = (ch: string) => ch !== ch.toLowerCase();
const fit = (cyr: string, src: string, nextUpper: boolean) =>
  isUpper(src) ? (nextUpper || cyr.length === 1 ? cyr.toUpperCase() : cyr[0].toUpperCase() + cyr.slice(1)) : cyr;

function convertWord(w: string): string {
  const dict = WORDS[w.toLowerCase()];
  if (dict) return isUpper(w[0]) ? dict[0].toUpperCase() + dict.slice(1) : dict;
  let out = "";
  for (let i = 0; i < w.length; i++) {
    const c = w[i], n = w[i + 1] ?? "", lc = c.toLowerCase(), ln = n.toLowerCase(), prev = w[i - 1] ?? "";
    const nextUpper = n !== "" && isUpper(n);
    if ((lc === "o" || lc === "g") && OKINA.test(n)) { out += fit(lc === "o" ? "ў" : "ғ", c, true); i++; continue; }
    if (lc === "s" && ln === "h") { out += fit("ш", c, nextUpper); i++; continue; }
    if (lc === "c" && ln === "h") { out += fit("ч", c, nextUpper); i++; continue; }
    if (lc === "y" && IOTATED[ln] && !(ln === "o" && OKINA.test(w[i + 2] ?? ""))) { out += fit(IOTATED[ln], c, nextUpper); i++; continue; }
    if (lc === "t" && ln === "s" && VOWELS.includes(prev) && VOWELS.includes(w[i + 2] ?? "")) { out += fit("ц", c, nextUpper); i++; continue; }
    if (lc === "e") { const start = i === 0 || VOWELS.includes(prev) || prev === "ʼ"; out += fit(start ? "э" : "е", c, nextUpper); continue; }
    if (c === "ʼ") { out += "ъ"; continue; }
    if (LETTERS[lc]) { out += fit(LETTERS[lc], c, nextUpper); continue; }
    out += c;
  }
  return out;
}

function convertPlain(text: string): string {
  return text.replace(/[A-Za-zʻʼ‘'`]+/g, (w) => convertWord(w));
}

export function latnToCyrl(text: string): string {
  return text.split(KEEP).map((chunk, i) => (i % 2 ? chunk : convertPlain(chunk))).join("");
}

/** Recursively transliterate every string in a JSON-like object. */
export function transliterateDeep<T>(value: T): T {
  if (typeof value === "string") return latnToCyrl(value) as T;
  if (Array.isArray(value)) return value.map(transliterateDeep) as T;
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, transliterateDeep(v)])) as T;
  }
  return value;
}
