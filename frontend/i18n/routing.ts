import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["uz-Latn", "uz-Cyrl", "ru"],
  defaultLocale: "uz-Latn",
  // short, readable URL prefixes; the locale codes stay BCP 47 (backend contract)
  localePrefix: { mode: "always", prefixes: { "uz-Latn": "/uz", "uz-Cyrl": "/uz-cyrl", ru: "/ru" } },
});

export type Locale = (typeof routing.locales)[number];
