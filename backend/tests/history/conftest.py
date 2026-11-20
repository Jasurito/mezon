"""Фикстуры истории: игровой клиент с подменой хранилища истории, LLM и записи событий наставника."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta

import pytest

from app.ai.llm import get_llm
from app.api.mentor import get_event_db_factory
from app.history import get_history
from app.history.store import InMemoryHistoryStore
from app.rag.deps import embedder_dep
from app.rag.embedder import NullEmbedder
from app.services.clock import get_now
from tests.engine.conftest import BEST, LOSS, PARTIAL  # noqa: F401
from tests.game.conftest import SCENARIO_ID, Api, Clock, clock, make_client  # noqa: F401
from tests.mentor.conftest import no_network, seeded_db  # noqa: F401  (seeded_db с чанками RAG)

pytestmark = pytest.mark.db

PRE_OK = {"pre1": "b", "pre2": "a", "pre3": "b"}


class SettableClock:
    """Часы, которыми тест управляет сам: .t = нужный момент."""

    def __init__(self, t: datetime) -> None:
        self.t = t

    def __call__(self) -> datetime:
        return self.t

    def at(self, days: int = 0, hour: int = 12, minute: int = 0) -> "SettableClock":
        self.t = datetime(2026, 11, 20, hour, minute, tzinfo=UTC) + timedelta(days=days)
        return self


@pytest.fixture
def settable_clock() -> SettableClock:
    return SettableClock(datetime(2026, 11, 20, 12, 0, tzinfo=UTC))


@pytest.fixture
def hclient(make_client, seeded_db):
    """with hclient(store, now=None) as c: клиент; store по умолчанию InMemoryHistoryStore."""

    @contextmanager
    def _make(store=None, now=None):
        @contextmanager
        def open_db():
            yield seeded_db

        with make_client() as c:
            ov = c.app.dependency_overrides
            s = store if store is not None else InMemoryHistoryStore()
            ov[get_history] = lambda: s
            ov[get_llm] = lambda: None
            ov[embedder_dep] = lambda: NullEmbedder()
            ov[get_event_db_factory] = lambda: open_db
            if now is not None:
                ov[get_now] = now
            yield c

    return _make


def post_quiz(c, user_id: str, kind: str = "pre", answers: dict | None = None):
    r = c.post(f"/api/quiz/{SCENARIO_ID}/attempts", json={"user_id": user_id, "kind": kind, "answers": answers or PRE_OK})
    assert r.status_code == 201, r.text
    return r.json()
