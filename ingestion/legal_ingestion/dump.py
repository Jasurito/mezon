"""dump: legal_data/seed.sql.gz, только данные правовых таблиц (грузится backend/docker/load_seed.py)."""

from __future__ import annotations

import gzip
import re
import subprocess
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.engine import make_url

from app.models.legal import DocumentVersion
from legal_ingestion.errors import IngestionError
from legal_ingestion.paths import Paths

LEGAL_TABLES = ("legal_documents", "document_versions", "articles", "article_parts", "chunks", "citations")


# pg_dump >= 16.10 добавляет psql-метакоманды \restrict / \unrestrict: через psycopg они не выполняются
_PSQL_META = re.compile(rb"^\\(?:un)?restrict\b.*\n?", re.MULTILINE)


def pg_dump_command(database_url: str, service: str = "db") -> list[str]:
    url = make_url(database_url)
    cmd = ["docker", "compose", "exec", "-T", service, "pg_dump", "--data-only", "--no-owner", "--no-privileges"]
    # COPY ... FROM stdin load_seed.py выполнить не может, поэтому INSERT'ы; без колонок chunks.tsv (generated)
    cmd += ["--column-inserts", "--rows-per-insert=200"]
    for t in LEGAL_TABLES:
        cmd.append(f"--table=public.{t}")
    cmd += ["-U", url.username or "adolat", "-d", url.database or "adolat"]
    return cmd


def sequence_fixups() -> str:
    """pg_dump с --table не переносит значения serial-последовательностей: выставляем их сами,
    иначе следующий run ingestion после загрузки seed упрётся в дубли id."""
    lines = ["", "-- sequences"]
    for t in LEGAL_TABLES:
        if t == "citations":  # текстовый первичный ключ
            continue
        lines.append(
            f"SELECT pg_catalog.setval(pg_get_serial_sequence('public.{t}', 'id'), "
            f"COALESCE((SELECT max(id) FROM public.{t}), 1), (SELECT max(id) IS NOT NULL FROM public.{t}));"
        )
    return "\n".join(lines) + "\n"


def assert_no_drafts(session_factory) -> None:
    """Дамп не должен содержать черновиков: active-редакция без verified_by = отказ."""
    session = session_factory()
    try:
        n = session.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.review_status == "active",
                (DocumentVersion.verified_by.is_(None)) | (func.trim(DocumentVersion.verified_by) == ""),
            )
        )
    finally:
        session.close()
    if n:
        raise IngestionError(
            f"dump: в базе {n} активных редакций без verified_by (черновики, загруженные через --draft-activate). "
            "Дамп из такой базы делать нельзя: подтвердите редакции (команда activate) или снимайте дамп с основной базы."
        )


def dump_seed(paths: Paths, database_url: str, service: str = "db") -> Path:
    """Снять дамп через pg_dump внутри контейнера db (версия совпадает с сервером) и сжать gzip."""
    cmd = pg_dump_command(database_url, service)
    try:
        proc = subprocess.run(cmd, cwd=paths.repo_root, capture_output=True, timeout=600)
    except FileNotFoundError as exc:
        raise IngestionError("dump: docker не найден; pg_dump запускается в контейнере db (make db-up)") from exc
    except subprocess.TimeoutExpired as exc:
        raise IngestionError("dump: pg_dump не завершился за 10 минут") from exc
    if proc.returncode != 0:
        raise IngestionError(
            "dump: pg_dump не удался (запущен ли контейнер? make db-up):\n" + proc.stderr.decode("utf-8", "replace")[:1000]
        )
    out = paths.seed_file
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with open(tmp, "wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
        gz.write(_PSQL_META.sub(b"", proc.stdout))
        gz.write(sequence_fixups().encode())
    tmp.replace(out)
    return out
