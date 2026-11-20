"""Модели запросов и ответов игрового API (docs/BACKEND.md §4, §5.2, §5.3, §5.5)."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.legal import CitationView, LegalActView, Locale
from app.schemas.scenario import ActionKind, Reaction

# --------------------------------------------------------------------------- запросы


class CreateUser(BaseModel):
    display_name: str | None = Field(None, max_length=200, examples=["Азиз"])


class CreateSession(BaseModel):
    user_id: uuid.UUID
    scenario_id: str = Field(examples=["consumer_dispute_001"])
    locale: Locale = "ru"


class PatchSession(BaseModel):
    locale: Locale


class ActionParams(BaseModel):
    option: str | None = Field(None, description="Выбранный вариант (только для kind=decision)")


class ActionRequest(BaseModel):
    action_id: str = Field(examples=["present_receipt"])
    params: ActionParams | None = None


# --------------------------------------------------------------------------- пользователи


class UserOut(BaseModel):
    user_id: uuid.UUID
    display_name: str | None
    created_at: datetime


# --------------------------------------------------------------------------- состояние игры


class OptionView(BaseModel):
    id: str
    label: str


class ActionView(BaseModel):
    """Кнопка, которую фронт может показать."""

    action_id: str
    kind: ActionKind
    label: str
    target_character: str | None = None
    evidence_id: str | None = None
    options: list[OptionView] | None = None
    hint_citation_ids: list[str] = []

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "action_id": "present_receipt",
                "kind": "evidence",
                "label": "Представить кассовый чек",
                "target_character": "judge",
                "evidence_id": "receipt",
                "options": None,
                "hint_citation_ids": ["CPC.art.Z"],
            }
        }
    )


class SayEvent(BaseModel):
    type: Literal["say"] = "say"
    speaker: str
    text: str
    emotion: str = "neutral"


class ReactEvent(BaseModel):
    type: Literal["react"] = "react"
    character: str
    reaction: Reaction


class StageChangedEvent(BaseModel):
    type: Literal["stage_changed"] = "stage_changed"
    stage: str
    title: str


class EvidenceAddedEvent(BaseModel):
    type: Literal["evidence_added"] = "evidence_added"
    evidence_id: str


class ScoreEvent(BaseModel):
    type: Literal["score"] = "score"
    delta: int
    total: int


class LegalNoteEvent(BaseModel):
    type: Literal["legal_note"] = "legal_note"
    citation_id: str
    text: str


class MistakeEvent(BaseModel):
    type: Literal["mistake"] = "mistake"
    category: str
    text: str


GameEvent = Annotated[
    SayEvent
    | ReactEvent
    | StageChangedEvent
    | EvidenceAddedEvent
    | ScoreEvent
    | LegalNoteEvent
    | MistakeEvent,
    Field(discriminator="type"),
]


class EvidenceView(BaseModel):
    id: str
    title: str
    type: Literal["document", "object", "testimony"]
    reviewed: bool = False
    presented: bool = False


class GameState(BaseModel):
    session_id: uuid.UUID
    scenario_id: str
    locale: Locale
    stage: str
    stage_title: str
    stage_index: int = Field(description="Номер этапа с 1")
    stage_count: int
    score: int
    max_score: int
    evidence: list[EvidenceView]
    available_actions: list[ActionView]
    events: list[GameEvent] = Field(description="События последнего действия")
    finished: bool
    legal_date: date


# --------------------------------------------------------------------------- сценарии


class ScenarioCard(BaseModel):
    scenario_id: str
    title: str
    category: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    minutes: int
    topics: list[str]
    cover: str | None
    fictional_notice: str
    available: bool

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scenario_id": "consumer_dispute_001",
                "title": "Неисправный смартфон",
                "category": "Защита прав потребителей",
                "difficulty": "beginner",
                "minutes": 15,
                "topics": ["Качество товара", "Доказательства"],
                "cover": "/game/covers/consumer_dispute_001.png",
                "fictional_notice": "Учебная ситуация, не реальное дело",
                "available": True,
            }
        }
    )


class PlayerRoleView(BaseModel):
    character_id: str
    title: str


class CharacterView(BaseModel):
    id: str
    name: str
    role: str
    sprite: str


class ClaimView(BaseModel):
    side: Literal["plaintiff", "defendant"]
    text: str


class DocumentView(BaseModel):
    id: str
    title: str


class ScenarioDetail(BaseModel):
    scenario_id: str
    title: str
    fictional_notice: str
    legal_date: date
    story: str
    player_role: PlayerRoleView
    characters: list[CharacterView]
    claims: list[ClaimView]
    documents: list[DocumentView]
    legal_acts: list[LegalActView]


# --------------------------------------------------------------------------- результат


class DecisionView(BaseModel):
    decision_id: str
    stage: str
    chosen: str | None
    chosen_label: str
    best: str
    best_label: str
    correct: bool
    explanation: str
    citation_ids: list[str]


class MistakeView(BaseModel):
    category: str
    title: str
    explanation: str
    correct_action: str | None
    citation_ids: list[str]


class RecommendationView(BaseModel):
    topic: str
    citation_ids: list[str]
    scenario_id: str | None


class SessionResult(BaseModel):
    session_id: uuid.UUID
    scenario_id: str
    outcome: str
    outcome_title: str
    ruling_text: str
    score: int
    max_score: int
    correct_decision_rate: float
    time_spent_sec: int
    decisions: list[DecisionView]
    mistakes: list[MistakeView]
    citations: list[CitationView]
    recommendations: list[RecommendationView]
    disclaimer: str
