# Дела (сценарии)

Папки дел хранятся **вне git** (см. `.gitignore`). CI их не копирует и не удаляет на сервере.

- Схема: `backend/app/schemas/scenario.schema.json`, пример: `backend/tests/fixtures/scenarios/test_consumer/`.
- Залить дела на сервер: `make scenarios-upload` (нужен SSH-доступ к vm1), затем перезапустить бэкенд на сервере.
- Перед заливкой каждая статья дела должна быть в seed (`legal_data/citations.yaml` → `make ingest ARGS="run"` → `make seed-dump`), иначе бэкенд не стартует.
