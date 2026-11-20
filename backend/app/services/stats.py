"""Агрегаты игрока (user_stats). Обновляются в той же транзакции, что и основное действие."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models.app_tables import UserStats


def _row(db: Session, user_id: uuid.UUID) -> UserStats:
    db.execute(pg_insert(UserStats).values(user_id=user_id).on_conflict_do_nothing(index_elements=["user_id"]))
    row = db.execute(select(UserStats).where(UserStats.user_id == user_id).with_for_update()).scalar_one()
    db.refresh(row)  # значения по умолчанию из БД, а не из кэша сессии
    return row


def _touch(row: UserStats, now: datetime) -> None:
    """Активность: active_days и streak_days по UTC-датам."""
    today = now.astimezone(UTC).date()
    if row.last_active_at is None:
        row.active_days = 1
        row.streak_days = 1
        row.last_active_at = now
        return
    last = row.last_active_at.astimezone(UTC).date()
    if last == today or today < last:
        pass
    elif (today - last).days == 1:
        row.active_days += 1
        row.streak_days += 1
    else:
        row.active_days += 1
        row.streak_days = 1
    if now > row.last_active_at:
        row.last_active_at = now


def on_session_started(db: Session, user_id: uuid.UUID, now: datetime) -> None:
    row = _row(db, user_id)
    row.sessions_started += 1
    _touch(row, now)
    row.updated_at = now


def on_session_finished(db: Session, user_id: uuid.UUID, score: int, started_at: datetime, now: datetime) -> None:
    row = _row(db, user_id)
    row.sessions_finished += 1
    row.total_score += score
    row.best_score = max(row.best_score, score)
    row.total_time_sec += max(0, int((now - started_at).total_seconds()))
    _touch(row, now)
    row.updated_at = now


def on_quiz_attempt(db: Session, user_id: uuid.UUID, now: datetime) -> None:
    row = _row(db, user_id)
    row.quizzes_taken += 1
    _touch(row, now)
    row.updated_at = now
