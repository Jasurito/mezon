"""Общие фикстуры. Никаких autouse и подключений при импорте: тесты движка работают без Docker."""
import os

# До импорта app.*: тесты не читают локальный .env (ключи, LLM_PROVIDER=ollama и т. п.)
# и не видят переменных LLM/RAG из окружения разработчика.
os.environ["ADOLAT_NO_DOTENV"] = "1"
for _var in ("ANTHROPIC_API_KEY", "LLM_PROVIDER", "OLLAMA_URL", "OLLAMA_MODEL", "EMBEDDER", "RAG_MAX_SOURCES", "MONGO_URL", "MONGO_DB"):
    os.environ.pop(_var, None)

from pathlib import Path  # noqa: E402

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

BACKEND_DIR = Path(__file__).resolve().parents[1]


def make_alembic_config(url: str) -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "migrations"))
    cfg.attributes["url"] = url
    cfg.attributes["configure_logging"] = False
    return cfg


@pytest.fixture(scope="session")
def db_url() -> str:
    return os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://adolat:adolat@localhost:5433/adolat_test",
    )


@pytest.fixture(scope="session")
def alembic_config(db_url):
    return make_alembic_config(db_url)


@pytest.fixture(scope="session")
def db_engine(db_url):
    url = make_url(db_url)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": url.database}
            ).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    except Exception as exc:
        pytest.skip(f"Postgres недоступен ({exc.__class__.__name__}); запустите `make db-up`")
    finally:
        admin_engine.dispose()

    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    command.upgrade(make_alembic_config(db_url), "head")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    conn = db_engine.connect()
    trans = conn.begin()
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        conn.close()


@pytest.fixture
def client(db_session, db_url):
    from fastapi.testclient import TestClient

    from app.config import Settings, get_settings
    from app.db import get_db
    from app.main import create_app

    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_settings] = lambda: Settings(
        DATABASE_URL=db_url,
        # без сценариев: реальные дела из scenarios/ требуют законов в базе (их грузит `make demo-laws`)
        SCENARIOS_DIR=BACKEND_DIR / "tests" / "fixtures" / "no_scenarios",
    )
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mongo_url() -> str:
    return os.environ.get("TEST_MONGO_URL", "mongodb://localhost:27018")


@pytest.fixture
def mongo_store(mongo_url):
    """MongoHistoryStore на отдельной базе adolat_test; коллекции чистятся перед тестом; недоступна = skip."""
    from pymongo import MongoClient

    probe = MongoClient(mongo_url, serverSelectionTimeoutMS=800)
    try:
        probe.admin.command("ping")
    except Exception as exc:
        probe.close()
        pytest.skip(f"MongoDB недоступна ({exc.__class__.__name__}); запустите `make db-up`")
    for coll in ("session_history", "user_activity"):
        probe["adolat_test"][coll].delete_many({})
    probe.close()

    from app.history.mongo import MongoHistoryStore

    store = MongoHistoryStore(mongo_url, "adolat_test", timeout_ms=800)
    store.ensure_indexes()
    yield store
    store.close()
