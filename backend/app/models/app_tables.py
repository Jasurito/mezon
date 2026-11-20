import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    PrimaryKeyConstraint,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str | None] = mapped_column(Text)
    group_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    preferred_locale: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GameSession(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    scenario_id: Mapped[str] = mapped_column(Text)
    scenario_version: Mapped[str] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    outcome: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int | None] = mapped_column(Integer)


class SessionAction(Base):
    __tablename__ = "session_actions"
    __table_args__ = (PrimaryKeyConstraint("session_id", "seq"),)

    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sessions.id"))
    seq: Mapped[int] = mapped_column(Integer)
    action_id: Mapped[str] = mapped_column(Text)
    params: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_session_id", "session_id"),
        Index("ix_events_type", "type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    type: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (CheckConstraint("kind IN ('pre', 'post')", name="ck_quiz_attempts_kind"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    scenario_id: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text)
    answers: Mapped[Any] = mapped_column(JSONB)
    score: Mapped[int] = mapped_column(Integer)
    max_score: Mapped[int] = mapped_column(Integer)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    sessions_started: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    sessions_finished: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    best_score: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    total_time_sec: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    quizzes_taken: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    active_days: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    streak_days: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
