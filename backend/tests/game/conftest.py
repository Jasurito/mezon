"""Фикстуры игрового API: сценарий test_consumer, тестовые правовые данные, фиксированные часы."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from tests.engine.conftest import BEST, LOSS, PARTIAL  # noqa: F401  (переиспользуются в тестах)
from tests.fixtures.legal_seed import seed_test_legal_data

SCENARIOS_FIXTURES = Path(__file__).parent.parent / "fixtures" / "scenarios"
SCENARIO_ID = "test_consumer"
START = datetime(2026, 11, 21, 9, 0, 0, tzinfo=UTC)


class Clock:
    """Каждый вызов двигает время на 5 секунд: время прохождения предсказуемо."""

    def __init__(self) -> None:
        self.t = START

    def __call__(self) -> datetime:
        self.t += timedelta(seconds=5)
        return self.t


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def seeded_db(db_session):
    seed_test_legal_data(db_session)
    return db_session


@pytest.fixture
def make_client(seeded_db, db_url, clock):
    """Фабрика TestClient: ``with make_client(strict_citations=False) as c``."""
    from fastapi.testclient import TestClient

    from app.config import Settings, get_settings
    from app.db import get_db
    from app.main import create_app
    from app.services.clock import get_now

    @contextmanager
    def _make(strict_citations: bool = True, scenarios_dir: Path = SCENARIOS_FIXTURES):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: seeded_db
        app.dependency_overrides[get_now] = clock
        app.dependency_overrides[get_settings] = lambda: Settings(
            DATABASE_URL=db_url, SCENARIOS_DIR=scenarios_dir, STRICT_CITATIONS=strict_citations
        )
        with TestClient(app) as c:
            yield c

    return _make


@pytest.fixture
def game_client(make_client):
    with make_client() as c:
        yield c


class Api:
    """Тонкая обёртка над клиентом для прохождения игры через HTTP."""

    def __init__(self, client) -> None:
        self.c = client

    def user(self) -> str:
        r = self.c.post("/api/users", json={"display_name": "Азиз"})
        assert r.status_code == 201, r.text
        return r.json()["user_id"]

    def start(self, user_id: str, locale: str = "ru") -> dict:
        r = self.c.post("/api/sessions", json={"user_id": user_id, "scenario_id": SCENARIO_ID, "locale": locale})
        assert r.status_code == 201, r.text
        return r.json()

    def act(self, sid: str, action_id: str, params: dict | None = None):
        body = {"action_id": action_id}
        if params is not None:
            body["params"] = params
        return self.c.post(f"/api/sessions/{sid}/actions", json=body)

    def play(self, sid: str, path) -> list[dict]:
        """Пройти путь; вернуть состояния после каждого шага (без начального)."""
        out = []
        for action_id, params in path:
            r = self.act(sid, action_id, params)
            assert r.status_code == 200, f"{action_id}: {r.text}"
            out.append(r.json())
        return out


@pytest.fixture
def api(game_client) -> Api:
    return Api(game_client)
