"""Аккаунты: /api/auth/*. Контракт фронта описан в frontend/AUTH.md."""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth import accounts, ratelimit, sessions
from app.auth.deps import get_current_user
from app.auth.google import GoogleError, GoogleOAuth, get_google, pkce_challenge
from app.auth.merge import merge_guest
from app.auth.passwords import hash_password, verify_password
from app.auth.redirects import safe_next
from app.auth.sessions import hash_token
from app.config import Settings, get_settings
from app.db import get_db
from app.errors import AuthProviderDisabledError, EmailExistsError, InvalidCredentialsError
from app.history import get_history
from app.history.store import HistoryStore, safely
from app.models.app_tables import User
from app.models.auth import OAuthState
from app.schemas.auth import AccountUser, LoginIn, SignupIn
from app.services.clock import get_now

router = APIRouter(prefix="/auth", tags=["auth"])
log = logging.getLogger("adolat.auth")

OAUTH_TTL = timedelta(minutes=10)
BIND_COOKIE = "mezon_oauth"
BIND_PATH = "/api/auth/google"
NO_STORE = {"Cache-Control": "no-store"}


def _ua(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _open_session(
    db: Session,
    user: User,
    guest_id: uuid.UUID | None,
    request: Request,
    settings: Settings,
    now: datetime,
    history: HistoryStore,
) -> str:
    """Слить гостя, создать сессию, закоммитить одной транзакцией. Возвращает токен для cookie."""
    merged = merge_guest(db, guest_id, user.id, now)
    token = sessions.create_session(db, user.id, now, settings, _ua(request), ratelimit.client_ip(request, settings))
    db.commit()
    if merged and guest_id is not None:
        safely(history.reassign_user, str(guest_id), str(user.id))  # Mongo, best-effort
    return token


# --------------------------------------------------------------------------- email + password


@router.post("/signup", response_model=AccountUser, status_code=201)
def signup(
    body: SignupIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
):
    """Регистрация по email и паролю. 409, если email занят (так требует контракт фронта)."""
    ip = ratelimit.client_ip(request, settings)
    ratelimit.check(db, settings, now, ip, None)
    ratelimit.record_request(db, ip, now)
    if accounts.find_by_email(db, body.email) is not None:
        raise EmailExistsError()
    user = accounts.create_email_user(db, body.display_name, body.email, hash_password(body.password), now)
    if user is None:
        raise EmailExistsError()
    token = _open_session(db, user, body.guest_user_id, request, settings, now, history)
    sessions.set_cookie(response, token, settings)
    response.headers.update(NO_STORE)
    return accounts.account_out(user)


@router.post("/login", response_model=AccountUser)
def login(
    body: LoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
):
    """Вход. Любая неудача: 401 INVALID_CREDENTIALS, одинаковый ответ и время (проверяется фиктивный хэш)."""
    ip = ratelimit.client_ip(request, settings)
    email_h = ratelimit.email_hash(body.email)
    ratelimit.check(db, settings, now, ip, email_h)
    ratelimit.record_request(db, ip, now)

    user = accounts.find_by_email(db, body.email)
    ok, new_hash = verify_password(user.password_hash if user else None, body.password)
    if user is None or not ok:
        ratelimit.record_failure(db, email_h, ip, now)
        raise InvalidCredentialsError()

    if new_hash:
        user.password_hash = new_hash
    ratelimit.clear_failures(db, email_h)
    token = _open_session(db, user, body.guest_user_id, request, settings, now, history)
    sessions.set_cookie(response, token, settings)
    response.headers.update(NO_STORE)
    return accounts.account_out(user)


@router.post("/logout", status_code=204)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    now: datetime = Depends(get_now),
) -> Response:
    """Отзывает сессию на сервере и удаляет cookie."""
    sessions.revoke_token(db, request.cookies.get(sessions.COOKIE_NAME), now)
    resp = Response(status_code=204, headers=NO_STORE)
    sessions.clear_cookie(resp, settings)
    return resp


@router.get("/me", response_model=AccountUser)
def me(response: Response, user: User = Depends(get_current_user)):
    response.headers.update(NO_STORE)
    return accounts.account_out(user)


# --------------------------------------------------------------------------- Google


def _base(settings: Settings) -> str:
    return (settings.PUBLIC_BASE_URL or "").rstrip("/")


def _clear_bind(resp: Response, settings: Settings) -> None:
    resp.delete_cookie(BIND_COOKIE, path=BIND_PATH, httponly=True, secure=settings.COOKIE_SECURE, samesite="lax")


def _fail(settings: Settings, reason: str) -> RedirectResponse:
    log.warning("google sign-in failed: %s", reason)
    resp = RedirectResponse(_base(settings) + "/?auth_error=google", status_code=302, headers=NO_STORE)
    _clear_bind(resp, settings)
    return resp


@router.get("/google/start")
def google_start(
    request: Request,
    next: str | None = Query(None),
    guest_user_id: str | None = Query(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    now: datetime = Depends(get_now),
    google: GoogleOAuth = Depends(get_google),
):
    """302 на Google. state, PKCE-verifier, nonce, next и guest_user_id остаются на сервере."""
    if not settings.google_configured:
        raise AuthProviderDisabledError("Вход через Google не настроен")
    ip = ratelimit.client_ip(request, settings)
    ratelimit.check(db, settings, now, ip, None)
    ratelimit.record_request(db, ip, now)

    try:
        guest = uuid.UUID(guest_user_id) if guest_user_id else None
    except ValueError:
        guest = None
    state, nonce, bind = (secrets.token_urlsafe(32) for _ in range(3))
    verifier = secrets.token_urlsafe(64)  # 86 символов, допустимо для PKCE (43..128)
    db.execute(delete(OAuthState).where(OAuthState.expires_at < now))
    db.add(
        OAuthState(
            id=uuid.uuid4(),
            state_hash=hash_token(state),
            bind_hash=hash_token(bind),
            code_verifier=verifier,
            nonce=nonce,
            next_path=safe_next(next),
            guest_user_id=guest,
            created_at=now,
            expires_at=now + OAUTH_TTL,
        )
    )
    db.commit()

    resp = RedirectResponse(
        google.authorization_url(state, nonce, pkce_challenge(verifier)), status_code=302, headers=NO_STORE
    )
    # привязка state к браузеру: защита от подсовывания чужого callback (login CSRF)
    resp.set_cookie(
        BIND_COOKIE, bind, max_age=int(OAUTH_TTL.total_seconds()), path=BIND_PATH,
        httponly=True, secure=settings.COOKIE_SECURE, samesite="lax",
    )
    return resp


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str | None = Query(None, max_length=2048),
    state: str | None = Query(None, max_length=256),
    error: str | None = Query(None, max_length=256),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    now: datetime = Depends(get_now),
    google: GoogleOAuth = Depends(get_google),
    history: HistoryStore = Depends(get_history),
):
    if not settings.google_configured:
        raise AuthProviderDisabledError("Вход через Google не настроен")
    if not state:
        return _fail(settings, "no state")
    # одноразовость: строка удаляется и коммитится до любых других проверок
    row = db.execute(
        delete(OAuthState)
        .where(OAuthState.state_hash == hash_token(state))
        .returning(
            OAuthState.bind_hash, OAuthState.code_verifier, OAuthState.nonce, OAuthState.next_path,
            OAuthState.guest_user_id, OAuthState.expires_at,
        )
    ).first()
    db.commit()
    if row is None:
        return _fail(settings, "unknown or reused state")
    bind_hash, verifier, nonce, next_path, guest_id, expires_at = row
    bind = request.cookies.get(BIND_COOKIE)
    if expires_at <= now:
        return _fail(settings, "state expired")
    if not bind or not secrets.compare_digest(hash_token(bind), bind_hash):
        return _fail(settings, "state not bound to this browser")
    if error or not code:
        return _fail(settings, f"provider error: {error or 'no code'}"[:80])

    try:
        profile = google.verify_id_token(google.exchange_code(code, verifier), nonce)
        user = accounts.upsert_google_user(db, profile, now)
        token = _open_session(db, user, guest_id, request, settings, now, history)
    except (GoogleError, accounts.GoogleLinkError) as exc:
        db.rollback()
        return _fail(settings, str(exc))

    resp = RedirectResponse(_base(settings) + safe_next(next_path), status_code=302, headers=NO_STORE)
    sessions.set_cookie(resp, token, settings)
    _clear_bind(resp, settings)
    return resp
