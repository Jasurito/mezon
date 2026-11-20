import { Commissioner, IBM_Plex_Mono, IBM_Plex_Sans, Nunito, Onest, Oswald, Source_Serif_4, Tiny5 } from "next/font/google";

// Every family below was checked for Uzbek glyphs: ʻ ʼ ў қ ғ ҳ (Manrope and Pixelify Sans fail, do not use).
// next/font needs literal options in every call (no shared variables).
export const commissioner = Commissioner({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], variable: "--font-commissioner", display: "swap" });
export const tiny5 = Tiny5({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], weight: "400", variable: "--font-tiny5", display: "swap" });
export const plexMono = IBM_Plex_Mono({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], weight: ["400", "500", "700"], variable: "--font-plexmono", display: "swap" });
export const oswald = Oswald({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], weight: ["500", "700"], variable: "--font-oswald", display: "swap" });
// optional reading fonts (settings); not preloaded, downloaded only when selected
export const onest = Onest({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], variable: "--font-onest", display: "swap", preload: false });
export const plexSans = IBM_Plex_Sans({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], weight: ["400", "500", "600", "700"], variable: "--font-plex", display: "swap", preload: false });
export const serif = Source_Serif_4({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], variable: "--font-serif", display: "swap", preload: false });
export const nunito = Nunito({ subsets: ["latin", "latin-ext", "cyrillic", "cyrillic-ext"], variable: "--font-nunito", display: "swap", preload: false });

export const fontVariables = [commissioner, tiny5, plexMono, oswald, onest, plexSans, serif, nunito].map((f) => f.variable).join(" ");
