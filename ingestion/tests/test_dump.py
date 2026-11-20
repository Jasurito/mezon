"""dump → seed.sql.gz → backend/docker/load_seed.py в пустую базу. Нет docker/контейнера db = skip."""

import gzip
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from conftest import BACKEND_DIR, create_migrated_database
from legal_ingestion import pipeline
from legal_ingestion.dump import LEGAL_TABLES, dump_seed
from legal_ingestion.errors import IngestionError
from legal_ingestion.paths import REPO_ROOT


def test_dump_and_load_seed(ws, session_factory, ing_db_url, tmp_path):
    ws.add_doc("TESTDOC", [("ru", "2024-01-01", "v1", "html"), ("uz-Latn", "2024-01-01", "v1", "docx")])
    ws.write_citations('- citation_id: TESTDOC.art.1\n  document_key: TESTDOC\n  article_number: "1"\n  topic: "t"\n')
    from legal_ingestion.embed import embed_texts  # noqa: F401
    from app.rag.embedder import OllamaEmbedder
    import httpx
    import json

    def handler(req):
        body = json.loads(req.content)
        return httpx.Response(200, json={"embeddings": [[0.5, 0.25, 0.125] for _ in body["input"]]})

    assert pipeline.run(ws.paths, session_factory, OllamaEmbedder("http://x", transport=httpx.MockTransport(handler))).ok

    seed = tmp_path / "seed.sql.gz"
    try:
        out = dump_seed(replace(ws.paths, seed=seed, repo_root=REPO_ROOT), ing_db_url)
    except IngestionError as exc:
        pytest.skip(f"docker/контейнер db недоступен: {exc}")
    assert out == seed
    sql = gzip.decompress(seed.read_bytes()).decode("utf-8")
    assert "INSERT INTO public.chunks" in sql and "INSERT INTO public.citations" in sql
    assert "alembic_version" not in sql and "COPY " not in sql
    assert "tsv" not in sql.replace("setval", "")  # generated-колонку база считает сама
    for t in LEGAL_TABLES:
        assert f"public.{t}" in sql
    assert "app_users" not in sql

    # загрузка в пустую базу штатным загрузчиком бэкенда
    seed_url = ing_db_url.rsplit("/", 1)[0] + "/adolat_ingest_seed"
    engine = create_migrated_database(seed_url)
    try:
        env = {
            **os.environ,
            "DATABASE_URL": seed_url,
            "SEED_PATH": str(seed),
            "ADOLAT_NO_DOTENV": "1",
        }
        proc = subprocess.run(
            [sys.executable, str(BACKEND_DIR / "docker" / "load_seed.py")],
            cwd=BACKEND_DIR, env=env, capture_output=True, text=True, timeout=120,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "seed загружен" in proc.stdout
        with engine.connect() as conn, session_factory() as src:
            for t in LEGAL_TABLES:
                n_src = src.execute(text(f"select count(*) from {t}")).scalar()
                assert conn.execute(text(f"select count(*) from {t}")).scalar() == n_src > 0, t
            # векторы и сгенерированный tsv на месте, последовательности продолжают с max(id)
            assert conn.execute(text("select count(*) from chunks where embedding is null or tsv is null")).scalar() == 0
            conn.execute(text("select 1"))
        with engine.begin() as conn:
            conn.execute(text("insert into legal_documents (document_key) values ('NEXT_ONE')"))
    finally:
        engine.dispose()
        admin = create_engine(make_url(seed_url).set(database="postgres"), isolation_level="AUTOCOMMIT")
        with admin.connect() as conn:
            conn.execute(text("DROP DATABASE IF EXISTS adolat_ingest_seed WITH (FORCE)"))
        admin.dispose()
