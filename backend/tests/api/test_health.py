import pytest
from sqlalchemy.exc import OperationalError

from app.db import get_db

pytestmark = pytest.mark.db


def test_health_empty_db(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["db"] is True
    assert body["articles"] == 0
    assert body["chunks"] == 0
    assert body["scenarios"] == 0
    assert body["llm_configured"] is False
    assert body["embedder"] is None


class _BrokenSession:
    def execute(self, *a, **kw):
        raise OperationalError("SELECT 1", {}, Exception("down"))

    def rollback(self):
        pass

    def close(self):
        pass


def test_health_db_unavailable(client):
    client.app.dependency_overrides[get_db] = lambda: _BrokenSession()
    r = client.get("/api/health")
    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "degraded"
    assert body["db"] is False
    assert body["articles"] is None
    assert body["chunks"] is None
    assert "error" not in body
