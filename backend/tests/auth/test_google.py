import json
import time
import uuid
from urllib.parse import parse_qs, urlsplit

import httpx
import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import select, text

from app.auth.google import ISSUERS, JWKS_URI, TOKEN_ENDPOINT, GoogleOAuth, get_google, pkce_challenge
from app.auth.redirects import safe_next
from app.config import Settings
from app.models.app_tables import GameSession, User
from app.models.auth import OAuthState
from tests.auth.conftest import (
    GOOGLE_ID,
    GOOGLE_SECRET,
    ORIGIN,
    PASSWORD,
    REDIRECT,
    add_session,
    login,
    sha,
    signup,
)

pytestmark = pytest.mark.db

KID = "test-kid-1"


def _keypair():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    return pem, key.public_key()


PRIVATE_PEM, PUBLIC = _keypair()
OTHER_PEM, _ = _keypair()
JWK = {**RSAAlgorithm.to_jwk(PUBLIC, as_dict=True), "kid": KID, "use": "sig", "alg": "RS256"}


class FakeGoogle:
    """httpx.MockTransport: token endpoint и JWKS. Запоминает запросы и выдаёт настраиваемый id_token."""

    def __init__(self):
        self.calls: list[tuple[str, dict]] = []
        self.token_status = 200
        self.claims: dict = {}
        self.pem = PRIVATE_PEM
        self.nonce: str | None = None  # nonce из start-редиректа
        self.settings = None

    def make_id_token(self):
        now = int(time.time())
        claims = {
            "iss": "https://accounts.google.com",
            "aud": GOOGLE_ID,
            "sub": "google-sub-1",
            "email": "g@example.com",
            "email_verified": True,
            "name": "Gia Google",
            "picture": "https://lh3.googleusercontent.com/a/pic",
            "nonce": self.nonce,
            "iat": now,
            "exp": now + 600,
        }
        claims.update(self.claims)
        claims = {k: v for k, v in claims.items() if v is not ...}
        return jwt.encode(claims, self.pem, algorithm="RS256", headers={"kid": KID})

    def handler(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if url == JWKS_URI:
            self.calls.append(("jwks", {}))
            return httpx.Response(200, json={"keys": [JWK]})
        if url == TOKEN_ENDPOINT:
            form = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
            self.calls.append(("token", form))
            if self.token_status != 200:
                return httpx.Response(self.token_status, json={"error": "invalid_grant"})
            return httpx.Response(200, json={"id_token": self.make_id_token(), "access_token": "at"})
        return httpx.Response(404)


@pytest.fixture
def fake():
    return FakeGoogle()


@pytest.fixture
def gapp(app_factory, fake):
    app, c = app_factory()
    cache: dict = {}
    settings = Settings(GOOGLE_CLIENT_ID=GOOGLE_ID, GOOGLE_CLIENT_SECRET=GOOGLE_SECRET, GOOGLE_REDIRECT_URI=REDIRECT)
    app.dependency_overrides[get_google] = lambda: GoogleOAuth(
        settings, lambda: httpx.Client(transport=httpx.MockTransport(fake.handler)), cache
    )
    return c


def start(c, fake, next="/uz/dashboard", guest=None):
    q = {"next": next}
    if guest:
        q["guest_user_id"] = guest
    r = c.get("/api/auth/google/start", params=q)
    assert r.status_code == 302, r.text
    loc = urlsplit(r.headers["location"])
    params = {k: v[0] for k, v in parse_qs(loc.query).items()}
    fake.nonce = params["nonce"]
    return r, loc, params


def callback(c, state, code="auth-code", **extra):
    return c.get("/api/auth/google/callback", params={"code": code, "state": state, **extra})


def assert_failed(r, c):
    assert r.status_code == 302 and r.headers["location"].endswith("/?auth_error=google"), r.headers.get("location")
    assert "mezon_session" not in r.headers.get("set-cookie", "")
    assert c.get("/api/auth/me").status_code == 401


# --------------------------------------------------------------------------- start


def test_start_builds_pkce_state_nonce_redirect(gapp, fake, db_session):
    r, loc, p = start(gapp, fake)
    assert f"{loc.scheme}://{loc.netloc}{loc.path}" == "https://accounts.google.com/o/oauth2/v2/auth"
    assert p["client_id"] == GOOGLE_ID and p["redirect_uri"] == REDIRECT
    assert p["response_type"] == "code" and p["scope"] == "openid email profile"
    assert p["code_challenge_method"] == "S256" and len(p["state"]) >= 32 and len(p["nonce"]) >= 32
    assert "client_secret" not in r.headers["location"] and "next" not in p and "guest" not in r.headers["location"]

    row = db_session.execute(select(OAuthState)).scalar_one()
    assert pkce_challenge(row.code_verifier) == p["code_challenge"]
    assert row.code_verifier not in r.headers["location"]
    assert row.nonce == p["nonce"] and row.next_path == "/uz/dashboard"
    # state и привязка к браузеру лежат хэшами, не открытым текстом
    assert row.state_hash == sha(p["state"]) and p["state"] not in (row.state_hash, row.bind_hash)
    ck = r.headers["set-cookie"].lower()
    assert "mezon_oauth=" in ck and "httponly" in ck and "samesite=lax" in ck
    assert 0 < (row.expires_at - row.created_at).total_seconds() <= 600


def test_start_disabled_without_config(app_factory):
    _, c = app_factory(GOOGLE_CLIENT_ID=None)
    r = c.get("/api/auth/google/start")
    assert r.status_code == 503 and r.json()["error"]["code"] == "AUTH_PROVIDER_DISABLED"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("//evil.com", "/"), ("https://evil.com", "/"), ("/\\evil.com", "/"), ("\\\\evil.com", "/"),
        ("/\t/evil.com", "/"), ("javascript:alert(1)", "/"), ("evil.com", "/"), ("", "/"), (None, "/"),
        ("/%0d%0aSet-Cookie:x", "/%0d%0aSet-Cookie:x"), ("/uz/dashboard?a=1", "/uz/dashboard?a=1"), ("/", "/"),
    ],
)
def test_safe_next(value, expected):
    assert safe_next(value) == expected


@pytest.mark.parametrize("bad", ["//evil.com", "https://evil.com", "/\\evil.com"])
def test_open_redirect_blocked_end_to_end(gapp, fake, db_session, bad):
    start(gapp, fake, next=bad)
    assert db_session.execute(select(OAuthState.next_path)).scalar_one() == "/"


# --------------------------------------------------------------------------- callback: success


def test_full_login_creates_account_and_redirects(gapp, fake, db_session):
    guest = gapp.post("/api/users", json={}).json()["user_id"]
    sid = add_session(db_session, guest, finished=True, score=4)
    _, _, p = start(gapp, fake, guest=guest)
    r = callback(gapp, p["state"])
    assert r.status_code == 302 and r.headers["location"] == ORIGIN + "/uz/dashboard"
    cookie = r.headers["set-cookie"].lower()
    assert "mezon_session=" in cookie and "httponly" in cookie

    me = gapp.get("/api/auth/me").json()
    assert me["provider"] == "google" and me["email"] == "g@example.com" and me["display_name"] == "Gia Google"
    assert me["avatar_url"].startswith("https://")

    kind, form = [c for c in fake.calls if c[0] == "token"][0]
    assert form["client_secret"] == GOOGLE_SECRET and form["redirect_uri"] == REDIRECT
    assert form["grant_type"] == "authorization_code" and form["code"] == "auth-code"
    assert pkce_challenge(form["code_verifier"]) == p["code_challenge"]

    s = db_session.get(GameSession, sid)
    db_session.refresh(s)
    assert str(s.user_id) == me["id"]  # гостевой прогресс перенесён
    u = db_session.get(User, uuid.UUID(me["id"]))
    assert u.google_sub == "google-sub-1" and u.email_verified and u.password_hash is None
    assert db_session.execute(select(OAuthState)).first() is None  # состояние израсходовано


def test_second_login_same_sub_reuses_account_and_caches_jwks(gapp, fake):
    _, _, p = start(gapp, fake)
    callback(gapp, p["state"])
    first = gapp.get("/api/auth/me").json()["id"]
    gapp.cookies.clear()
    _, _, p = start(gapp, fake)
    callback(gapp, p["state"])
    assert gapp.get("/api/auth/me").json()["id"] == first
    assert len([c for c in fake.calls if c[0] == "jwks"]) == 1


# --------------------------------------------------------------------------- callback: rejections


def test_unknown_state_rejected(gapp, fake):
    start(gapp, fake)
    assert_failed(callback(gapp, "forged-state"), gapp)


def test_missing_state_rejected(gapp, fake):
    start(gapp, fake)
    r = gapp.get("/api/auth/google/callback", params={"code": "x"})
    assert_failed(r, gapp)


def test_state_is_single_use(gapp, fake):
    _, _, p = start(gapp, fake)
    assert callback(gapp, p["state"]).headers["location"] == ORIGIN + "/uz/dashboard"
    saved = dict(gapp.cookies)
    gapp.cookies.clear()
    gapp.cookies.set("mezon_oauth", saved.get("mezon_oauth", "x"), path="/api/auth/google")
    assert_failed(callback(gapp, p["state"]), gapp)


def test_state_from_other_browser_rejected(gapp, fake):
    """Login CSRF: чужой callback без cookie привязки не принимается, и state сгорает."""
    _, _, p = start(gapp, fake)
    gapp.cookies.clear()
    assert_failed(callback(gapp, p["state"]), gapp)
    # и в «правильном» браузере он уже не сработает
    assert_failed(callback(gapp, p["state"]), gapp)


def test_expired_state_rejected(gapp, fake, db_session):
    _, _, p = start(gapp, fake)
    db_session.execute(text("UPDATE oauth_states SET expires_at = now() - interval '1 second'"))
    db_session.commit()
    assert_failed(callback(gapp, p["state"]), gapp)


def test_provider_error_rejected(gapp, fake):
    _, _, p = start(gapp, fake)
    r = gapp.get("/api/auth/google/callback", params={"error": "access_denied", "state": p["state"]})
    assert_failed(r, gapp)


def test_token_endpoint_failure_rejected(gapp, fake):
    fake.token_status = 400
    _, _, p = start(gapp, fake)
    assert_failed(callback(gapp, p["state"]), gapp)


NOW = int(time.time())


@pytest.mark.parametrize(
    "claims",
    [
        {"nonce": "attacker-nonce"},
        {"nonce": ...},
        {"aud": "someone-else.apps.googleusercontent.com"},
        {"exp": NOW - 3600, "iat": NOW - 7200},
        {"iss": "https://evil.example"},
        {"email_verified": False},
        {"email_verified": ...},
        {"sub": ...},
        {"email": ...},
    ],
    ids=["nonce", "no-nonce", "aud", "expired", "iss", "unverified", "no-verified-claim", "no-sub", "no-email"],
)
def test_bad_id_token_rejected(gapp, fake, db_session, claims):
    fake.claims = claims
    _, _, p = start(gapp, fake)
    assert_failed(callback(gapp, p["state"]), gapp)
    assert db_session.execute(select(User)).first() is None  # аккаунт не создан


def test_wrong_signature_rejected(gapp, fake):
    fake.pem = OTHER_PEM
    _, _, p = start(gapp, fake)
    assert_failed(callback(gapp, p["state"]), gapp)


def test_unsigned_and_hs256_tokens_rejected(gapp, fake):
    _, _, p = start(gapp, fake)
    now = int(time.time())
    claims = {"iss": ISSUERS[0], "aud": GOOGLE_ID, "sub": "s", "email": "g@example.com", "email_verified": True,
              "nonce": p["nonce"], "iat": now, "exp": now + 600}
    for tok in (
        jwt.encode(claims, None, algorithm="none", headers={"kid": KID}),
        jwt.encode(claims, "secret" * 8, algorithm="HS256", headers={"kid": KID}),
    ):
        fake.make_id_token = lambda t=tok: t
        gapp.cookies.clear()
        _, _, p = start(gapp, fake)
        assert_failed(callback(gapp, p["state"]), gapp)


# --------------------------------------------------------------------------- account takeover protection


def test_google_login_takes_over_unverified_password_account(gapp, fake, db_session):
    """Злоумышленник занял email жертвы по паролю; когда жертва входит через Google, пароль и сессии умирают."""
    signup(gapp, email="g@example.com", password="attacker password")
    attacker_token = gapp.cookies.get("mezon_session")
    victim_id = gapp.get("/api/auth/me").json()["id"]
    gapp.cookies.clear()

    _, _, p = start(gapp, fake)
    r = callback(gapp, p["state"])
    assert r.status_code == 302 and r.headers["location"].endswith("/uz/dashboard")
    assert gapp.get("/api/auth/me").json()["id"] == victim_id  # тот же аккаунт

    u = db_session.get(User, uuid.UUID(victim_id))
    db_session.refresh(u)
    assert u.password_hash is None and u.google_sub == "google-sub-1" and u.email_verified

    gapp.cookies.clear()
    gapp.cookies.set("mezon_session", attacker_token)
    assert gapp.get("/api/auth/me").status_code == 401  # старая сессия отозвана
    assert login(gapp, email="g@example.com", password="attacker password").status_code == 401


def test_email_of_other_google_identity_is_refused(gapp, fake, db_session):
    _, _, p = start(gapp, fake)
    callback(gapp, p["state"])
    gapp.cookies.clear()
    fake.claims = {"sub": "another-sub"}  # тот же email, другой Google-аккаунт
    _, _, p = start(gapp, fake)
    assert_failed(callback(gapp, p["state"]), gapp)


def test_password_signup_after_google_conflicts(gapp, fake):
    _, _, p = start(gapp, fake)
    callback(gapp, p["state"])
    gapp.cookies.clear()
    assert signup(gapp, email="g@example.com").status_code == 409
