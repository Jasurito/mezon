# legal_data

Входные и выходные данные конвейера `legal_ingestion` (спецификация: `docs/INGESTION.md`).

```
legal_data/
  raw/               исходные файлы с lex.uz, как скачали, руками не правятся
  processed/         JSONL шагов конвейера и отчёты (check_report.md, diff)
  sources.yaml       описание документов и редакций (по образцу sources.example.yaml)
  citations.yaml     стабильные citation_id (по образцу citations.example.yaml)
  seed.sql.gz        дамп данных правовых таблиц для демо (make seed-dump)
```

## Как положить документ вручную

Автоматического скачивания нет (команда `fetch` выключена): сначала прочитайте условия использования и
robots.txt lex.uz, результат запишите в `terms_of_use` в `sources.yaml`.

1. Откройте документ на lex.uz на нужном языке (ru, uz-Latn, uz-Cyrl) и в нужной редакции.
2. Сохраните страницу целиком средствами браузера («Сохранить как» → «Веб-страница, только HTML»)
   или скачайте DOCX, если сайт его отдаёт. Файл не редактируйте. PDF не поддерживается.
3. Назовите файл `<document_key>_<language>_<effective_from>.<ext>`, например
   `CPRL_ru_2024-01-01.html`. Ключ латиницей, цифры и `_`; язык `ru`, `uz-Latn` или `uz-Cyrl`;
   дата редакции в формате ГГГГ-ММ-ДД, та же, что `effective_from` в `sources.yaml`.
4. Положите файл в `legal_data/raw/`.
5. Добавьте документ и редакцию в `sources.yaml` (шаблон `sources.example.yaml`): `source_url`
   страницы, `effective_from` по lex.uz, `retrieved_at` (когда скачали).
6. Запустите `make ingest ARGS="run --doc <document_key>"`. Новая редакция попадёт в базу со статусом
   `pending_review` и в поиске не участвует.
7. Юрист проверяет статьи по отчёту `processed/check_report.md`, затем:
   `make ingest ARGS='activate --doc <document_key> --version <id> --by "<инициалы>"'`.

## Полезные команды

```
make ingest ARGS="run"                       # все документы
make ingest ARGS="parse --doc CPRL"          # отладка шага, без базы
make ingest ARGS="segment --doc CPRL"
make ingest ARGS="chunk --doc CPRL"
make ingest-check                            # только проверки
make ingest ARGS="diff --doc CPRL"           # что изменилось между редакциями
make seed-dump                               # legal_data/seed.sql.gz (нужен make db-up)
```

Эмбеддинги: `EMBEDDER=ollama-bge-m3` в `.env`, модель скачивается вручную (`ollama pull bge-m3`).
Без `EMBEDDER` векторы остаются пустыми, поиск работает по тексту (sparse).
