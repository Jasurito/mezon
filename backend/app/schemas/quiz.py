"""Pre/post quiz schema for a scenario."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class QuizOption(_Model):
    id: str
    text_key: str


class Question(_Model):
    question_id: str
    text_key: str
    options: list[QuizOption]
    correct_option: str
    explanation_key: str
    citation_ids: list[str] = []


class Quiz(_Model):
    scenario_id: str
    pre: list[Question]
    post: list[Question]
