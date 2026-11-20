#!/usr/bin/env bash
# Backend (demo DB + test case) and frontend (live mode) in one terminal. Ctrl+C stops both.
# Run via `make dev-all` (it starts the databases and loads demo data first).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEMO_PORT="${DEMO_PORT:-8002}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
DEMO_DB_URL="${DEMO_DB_URL:-postgresql+psycopg://adolat:adolat@localhost:5433/adolat_demo}"
DEMO_MONGO_URL="${DEMO_MONGO_URL:-mongodb://localhost:27018}"
export COREPACK_ENABLE_DOWNLOAD_PROMPT=0

if ! curl -sf -o /dev/null --max-time 2 http://localhost:11434/api/tags; then
  echo "! Ollama не отвечает на :11434 — наставник и NPC будут без AI (запустите приложение Ollama или 'ollama serve')."
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "> ставлю зависимости фронта (один раз, пару минут)..."
  (cd "$ROOT/frontend" && corepack pnpm install --frozen-lockfile)
fi

pids=()
cleanup() {
  trap - INT TERM EXIT
  echo; echo "> останавливаю бэк и фронт..."
  for pid in "${pids[@]}"; do pkill -TERM -P "$pid" 2>/dev/null || true; kill -TERM "$pid" 2>/dev/null || true; done
  wait 2>/dev/null || true
}
trap cleanup INT TERM EXIT

(
  cd "$ROOT/backend"
  DATABASE_URL="$DEMO_DB_URL" MONGO_URL="$DEMO_MONGO_URL" MONGO_DB=adolat_demo \
  SCENARIOS_DIR=../scenarios:tests/fixtures/scenarios \
  CORS_ORIGINS="http://localhost:$FRONTEND_PORT" \
    .venv/bin/uvicorn app.main:app --reload --port "$DEMO_PORT" 2>&1 | sed -u 's/^/[back]  /'
) &
pids+=($!)

(
  cd "$ROOT/frontend"
  NEXT_PUBLIC_API_MODE=live NEXT_PUBLIC_API_BASE="http://localhost:$DEMO_PORT" \
    corepack pnpm dev --port "$FRONTEND_PORT" 2>&1 | sed -u 's/^/[front] /'
) &
pids+=($!)

echo "> фронт:   http://localhost:$FRONTEND_PORT"
echo "> бэкенд:  http://localhost:$DEMO_PORT/docs"
echo "> Ctrl+C — остановить оба"
wait
