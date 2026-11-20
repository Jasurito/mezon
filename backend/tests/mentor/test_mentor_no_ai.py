"""Режим без AI: нормы найдены, объяснения нет, LLM не вызывается."""

import pytest

from app.ai.llm import get_llm
from app.config import Settings
from tests.mentor.helpers import first, names

pytestmark = pytest.mark.db


def test_no_key_means_no_llm():
    assert get_llm(Settings(ANTHROPIC_API_KEY=None)) is None
    assert get_llm(Settings(ANTHROPIC_API_KEY="  ")) is None


def test_no_key_returns_sources_and_ai_unavailable(mentor_client):
    with mentor_client(llm=None) as m:
        events = m.ask("Можно ли вернуть товар с недостатком?")
    assert names(events) == ["sources", "done"]
    sources = first(events, "sources")
    assert sources and sources[0]["source_id"] == "c1"
    citation = sources[0]["citation"]
    assert citation["article_number"] == "10"
    assert citation["citation_id"] == "TEST_RAG.art.10"
    assert citation["source_url"] and citation["text"]
    done = first(events, "done")
    assert done["ai_unavailable"] is True
    assert done["insufficient_sources"] is False
    assert done["message"].startswith("AI-объяснение сейчас недоступно")
    assert done["disclaimer"] == "Образовательное объяснение, не юридическая консультация"


def test_no_key_message_follows_question_language(mentor_client):
    with mentor_client(llm=None) as m:
        events = m.ask("Sifatsiz tovarni qaytarish mumkinmi?", locale="ru")
    done = first(events, "done")
    assert done["ai_unavailable"] is True
    assert "AI tushuntirishi" in done["message"]
    assert done["disclaimer"].startswith("Ta’limiy")
    assert first(events, "sources")[0]["citation"]["language"] == "uz-Latn"


def test_no_key_still_applies_threshold(mentor_client):
    with mentor_client(llm=None) as m:
        events = m.ask("Как оформить развод через загс?")
    done = first(events, "done")
    assert first(events, "sources") == []
    assert done["insufficient_sources"] is True and done["ai_unavailable"] is False
