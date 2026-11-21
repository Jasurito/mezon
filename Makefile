PY ?= backend/.venv/bin/python
BACKEND_PORT ?= 8001
DEMO_PORT ?= 8002
DEMO_DB_URL ?= postgresql+psycopg://adolat:adolat@localhost:5433/adolat_demo
DEMO_MONGO_URL ?= mongodb://localhost:27018

.PHONY: db-up migrate dev test history-backfill api-client demo demo-reset demo-seed demo-laws dev-all ingest ingest-check seed-dump scenarios-upload

db-up:
	docker compose up -d db mongo
	@echo "waiting for db and mongo..."
	@for svc in db mongo; do \
		ok=0; \
		for i in $$(seq 1 60); do \
			s=$$(docker inspect -f '{{.State.Health.Status}}' $$(docker compose ps -q $$svc) 2>/dev/null); \
			[ "$$s" = "healthy" ] && echo "$$svc healthy" && ok=1 && break; \
			sleep 1; \
		done; \
		[ $$ok = 1 ] || { echo "$$svc did not become healthy" >&2; exit 1; }; \
	done

migrate:
	cd backend && .venv/bin/alembic upgrade head

dev:
	cd backend && .venv/bin/uvicorn app.main:app --reload --port $(BACKEND_PORT)

test: db-up
	cd backend && .venv/bin/pytest -q

# Пересобрать историю MongoDB из Postgres (идемпотентно); нужен MONGO_URL в .env или окружении.
# Один пользователь: make history-backfill USER_ID=<uuid>
history-backfill:
	cd backend && .venv/bin/python -m app.history.backfill $(if $(USER_ID),--user $(USER_ID),)

# Local demo: separate DB adolat_demo with TEST legal data + real laws (drafts) + test and real scenarios.
# LLM settings (LLM_PROVIDER=ollama etc.) come from .env. Swagger: http://localhost:$(DEMO_PORT)/docs
demo-seed: db-up
	cd backend && DATABASE_URL=$(DEMO_DB_URL) .venv/bin/python scripts/demo_seed.py

# Настоящие законы (CPRL, CC2, CPC, ...) в демо-базу как ЧЕРНОВИКИ (--draft-activate: active без verified_by,
# разрешено только для базы *_demo) + ссылки из legal_data/citations.yaml. Идемпотентно.
# Векторы считаются, если Ollama отвечает и в ней есть bge-m3 (EMBEDDER из .env); иначе загрузка без векторов.
demo-laws: demo-seed
	@emb=""; \
	if curl -sf -m 3 http://localhost:11434/api/tags 2>/dev/null | grep -q 'bge-m3'; then \
		echo "Ollama bge-m3 доступна: векторы считаются, если EMBEDDER задан в .env"; \
	else \
		echo "! Ollama или модель bge-m3 недоступны: законы грузятся без векторов"; emb="EMBEDDER="; \
	fi; \
	env $$emb DATABASE_URL=$(DEMO_DB_URL) $(PY) -m legal_ingestion run --draft-activate

demo: demo-laws
	@echo "Swagger: http://localhost:$(DEMO_PORT)/docs   (Ctrl+C to stop)"
	cd backend && DATABASE_URL=$(DEMO_DB_URL) MONGO_URL=$(DEMO_MONGO_URL) MONGO_DB=adolat_demo \
		SCENARIOS_DIR=../scenarios:tests/fixtures/scenarios \
		.venv/bin/uvicorn app.main:app --reload --port $(DEMO_PORT)

# Everything locally in one terminal: databases + demo data + backend (:8002) + frontend live (:3000).
dev-all: demo-laws
	@DEMO_PORT=$(DEMO_PORT) DEMO_DB_URL=$(DEMO_DB_URL) DEMO_MONGO_URL=$(DEMO_MONGO_URL) ./scripts/dev-all.sh

demo-reset:
	docker compose exec -T db psql -U adolat -d postgres -c "DROP DATABASE IF EXISTS adolat_demo"

api-client:
	@command -v npx >/dev/null 2>&1 || { echo "npx не найден: установите Node.js, чтобы сгенерировать TS-клиент" >&2; exit 1; }
	cd backend && .venv/bin/python -c "import json; from app.main import create_app; json.dump(create_app().openapi(), open('openapi.json','w'), ensure_ascii=False, indent=2)"
	npx openapi-typescript backend/openapi.json -o frontend/lib/api/schema.d.ts

# Конвейер загрузки законодательства (docs/INGESTION.md). Пример: make ingest ARGS="run --doc CPRL"
ingest:
	$(PY) -m legal_ingestion $(ARGS)

ingest-check:
	$(PY) -m legal_ingestion check

# Дамп правовых таблиц в legal_data/seed.sql.gz (нужен запущенный контейнер db)
seed-dump:
	$(PY) -m legal_ingestion dump

# Дела хранятся вне git: залить scenarios/ на сервер (нужен SSH-доступ к vm1), потом перезапустить бэкенд там.
VM_HOST ?= deploy@vm1.modeus.cc
VM_SRC ?= /opt/mezon/src
scenarios-upload:
	rsync -az --delete --exclude '.DS_Store' scenarios/ $(VM_HOST):$(VM_SRC)/scenarios/
	@echo "Дела залиты в $(VM_HOST):$(VM_SRC)/scenarios. Перезапустите бэкенд на сервере: systemctl restart mezon-backend"
