/** "ст. 13" / "13-modda" / "13-модда": short article label in the interface language. */
export function articleLabel(n: string | number, locale: string, long = false): string {
  if (locale === "ru") return long ? `Статья ${n}` : `ст. ${n}`;
  return locale === "uz-Cyrl" ? `${n}-модда` : `${n}-modda`;
}
