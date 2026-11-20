# mezon

ADOLAT — учебный симулятор суда по праву Узбекистана. Игрок ведёт дело в роли участника процесса, а AI-наставник подсказывает статьи закона.
Законы берутся с lex.uz и загружаются в базу. Модели локальные (Ollama) или Claude; без них проект тоже работает.

## Быстрый старт

Нужны Docker Desktop, Python 3.12 и Node.js. Подробности: [docs/SETUP.md](docs/SETUP.md).

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/pip install -e "backend[dev]" -e ingestion
cp .env.example .env
make demo-laws   # первый раз: законы в демо-базу (черновик)
make dev-all     # базы, бэкенд :8002/docs и фронт :3000; Ctrl+C останавливает
```

## Документация

- [docs/SETUP.md](docs/SETUP.md): как запустить проект.
- [docs/MODELS.md](docs/MODELS.md): локальные модели и AI.
- [docs/DATA.md](docs/DATA.md): как собираются правовые данные и дела.
- [docs/BACKEND.md](docs/BACKEND.md): спецификация бэкенда.
- [docs/FRONTEND.md](docs/FRONTEND.md): спецификация фронтенда.
- [docs/INGESTION.md](docs/INGESTION.md): спецификация конвейера загрузки законов.
