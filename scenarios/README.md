# Дела (сценарии)

Папки дел хранятся **вне git** (см. `.gitignore`). CI их не копирует и не удаляет на сервере.

- Схема: `backend/app/schemas/scenario.schema.json`, пример: `backend/tests/fixtures/scenarios/test_consumer/`.
- Залить дела на сервер: `make scenarios-upload` (нужен SSH-доступ к vm1), затем перезапустить бэкенд на сервере.
- Перед заливкой каждая статья дела должна быть в seed (`legal_data/citations.yaml` → `make ingest ARGS="run"` → `make seed-dump`), иначе бэкенд не стартует.

## Жизненные ситуации для не юристов (`card.audience: "public"`)

Тот же формат файлов (`scenario.json`, `texts.ru.json`, `texts.uz-Latn.json`, `quiz.json`) и тот же движок. Отличия:
- в карточке `"audience": "public"` (по умолчанию `"professional"` — судебное дело);
- этапы — бытовые шаги, а не процесс. Пример `phone_defect_life_001`: `SITUATION → EVIDENCE → RIGHTS → CLAIM → ESCALATE → RESULTS`;
- действия: решения (`kind: decision`, подпись действия = вопрос), «положить в папку» (`kind: evidence` + флаг `<id>_presented`), «дальше» (`kind: continue`); `legal_note` показывается как «Правило простыми словами»;
- язык — простой, без жаргона; правовые утверждения — только из проверенных статей (как в настоящих делах).

Фронт показывает такие дела без зала суда (`components/play/situation-screen.tsx`), в отдельной дорожке «Жизненные ситуации», а в итоге добавляет конструктор письменной претензии продавцу.
