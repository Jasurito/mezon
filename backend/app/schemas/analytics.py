"""Модели запросов и ответов учебной аналитики (docs/BACKEND.md §5.2, §5.4, §5.9)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

QuizKind = Literal["pre", "post"]


# --- квиз -------------------------------------------------------------------


class QuizOptionOut(BaseModel):
    id: str
    text: str


class QuizQuestionOut(BaseModel):
    question_id: str
    text: str
    options: list[QuizOptionOut]


class QuizOut(BaseModel):
    scenario_id: str
    kind: QuizKind
    questions: list[QuizQuestionOut]
    total: int


class QuizAttemptIn(BaseModel):
    user_id: uuid.UUID
    kind: QuizKind
    answers: dict[str, str]


class QuizReviewItem(BaseModel):
    question_id: str
    chosen_option: str | None
    correct: bool
    correct_option: str
    explanation: str
    citation_ids: list[str]


class LearningGainOut(BaseModel):
    pre: int
    post: int
    max: int
    delta: int
    note: str


class QuizAttemptOut(BaseModel):
    attempt_id: int
    score: int
    max: int
    review: list[QuizReviewItem]
    learning_gain: LearningGainOut | None


# --- дашборд ----------------------------------------------------------------


class DashboardUser(BaseModel):
    user_id: uuid.UUID
    display_name: str | None


class KnowledgeLevel(BaseModel):
    score: int | None
    label: str


class CompletedSession(BaseModel):
    session_id: uuid.UUID
    scenario_id: str
    title: str
    outcome: str | None
    outcome_title: str
    score: int
    max_score: int
    finished_at: datetime


class DashboardLearningGain(BaseModel):
    scenario_id: str
    pre: int | None
    post: int | None
    max: int
    note: str


class MistakeCategoryOut(BaseModel):
    category: str
    title: str
    count: int


class RecommendedScenario(BaseModel):
    scenario_id: str
    title: str
    category: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    minutes: int
    topics: list[str]
    available: bool
    reason: str


class FocusTopic(BaseModel):
    category: str
    topic: str
    citation_ids: list[str]
    scenario_id: str | None


class DashboardOut(BaseModel):
    user: DashboardUser
    knowledge_level: KnowledgeLevel
    completed: list[CompletedSession]
    learning_gain: list[DashboardLearningGain]
    mistake_categories: list[MistakeCategoryOut]
    recommended: list[RecommendedScenario]
    focus_topics: list[FocusTopic]


# --- события и сводка ---------------------------------------------------------


class ClientEvent(BaseModel):
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    ts: datetime | None = None


class EventsIn(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID | None = None
    events: list[ClientEvent] = Field(max_length=50)


class EventsOut(BaseModel):
    accepted: int
    rejected: int


class ScenarioSummary(BaseModel):
    sessions_started: int
    completion_rate: float | None
    avg_score: int | None
    correct_decision_rate: float | None
    avg_time_sec: int | None
    avg_learning_gain: float | None
    mistakes_by_category: dict[str, int]
    note: str
