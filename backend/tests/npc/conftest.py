"""Фикстуры NPC: клиент игрового API с подменой LLM."""

from __future__ import annotations

from contextlib import contextmanager

import pytest

from app.ai.llm import get_llm
from tests.engine.conftest import BEST
from tests.game.conftest import Api, Clock, clock, make_client, seeded_db  # noqa: F401  (переиспользуются)


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **kw):
        raise AssertionError("тест пытается создать настоящий клиент Anthropic")

    monkeypatch.setattr("anthropic.Anthropic", boom)


class Npc:
    def __init__(self, client) -> None:
        self.api = Api(client)
        self.c = client
        self.sid: str | None = None

    def start(self, locale: str = "ru", steps: int = 0) -> str:
        """Новая сессия; steps = сколько первых действий BEST выполнить."""
        self.sid = self.api.start(self.api.user(), locale)["session_id"]
        self.api.play(self.sid, BEST[:steps])
        return self.sid

    def ask(self, character: str, text: str, sid: str | None = None):
        return self.c.post(f"/api/sessions/{sid or self.sid}/npc/{character}/ask", json={"text": text})


@pytest.fixture
def npc_client(make_client):
    """with npc_client(llm=...) as n: n.start(steps=7); n.ask("plaintiff", "..."); llm=None = без AI."""

    @contextmanager
    def _make(llm=None):
        with make_client() as c:
            c.app.dependency_overrides[get_llm] = lambda: llm
            yield Npc(c)

    return _make


from tests.engine.conftest import scenario  # noqa: E402,F401  (фикстура сценария test_consumer)
