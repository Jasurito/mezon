"""Модели API свободных вопросов персонажам (docs/BACKEND.md §5.6)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NpcAskRequest(BaseModel):
    text: str = Field(min_length=1, max_length=500)


class NpcAnswer(BaseModel):
    speaker: str
    text: str
    question_id: str
    fact_ids: list[str]
    ai_generated: bool
    suggested_action_id: str | None = None


class NpcReply(BaseModel):
    """Структурированный ответ модели-перефразировщика."""

    text: str


class NpcClassification(BaseModel):
    """База ответа классификатора; у конкретного вызова поле ``question_id`` сужено до enum."""

    question_id: str
