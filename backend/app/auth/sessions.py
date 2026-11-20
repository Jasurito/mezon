"""Серверные сессии: в cookie случайный токен, в базе только его SHA-256."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

from fastapi import Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.app_tables import User
from app.models.auth import AuthSession

COOKIE_NAME = "mezon_session"
_TOUCH_EVERY = timedelta(minutes=5)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(
    db: Session, user_id: uuid.UUID, now: datetime, settings: Settings, user_agent: str | None, ip: str | None
) -> str:
    """Новая сессия (новый токен при каждом входе). Возвращает сырой токен, в базу он не попадает."""
    token = secrets.token_urlsafe(32)
    db.add(
        AuthSession(
            id=uuid.uuid4(),
            user_id=user_id,
            token_hash=hash_token(token),
            created_at=now,
            expires_at=now + timedelta(days=settings.SESSION_TTL_DAYS),
            last_seen_at=now,
            user_agent=(user_agent or "")[:255] or None,
            ip=(ip or "")[:64] or None,
        )
    )
    return token


def resolve(db: Session, token: str | None, now: datetime) -> tuple[AuthSession, User] | None:
    """Активная сессия по токену или None (нет, отозвана, истекла)."""
    if not token or len(token) > 256:
        return None
    row = db.execute(
        select(AuthSession, User)
        .join(User, User.id == AuthSession.user_id)
        .where(AuthSession.token_hash == hash_token(token))
    ).first()
    if row is None:
        return None
    sess, user = row
    if sess.revoked_at is not None or sess.expires_at <= now:
        return None
    if now - sess.last_seen_at > _TOUCH_EVERY:
        sess.last_seen_at = now
        db.commit()
    return sess, user


def revoke_token(db: Session, token: str | None, now: datetime) -> None:
    if not token or len(token) > 256:
        return
    db.execute(
        update(AuthSession)
        .where(AuthSession.token_hash == hash_token(token), AuthSession.revoked_at.is_(None))
        .values(revoked_at=now)
    )
    db.commit()


def revoke_all(db: Session, user_id: uuid.UUID, now: datetime) -> None:
    db.execute(
        update(AuthSession).where(AuthSession.user_id == user_id, AuthSession.revoked_at.is_(None)).values(revoked_at=now)
    )


def set_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=settings.SESSION_TTL_DAYS * 86400,
        path="/",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


def clear_cookie(response: Response, settings: Settings) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, secure=settings.COOKIE_SECURE, samesite="lax")
