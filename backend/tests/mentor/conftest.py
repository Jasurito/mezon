"""Фикстуры наставника: тестовый корпус с чанками, клиент с подменой LLM, эмбеддера и записи событий."""

from __future__ import annotations

from contextlib import contextmanager

import pytest

from app.ai.llm import get_llm
from app.api.mentor import get_event_db_factory
from app.rag.deps import embedder_dep
from app.rag.embedder import NullEmbedder
from tests.fixtures.legal_seed import seed_test_legal_data
from tests.fixtures.rag_seed import seed_test_chunks
from tests.game.conftest import Api, Clock, clock, make_client  # noqa: F401  (переиспользуются)
from tests.mentor.helpers import parse_sse


@pytest.fixture
def seeded_db(db_session):
    seed_test_legal_data(db_session)
    seed_test_chunks(db_session)
    return db_session


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Настоящий клиент Anthropic в тестах создавать нельзя."""

    def boom(*a, **kw):
        raise AssertionError("тест пытается создать настоящий клиент Anthropic")

    monkeypatch.setattr("anthropic.Anthropic", boom)


class Mentor:
    def __init__(self, client) -> None:
        self.c = client

    def ask(self, question: str, **extra):
        body = {"question": question, "locale": "ru", **extra}
        r = self.c.post("/api/mentor/ask", json=body)
        assert r.status_code == 200, r.text
        assert r.headers["content-type"].startswith("text/event-stream")
        return parse_sse(r.text)


@pytest.fixture
def mentor_client(make_client, seeded_db):
    """with mentor_client(llm=FakeLLM(...)) as m: m.ask("вопрос"); llm=None = режим без AI."""

    @contextmanager
    def _make(llm=None, embedder=None):
        @contextmanager
        def open_db():
            yield seeded_db

        with make_client() as c:
            ov = c.app.dependency_overrides
            ov[get_llm] = lambda: llm
            ov[embedder_dep] = lambda: embedder or NullEmbedder()
            ov[get_event_db_factory] = lambda: open_db
            yield Mentor(c)

    return _make
