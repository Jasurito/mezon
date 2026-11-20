"""Фикстуры авторизации: приложение с настраиваемыми Settings, помощники регистрации и входа."""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

import pytest

from tests.conftest import BACKEND_DIR

pytestmark = pytest.mark.db

ORIGIN = "http://localhost:3000"
H = {"Origin": ORIGIN}
PASSWORD = "correct horse battery"
GOOGLE_ID = "test-client.apps.googleusercontent.com"
GOOGLE_SECRET = "test-secret"
REDIRECT = "http://localhost:3000/api/auth/google/callback"


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@pytest.fixture
def app_factory(db_session, db_url):
    """build(**settings) -> (app, TestClient). Клиенты закрываются по окончании теста."""
    from fastapi.testclient import TestClient

    from app.config import Settings, get_settings
    from app.db import get_db
    from app.main import create_app

    clients = []

    def build(**overrides):
        base = dict(
            DATABASE_URL=db_url,
            SCENARIOS_DIR=BACKEND_DIR / "tests" / "fixtures" / "no_scenarios",
            COOKIE_SECURE=False,  # TestClient ходит по http, Secure-cookie jar не вернул бы
            CORS_ORIGINS=[ORIGIN],
            PUBLIC_BASE_URL=ORIGIN,
            GOOGLE_CLIENT_ID=GOOGLE_ID,
            GOOGLE_CLIENT_SECRET=GOOGLE_SECRET,
            GOOGLE_REDIRECT_URI=REDIRECT,
        )
        base.update(overrides)
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        app.dependency_overrides[get_settings] = lambda: Settings(**base)
        c = TestClient(app, follow_redirects=False)
        c.__enter__()
        clients.append(c)
        return app, c

    yield build
    for c in clients:
        c.__exit__(None, None, None)


@pytest.fixture
def app_and_client(app_factory):
    return app_factory()


@pytest.fixture
def app(app_and_client):
    return app_and_client[0]


@pytest.fixture
def client(app_and_client):
    return app_and_client[1]


def signup(c, email="a@example.com", name="Aziz", password=PASSWORD, guest=None, origin=ORIGIN):
    body = {"display_name": name, "email": email, "password": password, "guest_user_id": guest}
    return c.post("/api/auth/signup", json=body, headers={"Origin": origin})


def login(c, email="a@example.com", password=PASSWORD, guest=None, origin=ORIGIN):
    body = {"email": email, "password": password, "guest_user_id": guest}
    return c.post("/api/auth/login", json=body, headers={"Origin": origin})


def as_token(c, token: str | None):
    """Переключить клиент на сессию с данным токеном (None = аноним)."""
    c.cookies.clear()
    if token:
        c.cookies.set("mezon_session", token)


@pytest.fixture
def make_account(client):
    """make_account(email) -> (user_id, token). Клиент остаётся анонимным."""

    def make(email: str, guest: str | None = None):
        client.cookies.clear()
        r = signup(client, email=email, guest=guest)
        assert r.status_code == 201, r.text
        token = client.cookies.get("mezon_session")
        client.cookies.clear()
        return r.json()["id"], token

    return make


@pytest.fixture
def make_guest(client):
    def make() -> str:
        r = client.post("/api/users", json={"display_name": "guest"})
        assert r.status_code == 201
        return r.json()["user_id"]

    return make


def add_session(db, user_id, finished=False, score=None):
    from app.models.app_tables import GameSession

    s = GameSession(
        id=uuid.uuid4(), user_id=uuid.UUID(str(user_id)), scenario_id="x", scenario_version="1", locale="ru",
        started_at=datetime(2026, 11, 1, tzinfo=UTC),
        finished_at=datetime(2026, 11, 1, 1, tzinfo=UTC) if finished else None,
        outcome="best" if finished else None, score=score,
    )
    db.add(s)
    db.commit()
    return s.id
