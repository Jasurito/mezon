"""Reranker в потоке наставника: порядок источников, флаг в событии, режим без AI."""

import re

import pytest
from sqlalchemy import select

from app.ai.llm import FakeLLM
from app.config import Settings, get_settings
from app.models.app_tables import Event
from app.rag.rerank import RerankScore, RerankScores
from app.schemas.rag import MentorAnswer, QueryClassification
from tests.game.conftest import SCENARIOS_FIXTURES
from tests.mentor.helpers import first

pytestmark = pytest.mark.db

QUESTION = "Можно ли вернуть товар с недостатком?"


def set_settings(m, db_url, **kw):
    m.c.app.dependency_overrides[get_settings] = lambda: Settings(
        DATABASE_URL=db_url, SCENARIOS_DIR=SCENARIOS_FIXTURES, **kw
    )


def article_numbers(events):
    return [s["citation"]["article_number"] for s in first(events, "sources")]


def mentor_event(db):
    return list(db.scalars(select(Event).where(Event.type == "mentor_question")))[-1]


def last_first(system, messages):
    """Лучшая оценка последнему кандидату пула, остальным 0: он становится первым."""
    found = re.findall(r'<candidate id="(r\d+)"', messages[0]["content"])
    return RerankScores(scores=[RerankScore(id=i, score=3 if i == found[-1] else 0) for i in found])


def make_llm(rerank_response):
    return FakeLLM(
        {
            QueryClassification: QueryClassification(category="concept"),
            MentorAnswer: MentorAnswer(answer_blocks=[], insufficient_sources=True),
            RerankScores: rerank_response,
        }
    )


def baseline(mentor_client, db_url, llm, **kw):
    with mentor_client(llm=llm) as m:
        set_settings(m, db_url, **kw)
        return m.ask(QUESTION)


def test_llm_reranker_changes_sources_order(mentor_client, seeded_db, db_url):
    plain = baseline(mentor_client, db_url, make_llm(None), RAG_MAX_SOURCES=2, RERANKER="none")
    base_order = article_numbers(plain)
    assert len(base_order) == 2

    llm = make_llm(last_first)
    events = baseline(mentor_client, db_url, llm, RAG_MAX_SOURCES=2, RERANKER="llm", RERANK_CANDIDATES=10)
    assert len(llm.calls_for(RerankScores)) == 1
    assert article_numbers(events) != base_order
    assert [s["source_id"] for s in first(events, "sources")] == ["c1", "c2"]
    assert mentor_event(seeded_db).payload["reranked"] is True


def test_reranker_none_keeps_order_and_no_call(mentor_client, seeded_db, db_url):
    llm = make_llm(last_first)
    baseline(mentor_client, db_url, llm, RAG_MAX_SOURCES=2, RERANKER="none")
    assert llm.calls_for(RerankScores) == []
    assert mentor_event(seeded_db).payload["reranked"] is False


def test_no_rerank_when_candidates_fit(mentor_client, seeded_db, db_url):
    llm = make_llm(last_first)
    baseline(mentor_client, db_url, llm, RAG_MAX_SOURCES=50, RERANKER="llm")
    assert llm.calls_for(RerankScores) == []
    assert mentor_event(seeded_db).payload["reranked"] is False


def test_no_ai_never_reranks(mentor_client, seeded_db, db_url):
    events = baseline(mentor_client, db_url, None, RAG_MAX_SOURCES=2, RERANKER="llm")
    assert first(events, "done")["ai_unavailable"] is True
    assert mentor_event(seeded_db).payload["reranked"] is False


def test_rerank_failure_keeps_rrf_order(mentor_client, seeded_db, db_url):
    base = article_numbers(baseline(mentor_client, db_url, make_llm(None), RAG_MAX_SOURCES=2, RERANKER="none"))
    events = baseline(mentor_client, db_url, make_llm(None), RAG_MAX_SOURCES=2, RERANKER="llm")
    assert article_numbers(events) == base
