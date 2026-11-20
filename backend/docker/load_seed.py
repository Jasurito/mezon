"""Загрузка правового seed (gzip SQL, data-only) при пустой таблице legal_documents."""
import gzip
import sys
from pathlib import Path

import psycopg

from app.config import get_settings


def log(msg: str) -> None:
    print(f"[load_seed] {msg}", flush=True)


def main() -> int:
    settings = get_settings()
    path: Path | None = settings.SEED_PATH
    if path is None:
        log("SEED_PATH не задан, загрузка seed пропущена")
        return 0
    if not path.is_file():
        log(f"файл {path} не найден, загрузка seed пропущена")
        return 0

    dsn = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(dsn) as conn:
        count = conn.execute("SELECT count(*) FROM legal_documents").fetchone()[0]
        if count > 0:
            log(f"legal_documents уже содержит {count} строк, seed пропущен")
            return 0
        with gzip.open(path, "rt", encoding="utf-8") as f:
            sql = f.read()
        conn.execute(sql)
        conn.commit()
    log(f"seed загружен из {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
