"""Профиль, статистика и список игр пользователя."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.schemas.legal import Locale


class UserStatsOut(BaseModel):
    sessions_started: int = 0
    sessions_finished: int = 0
    total_score: int = 0
    best_score: int = 0
    total_time_sec: int = 0
    quizzes_taken: int = 0
    last_active_at: datetime | None = None
    active_days: int = 0
    streak_days: int = 0


class UserProfileOut(BaseModel):
    user_id: uuid.UUID
    display_name: str | None
    preferred_locale: Locale | None
    created_at: datetime
    stats: UserStatsOut


class PatchUser(BaseModel):
    display_name: str | None = None
    preferred_locale: Locale | None = None


class UserSessionItem(BaseModel):
    session_id: uuid.UUID
    scenario_id: str
    title: str | None
    started_at: datetime
    finished_at: datetime | None
    outcome: str | None
    outcome_title: str | None
    score: int | None
    max_score: int | None
    steps: int


class UserSessionsOut(BaseModel):
    items: list[UserSessionItem]
    total: int
    limit: int
    offset: int
