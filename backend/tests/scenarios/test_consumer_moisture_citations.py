"""Ссылки дела consumer_moisture_001 находятся в демо-базе adolat_demo (после `make demo-laws`). Нет базы или законов = skip."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.game_engine import collect_citation_ids
from app.legal.service import get_citation_view, missing_citation_ids
from app.models.legal import LegalDocument
from app.scenarios import load_scenario_dir

pytestmark = pytest.mark.db

SCENARIO_DIR = Path(__file__).resolve().parents[3] / "scenarios" / "consumer_moisture_001"
DEMO_URL = os.environ.get("DEMO_DATABASE_URL", "postgresql+psycopg://adolat:adolat@localhost:5433/adolat_demo")


@pytest.fixture(scope="module")
def demo_db():
    engine = create_engine(DEMO_URL)
    try:
        session = Session(engine)
        has_cprl = session.scalar(select(LegalDocument.id).where(LegalDocument.document_key == "CPRL"))
    except Exception as exc:
        engine.dispose()
        pytest.skip(f"demo-база недоступна ({exc.__class__.__name__}); запустите `make demo-laws`")
    if has_cprl is None:
        session.close()
        engine.dispose()
        pytest.skip("в adolat_demo нет CPRL; запустите `make demo-laws`")
    yield session
    session.close()
    engine.dispose()


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
def test_all_citations_resolve_on_legal_date(demo_db, locale):
    sc = load_scenario_dir(SCENARIO_DIR).scenario
    ids = collect_citation_ids(sc)
    assert len(ids) == 20
    assert missing_citation_ids(demo_db, ids) == set()
    for cid in sorted(ids):
        view = get_citation_view(demo_db, cid, sc.legal_date, locale)
        assert view.edition.status != "unconfirmed", cid  # редакция действует на legal_date
        assert view.text.strip(), cid
        assert view.language == locale, cid
