# Claude Code setup (shared)

Everything here is committed so every teammate's Claude Code gets the same tools when it is started from the repo root.

## One-time steps per machine

1. Install the TypeScript language server (needed by the `typescript-lsp` plugin):
   ```
   npm i -g typescript typescript-language-server
   ```
2. Start `claude` from the repo root. Accept the prompts to:
   - trust the project's plugin marketplace and enable its plugins (`.claude/settings.json`);
   - approve the project MCP servers (`.mcp.json`).
3. Run `/mcp` → `context7` → authenticate (free; needed for live library docs).

## What you get

| Kind | Name | Use |
|---|---|---|
| Plugin | `frontend-design` (Anthropic) | Distinctive UI, avoids generic AI look |
| Plugin | `playwright` (Microsoft) | Claude opens the app, clicks, takes screenshots; also used for smoke tests |
| Plugin | `context7` (Upstash) | Current docs: Next.js 16, Phaser 4, Tailwind 4, next-intl, Zustand |
| Plugin | `typescript-lsp` (Anthropic) | Type errors and go-to-definition in TS/TSX |
| MCP | `next-devtools` (Vercel) | Runtime errors, routes, logs from the running `next dev` |
| MCP | `shadcn` | Search and add shadcn/ui components |
| Skills | `vercel-react-best-practices`, `vercel-composition-patterns`, `web-design-guidelines` | React/Next performance, component structure, UI + a11y review |
| Skills | `shadcn` | shadcn/ui usage rules |
| Skills | `phaser-*` (19) | Official Phaser 4 skills: scenes, animations, cameras, tweens, input, scaling, audio, … |

Skill sources and pinned commits: [`skills/SOURCES.md`](skills/SOURCES.md). All skills were read and checked before being committed. Do not add third-party skills without reading them first.

## Stack decisions (frontend)

- **Phaser 4** (not 3): 4.x is current, 3.x is frozen at 3.90, and the official skills target v4.
- **shadcn/ui** on Tailwind for the UI around the game: accessible drawers (evidence, legal panel), dialogs (decision), toasts, progress.
