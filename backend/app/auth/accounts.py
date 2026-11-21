"""Работа с аккаунтами: поиск, создание, привязка Google."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import sessions
from app.auth.google import GoogleProfile
from app.models.app_tables import User
from app.schemas.auth import AccountUser


def account_out(user: User) -> AccountUser:
    """Только поля контракта фронта; пароль, хэши и google_sub наружу не идут."""
    email = user.email or ""
    return AccountUser(
        id=user.id,
        display_name=user.display_name or email.split("@")[0],
        email=email,
        provider="google" if user.google_sub else "email",
        avatar_url=user.avatar_url,
        audience=user.audience,  # type: ignore[arg-type]
    )


def find_by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def create_email_user(
    db: Session, display_name: str, email: str, password_hash: str, now: datetime, audience: str | None = None
) -> User | None:
    """None, если email занят (в том числе при гонке: ловим нарушение уникальности)."""
    user = User(id=uuid.uuid4(), display_name=display_name, email=email, email_verified=False,
                password_hash=password_hash, created_at=now, audience=audience)
    try:
        with db.begin_nested():
            db.add(user)
            db.flush()
    except IntegrityError:
        return None
    return user


class GoogleLinkError(Exception):
    pass


def upsert_google_user(db: Session, profile: GoogleProfile, now: datetime) -> User:
    """Найти или создать аккаунт по Google sub.

    Почта в пароле-регистрации не подтверждалась, поэтому при совпадении email с аккаунтом без google_sub
    аккаунт привязывается к Google, пароль стирается и все прежние сессии отзываются: так злоумышленник,
    заранее занявший чужой email, теряет доступ.
    """
    user = db.execute(select(User).where(User.google_sub == profile.sub)).scalar_one_or_none()
    if user is not None:
        if profile.picture and user.avatar_url != profile.picture:
            user.avatar_url = profile.picture
        return user

    user = find_by_email(db, profile.email)
    if user is not None:
        if user.google_sub is not None:
            raise GoogleLinkError("email belongs to another Google identity")
        user.google_sub = profile.sub
        user.email_verified = True
        user.password_hash = None
        if profile.picture:
            user.avatar_url = profile.picture
        sessions.revoke_all(db, user.id, now)
        db.flush()
        return user

    user = User(
        id=uuid.uuid4(),
        display_name=profile.name or profile.email.split("@")[0],
        email=profile.email,
        email_verified=True,
        google_sub=profile.sub,
        avatar_url=profile.picture,
        created_at=now,
    )
    try:
        with db.begin_nested():
            db.add(user)
            db.flush()
    except IntegrityError as exc:
        raise GoogleLinkError("concurrent account creation") from exc
    return user
