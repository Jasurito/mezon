# Mezon: notes for Claude Code

Monorepo: `frontend/` (Next.js 16 + Phaser 4), `backend/` (FastAPI, Postgres/pgvector, MongoDB history), `deploy/vm1/` (systemd + CI/CD), `docs/` (specs).
Shared tooling is in `.claude/` (see `.claude/README.md`).

## Knowledge graph (graphify): use it first

A knowledge graph of this repo is committed in `graphify-out/`:
- `GRAPH_REPORT.md`: communities, god nodes, surprising connections, open questions (read this first for orientation)
- `graph.json`: the graph data (used by `graphify query`)
- `graph.html`: interactive view, open in a browser

Before searching the code for architecture or "how does X connect to Y" questions, query the graph:

```
graphify query "how does the mentor build its answer from legal sources?"
graphify path "PlayScreen" "perform_action"
graphify explain "HistoryStore"
```

In Claude Code use the `/graphify` skill (`.claude/skills/graphify`); it installs the `graphifyy` package on first use.
Fall back to grep/Read for a single symbol lookup or when the graph has no answer.

**Keep it fresh.** After significant changes run `/graphify . --update` (it re-extracts only changed files), then commit the three files above. `.claude/` (vendored skills) is excluded from the graph on purpose. Graphify's local state in `graphify-out/` (cache, manifest) is git-ignored.
