"""Зависимости авторизации: текущий пользователь и проверка владельца user_id / session_id."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.auth import sessions
from app.db import get_db
from app.errors import ForbiddenError, UnauthorizedError
from app.models.app_tables import GameSession, User
from app.services.clock import get_now


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
) -> User | None:
    found = sessions.resolve(db, request.cookies.get(sessions.COOKIE_NAME), now)
    return found[1] if found else None


def get_current_user(user: User | None = Depends(get_optional_user)) -> User:
    if user is None:
        raise UnauthorizedError()
    return user


class Viewer:
    """Кто делает запрос. Гостевые user_id открыты (анонимный режим), аккаунты требуют свою сессию."""

    def __init__(self, db: Session, user: User | None) -> None:
        self.db = db
        self.user = user

    def require_user(self, user_id: uuid.UUID) -> None:
        owner = self.db.get(User, user_id)
        if owner is None or not owner.is_account:
            return  # нет такого или гость: дальше решит сам эндпоинт (404 или анонимный доступ)
        if self.user is None:
            raise UnauthorizedError()
        if self.user.id != owner.id:
            raise ForbiddenError()

    def require_session(self, session_id: uuid.UUID) -> None:
        owner_id = self.db.query(GameSession.user_id).filter(GameSession.id == session_id).scalar()
        if owner_id is not None:
            self.require_user(owner_id)


def get_viewer(db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)) -> Viewer:
    return Viewer(db, user)


def require_path_user(user_id: uuid.UUID, viewer: Viewer = Depends(get_viewer)) -> None:
    """Для маршрутов с {user_id} в пути: `dependencies=[Depends(require_path_user)]`."""
    viewer.require_user(user_id)


def require_path_session(session_id: uuid.UUID, viewer: Viewer = Depends(get_viewer)) -> None:
    """Для маршрутов с {session_id} в пути."""
    viewer.require_session(session_id)
