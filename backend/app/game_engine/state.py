"""Engine data types: state, events, available actions, outcome. All JSON-serializable."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.scenario import ActionKind, Mistake, Reaction, Recommendation


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True)


class EngineState(_Frozen):
    """Immutable game state. ``evidence`` lists only evidence added by effects."""

    stage: str
    flags: tuple[str, ...] = ()  # sorted
    score: int = 0
    evidence: tuple[str, ...] = ()
    performed: tuple[str, ...] = ()
    choices: dict[str, str] = Field(default_factory=dict)
    mistakes: tuple[Mistake, ...] = ()
    finished: bool = False
    outcome: str | None = None
    step: int = 0
    visited: tuple[str, ...] = ()  # stages entered, in order


class SayEvent(_Frozen):
    type: Literal["say"] = "say"
    speaker: str
    text_key: str
    emotion: str = "neutral"


class ReactEvent(_Frozen):
    type: Literal["react"] = "react"
    character: str
    reaction: Reaction


class StageChangedEvent(_Frozen):
    type: Literal["stage_changed"] = "stage_changed"
    stage: str
    title_key: str


class EvidenceAddedEvent(_Frozen):
    type: Literal["evidence_added"] = "evidence_added"
    evidence_id: str


class ScoreEvent(_Frozen):
    type: Literal["score"] = "score"
    delta: int
    total: int


class LegalNoteEvent(_Frozen):
    type: Literal["legal_note"] = "legal_note"
    citation_id: str
    text_key: str


class MistakeEvent(_Frozen):
    type: Literal["mistake"] = "mistake"
    category: str
    title_key: str


Event = Annotated[
    SayEvent
    | ReactEvent
    | StageChangedEvent
    | EvidenceAddedEvent
    | ScoreEvent
    | LegalNoteEvent
    | MistakeEvent,
    Field(discriminator="type"),
]


class OptionView(_Frozen):
    id: str
    label_key: str


class AvailableAction(_Frozen):
    id: str
    kind: ActionKind
    label_key: str
    target_character: str | None = None
    evidence_id: str | None = None
    decision_id: str | None = None
    hint_citation_ids: tuple[str, ...] = ()
    options: tuple[OptionView, ...] | None = None  # only for kind="decision"


class LoggedAction(BaseModel):
    action_id: str
    params: dict | None = None


class DecisionResult(_Frozen):
    decision_id: str
    stage: str
    chosen: str | None
    best: str
    correct: bool
    explanation_key: str
    citation_ids: tuple[str, ...] = ()
    kind: str = "action"
    counterfactual_key: str | None = None


class Outcome(_Frozen):
    outcome: str
    result_kind: str = "loss"
    title_key: str
    ruling_key: str
    score: int
    max_score: int
    decisions: tuple[DecisionResult, ...]
    correct_decision_rate: float
    mistakes: tuple[Mistake, ...]
    citation_ids: tuple[str, ...]
    recommendations: tuple[Recommendation, ...]
