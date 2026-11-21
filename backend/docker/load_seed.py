"""Загрузка правового seed (gzip SQL, только данные) при старте бэкенда.

Правовые таблицы на сервере целиком производные от seed. Хэш загруженного файла хранится
в legal_seed_state: если файл изменился (или законы загружены без отметки), правовые таблицы
очищаются и seed загружается заново — в одной транзакции, при ошибке остаются старые данные.
"""
import gzip
import hashlib
import sys
from pathlib import Path

import psycopg

from app.config import get_settings

LEGAL_TABLES = "citations, chunks, article_parts, articles, document_versions, legal_documents"
# the pg_dump seed clears search_path, so statements after it must name the schema
LEGAL_TABLES_QUALIFIED = ", ".join("public." + t.strip() for t in LEGAL_TABLES.split(","))


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
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    dsn = settings.DATABASE_URL.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(dsn) as conn:  # одна транзакция до commit
        conn.execute(
            "CREATE TABLE IF NOT EXISTS public.legal_seed_state ("
            " id int PRIMARY KEY DEFAULT 1 CHECK (id = 1), sha256 text NOT NULL, loaded_at timestamptz NOT NULL DEFAULT now())"
        )
        row = conn.execute("SELECT sha256 FROM public.legal_seed_state WHERE id = 1").fetchone()
        count = conn.execute("SELECT count(*) FROM legal_documents").fetchone()[0]
        if count > 0 and row and row[0] == digest:
            log(f"seed {digest[:12]} уже загружен, пропуск")
            conn.execute(f"ANALYZE {LEGAL_TABLES_QUALIFIED}")  # см. ниже: дёшево, держит статистику свежей
            conn.commit()
            return 0
        if count > 0:
            reason = "seed изменился" if row else "законы загружены без отметки seed"
            log(f"{reason}: правовые таблицы будут заменены")
            conn.execute(f"TRUNCATE {LEGAL_TABLES} RESTART IDENTITY CASCADE")
        conn.execute(gzip.decompress(raw).decode("utf-8"))
        conn.execute(
            "INSERT INTO public.legal_seed_state (id, sha256, loaded_at) VALUES (1, %s, now())"
            " ON CONFLICT (id) DO UPDATE SET sha256 = EXCLUDED.sha256, loaded_at = now()",
            (digest,),
        )
        conn.commit()
        # Статистика для планировщика сразу после массовой загрузки. Без неё маленькие таблицы (document_versions,
        # legal_documents: единицы строк) никогда не попадают под autoanalyze, планировщик оценивает соединение в 1
        # строку и выбирает nested loop: полнотекстовый поиск наставника шёл 38 с вместо 40 мс.
        conn.execute(f"ANALYZE {LEGAL_TABLES_QUALIFIED}")
        conn.commit()
    log(f"seed загружен из {path} (sha256 {digest[:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
