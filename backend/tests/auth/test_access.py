"""IDOR: данные аккаунта доступны только его владельцу; гостевые id работают без входа."""

import uuid

import pytest

from tests.auth.conftest import H, add_session, as_token

pytestmark = pytest.mark.db

Q = {"kind": "pre", "answers": {}}


def calls(uid, sid):
    ev = {"user_id": uid, "events": [{"type": "screen_view", "payload": {}}]}
    return [
        ("get", f"/api/users/{uid}", None),
        ("patch", f"/api/users/{uid}", {"display_name": "hacked"}),
        ("get", f"/api/users/{uid}/sessions", None),
        ("get", f"/api/users/{uid}/dashboard", None),
        ("get", f"/api/users/{uid}/activity", None),
        ("post", "/api/sessions", {"user_id": uid, "scenario_id": "x"}),
        ("post", "/api/quiz/x/attempts", {"user_id": uid, **Q}),
        ("post", "/api/events", ev),
        ("get", f"/api/sessions/{sid}", None),
        ("patch", f"/api/sessions/{sid}", {"locale": "ru"}),
        ("post", f"/api/sessions/{sid}/actions", {"action_id": "x"}),
        ("get", f"/api/sessions/{sid}/result", None),
        ("get", f"/api/sessions/{sid}/history", None),
        ("post", f"/api/sessions/{sid}/npc/c/ask", {"text": "hi"}),
        ("post", "/api/mentor/ask", {"session_id": str(sid), "question": "hi"}),
        ("post", "/api/events", {"user_id": str(uuid.uuid4()), "session_id": str(sid), "events": []}),
    ]


def do(c, method, url, body):
    return getattr(c, method)(url, headers=H, **({"json": body} if body is not None else {}))


@pytest.fixture
def world(client, db_session, make_account):
    a, ta = make_account("a@example.com")
    b, tb = make_account("b@example.com")
    sid = add_session(db_session, a)
    return client, a, ta, b, tb, sid


def test_other_account_gets_403(world):
    c, a, ta, b, tb, sid = world
    as_token(c, tb)
    for m, url, body in calls(a, sid):
        r = do(c, m, url, body)
        assert r.status_code == 403, (m, url, r.text)
        assert r.json()["error"]["code"] == "FORBIDDEN"


def test_no_session_gets_401(world):
    c, a, ta, b, tb, sid = world
    as_token(c, None)
    for m, url, body in calls(a, sid):
        r = do(c, m, url, body)
        assert r.status_code == 401, (m, url, r.text)
        assert r.json()["error"]["code"] == "UNAUTHORIZED"


def test_owner_passes(world):
    c, a, ta, b, tb, sid = world
    as_token(c, ta)
    for m, url, body in calls(a, sid):
        r = do(c, m, url, body)
        assert r.status_code not in (401, 403), (m, url, r.status_code, r.text)
    assert c.get(f"/api/users/{a}").json()["user_id"] == a
    assert c.get(f"/api/users/{a}/dashboard").status_code == 200
    assert c.get(f"/api/users/{a}/sessions").json()["total"] == 1


def test_expired_session_loses_access(world, db_session):
    from sqlalchemy import text

    c, a, ta, *_ = world
    as_token(c, ta)
    assert c.get(f"/api/users/{a}").status_code == 200
    db_session.execute(text("UPDATE auth_sessions SET revoked_at = now()"))
    db_session.commit()
    assert c.get(f"/api/users/{a}").status_code == 401


def test_guests_work_without_login(client, make_guest, db_session):
    g = make_guest()
    sid = add_session(db_session, g)
    client.cookies.clear()
    assert client.get(f"/api/users/{g}").status_code == 200
    assert client.patch(f"/api/users/{g}", json={"display_name": "x"}).status_code == 200
    assert client.get(f"/api/users/{g}/sessions").json()["total"] == 1
    assert client.get(f"/api/users/{g}/dashboard").status_code == 200
    assert client.get(f"/api/users/{g}/activity").status_code == 200
    assert client.post("/api/events", json={"user_id": g, "events": [{"type": "screen_view", "payload": {}}]}).status_code == 202
    assert client.get(f"/api/sessions/{sid}").status_code not in (401, 403)


def test_account_session_may_use_guest_ids(world, make_guest):
    c, a, ta, *_ = world
    g = make_guest()
    as_token(c, ta)
    assert c.get(f"/api/users/{g}").status_code == 200


def test_unknown_user_still_404(client):
    assert client.get(f"/api/users/{uuid.uuid4()}").status_code == 404
