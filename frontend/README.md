# Mezon frontend

Next.js 16 (App Router), TypeScript, Tailwind 4, shadcn/ui (Radix), Phaser 4 (courtroom only), Zustand and next-intl.
Live at https://mezon.modeus.cc. The reference sketches are at https://1.modeus.cc (play screen) and https://2.modeus.cc (landing).

## Run

```bash
pnpm install
pnpm dev            # http://localhost:3000 -> /uz
pnpm build && PORT=3000 pnpm start
pnpm typecheck && pnpm lint
pnpm i18n           # regenerate locales/uz-Cyrl.json from uz-Latn.json and check that the keys match
docker compose up -d --build frontend   # from the repo root
```

| Env (build time) | Default | Meaning |
|---|---|---|
| `NEXT_PUBLIC_API_MODE` | `mock` | `mock` runs a demo backend in the browser (localStorage). `live` calls FastAPI under `/api` on the same origin |
| `NEXT_PUBLIC_SHOW_SKETCHES` | `true` | Shows the "Eskizlar 1 2" pill linking to the reference sketches |

## Structure

```
app/[locale]/page.tsx             landing (case-file style, sketch 2)
app/[locale]/(app)/…              cases, case intro, pre/post tests, results, mentor, dashboard, settings, auth
app/[locale]/(game)/play/[id]     court simulator (night style, sketch 1)
game/                             Phaser 4 courtroom, drawn in code; Court.tsx mounts it client-only
store/                            game (event queue), user (guest id + account), settings (fonts), ui (legal panel)
lib/api/                          contract types (= backend/app/schemas), mock backend, live client
lib/auth/                         account service (mock now; Google SSO via backend, see AUTH.md)
locales/                          uz-Latn.json, ru.json (hand-written), uz-Cyrl.json (generated)
```

## Notes for the team

- **Languages.** URLs use `/uz`, `/uz-cyrl` and `/ru`; the locale codes sent to the API stay `uz-Latn`, `uz-Cyrl` and `ru`. Uzbek Cyrillic is a deterministic transliteration. **The legal member must spot-check it** (legal text is never transliterated).
- **Fonts.** Every font was checked for `ʻ ʼ ў қ ғ ҳ`. Manrope and Pixelify Sans fail, so don't use them.
- **The mock case is placeholder content.** Article numbers are `X/Z/W` and the article text is empty on purpose (no invented law). Quiz questions and stage names need legal review.
- **Backend gap.** Evidence documents need a body endpoint (e.g. `GET /api/scenarios/{id}/documents/{doc}`). `lib/api/live.ts` marks it with a TODO.
