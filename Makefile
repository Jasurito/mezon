PY ?= backend/.venv/bin/python
BACKEND_PORT ?= 8001

.PHONY: db-up migrate dev test api-client

db-up:
	docker compose up -d db
	@echo "waiting for db..."
	@for i in $$(seq 1 60); do \
		s=$$(docker inspect -f '{{.State.Health.Status}}' $$(docker compose ps -q db) 2>/dev/null); \
		[ "$$s" = "healthy" ] && echo "db healthy" && exit 0; \
		sleep 1; \
	done; echo "db did not become healthy" >&2; exit 1

migrate:
	cd backend && .venv/bin/alembic upgrade head

dev:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port $(BACKEND_PORT)

test: db-up
	cd backend && .venv/bin/pytest -q

api-client:
	@command -v npx >/dev/null 2>&1 || { echo "npx не найден: установите Node.js, чтобы сгенерировать TS-клиент" >&2; exit 1; }
	cd backend && .venv/bin/python -c "import json; from app.main import create_app; json.dump(create_app().openapi(), open('openapi.json','w'), ensure_ascii=False, indent=2)"
	npx openapi-typescript backend/openapi.json -o frontend/lib/api/schema.d.ts
