import uuid

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.db


def test_events_accepted_and_rejected(api, game_client, seeded_db):
    u = api.user()
    sid = api.start(u)["session_id"]
    body = {
        "user_id": u,
        "session_id": sid,
        "events": [
            {"type": "legal_panel_opened", "payload": {"citation_id": "TEST_CPC.art.1"}},
            {"type": "screen_view", "payload": {"screen": "intro"}, "ts": "2026-11-21T10:00:00Z"},
            {"type": "evidence_opened", "payload": {}},
            {"type": "mentor_opened", "payload": {}},
            {"type": "hack", "payload": {}},
            {"type": "session_finished", "payload": {}},
        ],
    }
    r = game_client.post("/api/events", json=body)
    assert r.status_code == 202, r.text
    assert r.json() == {"accepted": 4, "rejected": 2}

    rows = seeded_db.execute(
        text(
            "select type, payload, ts, session_id::text from events "
            "where user_id = :u and type in ('legal_panel_opened','screen_view','evidence_opened','mentor_opened','hack') "
            "order by id"
        ),
        {"u": u},
    ).all()
    assert [r[0] for r in rows] == ["legal_panel_opened", "screen_view", "evidence_opened", "mentor_opened"]
    assert rows[0][1] == {"citation_id": "TEST_CPC.art.1"}
    assert rows[1][2].isoformat().startswith("2026-11-21T10:00:00")
    assert rows[0][2].year == 2026  # время из get_now
    assert all(r[3] == sid for r in rows)


def test_events_without_session(game_client, seeded_db):
    u = str(uuid.uuid4())
    r = game_client.post("/api/events", json={"user_id": u, "events": [{"type": "screen_view"}]})
    assert r.status_code == 202 and r.json() == {"accepted": 1, "rejected": 0}
    assert seeded_db.execute(
        text("select session_id from events where user_id = :u"), {"u": u}
    ).scalar_one() is None


def test_more_than_50_events_is_422(game_client):
    ev = [{"type": "screen_view", "payload": {}}] * 51
    r = game_client.post("/api/events", json={"user_id": str(uuid.uuid4()), "events": ev})
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR"
    r = game_client.post("/api/events", json={"user_id": str(uuid.uuid4()), "events": ev[:50]})
    assert r.status_code == 202 and r.json()["accepted"] == 50
