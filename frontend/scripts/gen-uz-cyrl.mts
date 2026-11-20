/**
 * Generates locales/uz-Cyrl.json from locales/uz-Latn.json (deterministic transliteration)
 * and checks that every locale has exactly the same keys.
 * Run: pnpm i18n   (Node >= 23 runs .ts directly). Spot-check the output before release.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { transliterateDeep } from "../lib/translit.ts";

const dir = new URL("../locales/", import.meta.url);
const read = (name: string) => JSON.parse(readFileSync(new URL(name, dir), "utf8"));
const latn = read("uz-Latn.json");
writeFileSync(new URL("uz-Cyrl.json", dir), JSON.stringify(transliterateDeep(latn), null, 2) + "\n");

const keys = (o: Record<string, unknown>, p = ""): string[] =>
  Object.entries(o).flatMap(([k, v]) => (v && typeof v === "object" ? keys(v as Record<string, unknown>, p + k + ".") : [p + k]));
const base = new Set(keys(latn));
let failed = false;
for (const name of ["ru.json", "uz-Cyrl.json"]) {
  const other = new Set(keys(read(name)));
  const missing = [...base].filter((k) => !other.has(k));
  const extra = [...other].filter((k) => !base.has(k));
  if (missing.length || extra.length) { failed = true; console.error(name, { missing, extra }); }
}
if (failed) process.exit(1);
console.log(`uz-Cyrl.json generated, ${base.size} keys in sync`);
