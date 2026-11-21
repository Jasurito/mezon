import pytest
from argon2 import PasswordHasher
from sqlalchemy import select, text

from app.models.app_tables import User
from app.models.auth import AuthSession
from tests.auth.conftest import H, ORIGIN, PASSWORD, login, sha, signup

pytestmark = pytest.mark.db


def test_signup_me_logout_login_cycle(client):
    r = signup(client, email="  Aziz@Example.com ")
    assert r.status_code == 201
    body = r.json()
    assert set(body) == {"id", "display_name", "email", "provider", "avatar_url", "audience"}
    assert body["audience"] is None  # not chosen
    assert body["email"] == "aziz@example.com" and body["provider"] == "email" and body["display_name"] == "Aziz"
    assert "password" not in r.text and "argon2" not in r.text

    me = client.get("/api/auth/me")
    assert me.status_code == 200 and me.json() == body

    out = client.post("/api/auth/logout", json={}, headers=H)
    assert out.status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    r = login(client, email="AZIZ@example.com")
    assert r.status_code == 200 and r.json()["id"] == body["id"]
    assert client.get("/api/auth/me").json()["id"] == body["id"]


def test_me_without_session_is_401(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401 and r.json()["error"]["code"] == "UNAUTHORIZED"


def test_duplicate_email_is_409(client):
    assert signup(client).status_code == 201
    client.cookies.clear()
    r = signup(client, email="A@EXAMPLE.COM")
    assert r.status_code == 409 and r.json()["error"]["code"] == "EMAIL_EXISTS"


@pytest.mark.parametrize(
    "kw",
    [
        {"password": "abc1234"},
        {"password": "x" * 129},
        {"email": "not-an-email"},
        {"email": "same@example.com", "password": "same@example.com"},
        {"name": "   "},
    ],
)
def test_signup_validation(client, kw):
    r = signup(client, **kw)
    assert r.status_code == 422 and r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert '"password":' not in r.text  # поле пароля не возвращается ни в каком виде
    secret = kw.get("password")
    if secret and "@" not in secret:
        assert secret not in r.text


def test_password_hashed_with_argon2id_and_token_stored_hashed(client, db_session):
    signup(client)
    user = db_session.execute(select(User).where(User.email == "a@example.com")).scalar_one()
    assert user.password_hash.startswith("$argon2id$") and PASSWORD not in user.password_hash
    token = client.cookies.get("mezon_session")
    row = db_session.execute(select(AuthSession)).scalar_one()
    assert row.token_hash == sha(token) and token not in row.token_hash
    # токена нет ни в одной текстовой колонке таблицы
    dump = db_session.execute(text("SELECT row_to_json(t)::text FROM auth_sessions t")).scalar()
    assert token not in dump


def test_wrong_password_and_unknown_email_are_indistinguishable(client):
    signup(client)
    client.cookies.clear()
    wrong = login(client, password="wrong password!")
    unknown = login(client, email="nobody@example.com")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert wrong.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert "set-cookie" not in wrong.headers


def test_google_only_account_cannot_password_login(client, db_session):
    signup(client)
    client.cookies.clear()
    u = db_session.execute(select(User)).scalar_one()
    u.password_hash = None
    db_session.commit()
    assert login(client).status_code == 401


def test_new_token_on_every_login(client):
    signup(client)
    t1 = client.cookies.get("mezon_session")
    client.cookies.clear()
    login(client)
    t2 = client.cookies.get("mezon_session")
    assert t1 and t2 and t1 != t2


def test_revoked_session_is_401(client, db_session):
    signup(client)
    db_session.execute(text("UPDATE auth_sessions SET revoked_at = now()"))
    db_session.commit()
    assert client.get("/api/auth/me").status_code == 401


def test_expired_session_is_401(client, db_session):
    signup(client)
    assert client.get("/api/auth/me").status_code == 200
    db_session.execute(text("UPDATE auth_sessions SET expires_at = now() - interval '1 second'"))
    db_session.commit()
    assert client.get("/api/auth/me").status_code == 401


def test_logout_revokes_on_server(client, db_session):
    signup(client)
    token = client.cookies.get("mezon_session")
    r = client.post("/api/auth/logout", json={}, headers=H)
    assert r.status_code == 204
    assert 'mezon_session=""' in r.headers["set-cookie"] or "Max-Age=0" in r.headers["set-cookie"]
    assert db_session.execute(select(AuthSession.revoked_at)).scalar_one() is not None
    client.cookies.set("mezon_session", token)  # украденный cookie уже не работает
    assert client.get("/api/auth/me").status_code == 401


def test_rehash_on_login(client, db_session):
    signup(client)
    client.cookies.clear()
    weak = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1).hash(PASSWORD)
    u = db_session.execute(select(User)).scalar_one()
    u.password_hash = weak
    db_session.commit()
    assert login(client).status_code == 200
    db_session.refresh(u)
    assert u.password_hash != weak and u.password_hash.startswith("$argon2id$")


# --------------------------------------------------------------------------- cookie flags


def _flags(resp) -> dict:
    raw = resp.headers["set-cookie"]
    parts = [p.strip() for p in raw.split(";")]
    return {"raw": raw.lower(), "parts": [p.lower() for p in parts]}


def test_cookie_flags_secure_on(app_factory):
    _, c = app_factory(COOKIE_SECURE=True)
    f = _flags(signup(c))
    assert f["parts"][0].startswith("mezon_session=")
    for flag in ("httponly", "secure", "samesite=lax", "path=/", f"max-age={30 * 86400}"):
        assert flag in f["parts"], f


def test_cookie_secure_off_for_local(client):
    f = _flags(signup(client))
    assert "secure" not in f["parts"] and "httponly" in f["parts"] and "samesite=lax" in f["parts"]


def test_session_ttl_setting(app_factory, db_session):
    _, c = app_factory(SESSION_TTL_DAYS=7)
    assert "max-age=604800" in _flags(signup(c))["raw"]


# --------------------------------------------------------------------------- rate limits


def test_login_fails_limit_per_email_then_429(client):
    signup(client)
    client.cookies.clear()
    for _ in range(5):
        assert login(client, password="wrong password!").status_code == 401
    r = login(client, password="wrong password!")
    assert r.status_code == 429 and r.json()["error"]["code"] == "RATE_LIMITED"
    assert int(r.headers["retry-after"]) > 0
    # даже верный пароль не пускает, пока окно не истекло
    assert login(client).status_code == 429
    # другой email не затронут
    assert login(client, email="other@example.com").status_code == 401


def test_nonexistent_email_is_limited_too(client):
    for _ in range(5):
        assert login(client, email="ghost@example.com").status_code == 401
    assert login(client, email="ghost@example.com").status_code == 429


def test_successful_login_resets_failures(client):
    signup(client)
    client.cookies.clear()
    for _ in range(4):
        login(client, password="wrong password!")
    assert login(client).status_code == 200
    client.cookies.clear()
    for _ in range(4):
        assert login(client, password="wrong password!").status_code == 401


def test_ip_limit_and_proxy_header_ignored_by_default(app_factory):
    _, c = app_factory(AUTH_IP_MAX_REQUESTS=3, AUTH_LOGIN_MAX_FAILS=100)
    for i in range(3):
        r = c.post("/api/auth/login", json={"email": f"u{i}@example.com", "password": "x"},
                   headers={**H, "X-Forwarded-For": f"10.0.0.{i}"})
        assert r.status_code == 401
    r = c.post("/api/auth/login", json={"email": "u9@example.com", "password": "x"},
               headers={**H, "X-Forwarded-For": "10.9.9.9"})
    assert r.status_code == 429 and "retry-after" in r.headers


def test_ip_limit_uses_proxy_header_when_trusted(app_factory):
    _, c = app_factory(AUTH_IP_MAX_REQUESTS=2, AUTH_LOGIN_MAX_FAILS=100, TRUST_PROXY_HEADERS=True)
    for i in range(4):
        r = c.post("/api/auth/login", json={"email": "u@example.com", "password": "x"},
                   headers={**H, "X-Forwarded-For": f"203.0.113.{i}"})
        assert r.status_code == 401
    for _ in range(2):
        c.post("/api/auth/login", json={"email": "u@example.com", "password": "x"},
               headers={**H, "X-Forwarded-For": "198.51.100.7"})
    r = c.post("/api/auth/login", json={"email": "u@example.com", "password": "x"},
               headers={**H, "X-Forwarded-For": "198.51.100.7"})
    assert r.status_code == 429


# --------------------------------------------------------------------------- CSRF


@pytest.mark.parametrize("path", ["/api/auth/login", "/api/auth/signup", "/api/auth/logout"])
def test_auth_posts_require_origin(client, path):
    body = {"email": "a@example.com", "password": PASSWORD, "display_name": "A"}
    for headers in ({}, {"Origin": "https://evil.example"}, {"Origin": "null"}, {"Referer": "https://evil.example/x"}):
        r = client.post(path, json=body, headers=headers)
        assert r.status_code == 403 and r.json()["error"]["code"] == "CSRF_FAILED", (path, headers)


def test_origin_ok_and_referer_fallback(client):
    assert signup(client).status_code == 201
    r = client.post("/api/auth/logout", json={}, headers={"Referer": ORIGIN + "/uz/login"})
    assert r.status_code == 204


def test_csrf_on_regular_posts_only_with_cookie(client, make_guest):
    guest = make_guest()
    # аноним без cookie работает как раньше, без Origin
    r = client.post("/api/sessions", json={"user_id": guest, "scenario_id": "nope"})
    assert r.status_code != 403
    signup(client)  # теперь cookie есть
    r = client.post("/api/sessions", json={"user_id": guest, "scenario_id": "nope"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "CSRF_FAILED"
    r = client.post("/api/sessions", json={"user_id": guest, "scenario_id": "nope"}, headers={"Origin": "https://evil.example"})
    assert r.status_code == 403
    r = client.post("/api/sessions", json={"user_id": guest, "scenario_id": "nope"}, headers=H)
    assert r.status_code == 404  # прошло CSRF, сценария нет


def test_csrf_not_applied_to_get(client):
    signup(client)
    assert client.get("/api/auth/me").status_code == 200


def test_mentor_sse_post_checked_with_cookie(client):
    signup(client)
    r = client.post("/api/mentor/ask", json={"question": "hi"})
    assert r.status_code == 403 and r.json()["error"]["code"] == "CSRF_FAILED"
