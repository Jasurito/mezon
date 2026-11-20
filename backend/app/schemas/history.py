"""Хроника дела и лента активности."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel

from app.schemas.api import GameEvent
from app.schemas.legal import Locale


class HistoryStepOut(BaseModel):
    seq: int
    ts: datetime
    action_id: str | None
    params: dict[str, Any] | None
    stage_before: str | None
    stage_after: str
    score_after: int
    events: list[GameEvent]


class SessionHistoryOut(BaseModel):
    session_id: uuid.UUID
    user_id: uuid.UUID
    scenario_id: str
    scenario_version: str
    locale: Locale
    started_at: datetime
    finished_at: datetime | None
    outcome: str | None
    outcome_title: str | None
    score: int | None
    max_score: int | None
    steps: list[HistoryStepOut]
    source: Literal["mongo", "postgres"]


class ActivityItem(BaseModel):
    type: str
    ts: datetime
    session_id: uuid.UUID | None
    payload: dict[str, Any]


class ActivityOut(BaseModel):
    items: list[ActivityItem]
    next_before: datetime | None
    available: bool
