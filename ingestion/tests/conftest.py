"""Общие фикстуры ingestion-тестов. БД: отдельная база adolat_ingest_test, alembic upgrade head;
нет Postgres = skip (как в backend/tests/conftest.py)."""

import os
import sys
from pathlib import Path

# До импорта app.*: локальный .env разработчика не должен влиять на тесты
os.environ["ADOLAT_NO_DOTENV"] = "1"
for _var in ("ANTHROPIC_API_KEY", "LLM_PROVIDER", "OLLAMA_URL", "OLLAMA_MODEL", "EMBEDDER", "MONGO_URL", "MONGO_DB"):
    os.environ.pop(_var, None)

sys.path.insert(0, str(Path(__file__).parent))

import pytest  # noqa: E402
from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

import ing_synthetic as syn  # noqa: E402
from legal_ingestion.paths import Paths  # noqa: E402

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
LEGAL_TABLES = "citations, chunks, article_parts, articles, document_versions, legal_documents"


def alembic_config(url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["url"] = url
    cfg.attributes["configure_logging"] = False
    return cfg


def create_migrated_database(url: str):
    """Создать (если нет) базу, пересоздать схему public и накатить миграции. Нет Postgres → skip."""
    u = make_url(url)
    admin = create_engine(u.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin.connect() as conn:
            if not conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": u.database}).scalar():
                conn.execute(text(f'CREATE DATABASE "{u.database}"'))
    except Exception as exc:
        pytest.skip(f"Postgres недоступен ({exc.__class__.__name__}); запустите `make db-up`")
    finally:
        admin.dispose()
    engine = create_engine(u)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    command.upgrade(alembic_config(url), "head")
    return engine


@pytest.fixture(scope="session")
def ing_db_url() -> str:
    return os.environ.get(
        "TEST_INGEST_DATABASE_URL", "postgresql+psycopg://adolat:adolat@localhost:5433/adolat_ingest_test"
    )


@pytest.fixture(scope="session")
def ing_engine(ing_db_url):
    engine = create_migrated_database(ing_db_url)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(ing_engine):
    with ing_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {LEGAL_TABLES} RESTART IDENTITY CASCADE"))
    yield sessionmaker(bind=ing_engine, autoflush=False, expire_on_commit=False)
    with ing_engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {LEGAL_TABLES} RESTART IDENTITY CASCADE"))


class Workspace:
    """Временный legal_data с sources.yaml; documents можно дописывать и перезаписывать yaml."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.legal = root / "legal_data"
        self.legal.mkdir()
        self.paths = Paths(
            legal_dir=self.legal,
            scenarios_dir=root / "scenarios",
            processed=root / "processed",
            repo_root=root,
        )
        self.documents: list[dict] = []

    def add_doc(
        self,
        key: str,
        editions: list[tuple[str, str, str, str]],  # (язык, дата, вариант, формат)
        *,
        verified_by: str | None = "QA",
        known_gaps: dict | None = None,
    ) -> dict:
        versions = []
        for lang, eff, variant, fmt in editions:
            rel = syn.write_source(self.legal, key, lang, eff, variant, fmt)
            versions.append(syn.version_entry(key, lang, eff, rel, verified_by))
        existing = next((d for d in self.documents if d["document_key"] == key), None)
        if existing:
            existing["versions"].extend(versions)
            doc = existing
        else:
            doc = syn.document_entry(key, versions, known_gaps)
            self.documents.append(doc)
        syn.write_sources_yaml(self.legal, self.documents)
        return doc

    def write_citations(self, text_: str) -> None:
        (self.legal / "citations.yaml").write_text(text_, encoding="utf-8")


@pytest.fixture
def ws(tmp_path) -> Workspace:
    return Workspace(tmp_path)
