"""Перенос гостевого прогресса на аккаунт (Postgres, без коммита: вызывающий коммитит вместе со входом)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.app_tables import Event, GameSession, QuizAttempt, User, UserStats


def _stats_row(db: Session, user_id: uuid.UUID) -> UserStats:
    row = db.get(UserStats, user_id)
    if row is None:
        row = UserStats(
            user_id=user_id,
            sessions_started=0,
            sessions_finished=0,
            total_score=0,
            best_score=0,
            total_time_sec=0,
            quizzes_taken=0,
            active_days=0,
            streak_days=0,
        )
        db.add(row)
        db.flush()
    return row


def merge_guest(db: Session, guest_id: uuid.UUID | None, account_id: uuid.UUID, now: datetime) -> bool:
    """Перенести данные гостя на аккаунт. Молча ничего не делает, если guest_id не подходит.

    Подходит только существующий гость: нет email и google_sub, не слит ранее, не сам аккаунт.
    """
    if guest_id is None or guest_id == account_id:
        return False
    guest = db.execute(select(User).where(User.id == guest_id).with_for_update()).scalar_one_or_none()
    if (
        guest is None
        or guest.email is not None
        or guest.google_sub is not None
        or guest.password_hash is not None
        or guest.merged_into is not None
    ):
        return False

    for model in (GameSession, QuizAttempt, Event):
        db.execute(update(model).where(model.user_id == guest_id).values(user_id=account_id))

    g = db.get(UserStats, guest_id)
    if g is not None:
        a = _stats_row(db, account_id)
        a.sessions_started += g.sessions_started
        a.sessions_finished += g.sessions_finished
        a.total_score += g.total_score
        a.best_score = max(a.best_score, g.best_score)
        a.total_time_sec += g.total_time_sec
        a.quizzes_taken += g.quizzes_taken
        a.active_days += g.active_days
        a.streak_days = max(a.streak_days, g.streak_days)
        if g.last_active_at is not None and (a.last_active_at is None or g.last_active_at > a.last_active_at):
            a.last_active_at = g.last_active_at
        a.updated_at = now
        db.delete(g)

    guest.merged_into = account_id
    db.flush()
    return True
