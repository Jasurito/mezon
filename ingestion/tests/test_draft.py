"""--draft-activate: черновики (verified_by: null) как active только в базе *_demo; dump их не пропускает."""

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.models.legal import DocumentVersion
from conftest import LEGAL_TABLES, create_migrated_database
from legal_ingestion import pipeline
from legal_ingestion.cli import main as cli_main
from legal_ingestion.dump import assert_no_drafts
from legal_ingestion.errors import IngestionError

KEY = "TESTDOC"
EDITIONS = [("ru", "2024-01-01", "v1", "html")]


@pytest.fixture
def demo_factory(ing_db_url):
    url = make_url(ing_db_url).set(database="adolat_ingest_demo")
    engine = create_migrated_database(url.render_as_string(hide_password=False))
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS adolat_ingest_demo WITH (FORCE)"))
    admin.dispose()


def statuses(sf):
    with sf() as s:
        return [(v.review_status, v.verified_by) for v in s.scalars(select(DocumentVersion))]


def test_draft_activate_refused_outside_demo_database(ws, session_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    with pytest.raises(IngestionError, match="_demo"):
        pipeline.run(ws.paths, session_factory, draft_activate=True)
    assert statuses(session_factory) == []  # ничего не загружено


def test_cli_draft_activate_refused_outside_demo_database(ws, session_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    url = session_factory.kw["bind"].url.render_as_string(hide_password=False)
    code = cli_main(
        ["--legal-dir", str(ws.legal), "--processed-dir", str(ws.paths.processed_dir),
         "run", "--draft-activate", "--database-url", url]
    )
    assert code == 2
    assert statuses(session_factory) == []


def test_without_flag_draft_stays_pending_review(ws, session_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    pipeline.run(ws.paths, session_factory)
    assert statuses(session_factory) == [("pending_review", None)]


def test_draft_activate_in_demo_database_is_idempotent_and_check_still_fails(ws, demo_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    res = pipeline.run(ws.paths, demo_factory, draft_activate=True)
    assert statuses(demo_factory) == [("active", None)]
    # check по-прежнему считает черновик ошибкой
    assert any("без verified_by" in i.message for i in res.check.errors)
    again = pipeline.run(ws.paths, demo_factory, draft_activate=True)
    assert [e.action for e in again.editions] == ["unchanged"]
    assert statuses(demo_factory) == [("active", None)]


def test_draft_activate_promotes_already_loaded_pending(ws, demo_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    pipeline.run(ws.paths, demo_factory)
    assert statuses(demo_factory) == [("pending_review", None)]
    pipeline.run(ws.paths, demo_factory, draft_activate=True)
    assert statuses(demo_factory) == [("active", None)]


def test_dump_refuses_active_version_without_verified_by(ws, demo_factory):
    ws.add_doc(KEY, EDITIONS, verified_by=None)
    pipeline.run(ws.paths, demo_factory, draft_activate=True)
    with pytest.raises(IngestionError, match="без verified_by"):
        assert_no_drafts(demo_factory)
    url = demo_factory.kw["bind"].url.render_as_string(hide_password=False)
    assert cli_main(["--legal-dir", str(ws.legal), "dump", "--database-url", url]) == 2


def test_dump_guard_passes_for_verified(ws, session_factory):
    ws.add_doc(KEY, EDITIONS)  # verified_by="QA"
    pipeline.run(ws.paths, session_factory)
    assert_no_drafts(session_factory)
