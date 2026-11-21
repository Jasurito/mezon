"""Scenario schema (Pydantic v2): the game FSM as data.

Conditions and effects are JSON DSLs where an object holds exactly one key.
Python field names that clash with builtins/keywords use aliases (``not``, ``all``...).
"""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Reaction = Literal["nod", "object", "surprised", "think", "gavel"]
ActionKind = Literal[
    "question", "evidence", "motion", "objection", "argument", "decision", "continue"
]
ResultKind = Literal["win", "partial", "loss", "settlement", "procedural_loss"]
# voice of a character in the pre-generated speech (app/tts); usually inferred from the name, see app/tts/voices.py
VoiceGender = Literal["male", "female"]
DecisionKind = Literal["action", "reasoning", "prediction"]
Skill = Literal["procedure", "evidence", "substantive_law", "remedy_choice"]
SKILLS: tuple[str, ...] = ("procedure", "evidence", "substantive_law", "remedy_choice")
# `DecisionPoint.best` value: the correct option is the final outcome of the case.
OUTCOME_BEST = "@outcome"


class _Model(BaseModel):
    """Base: unknown keys are errors, so typos in scenario JSON are caught."""

    model_config = ConfigDict(extra="forbid")


class _OneOf(_Model):
    """A model where exactly one field must be set (DSL node)."""

    @model_validator(mode="after")
    def _exactly_one(self) -> _OneOf:
        if len(self._set_fields()) != 1:
            names = ", ".join(type(self).model_fields)
            raise ValueError(f"exactly one key of [{names}] is required")
        return self

    def _set_fields(self) -> list[tuple[str, Any]]:
        return [(n, v) for n in type(self).model_fields if (v := getattr(self, n)) is not None]

    def active(self) -> tuple[str, Any]:
        """Return (python_field_name, value) of the single set key."""
        return self._set_fields()[0]


# --------------------------------------------------------------------------- conditions


class Gte(_Model):
    """``{"var": "score", "value": N}`` or ``{"count": [flags], "value": N}``."""

    var: Literal["score"] | None = None
    count: list[str] | None = None
    value: int

    @model_validator(mode="after")
    def _one_source(self) -> Gte:
        if (self.var is None) == (self.count is None):
            raise ValueError("gte needs exactly one of 'var' or 'count'")
        return self


class Chose(_Model):
    decision_id: str
    option: str


class Condition(_OneOf):
    """Boolean DSL node: always | flag | not | all | any | gte | chose."""

    always: Literal[True] | None = None
    flag: str | None = None
    not_: Condition | None = Field(None, alias="not")
    all_: list[Condition] | None = Field(None, alias="all")
    any_: list[Condition] | None = Field(None, alias="any")
    gte: Gte | None = None
    chose: Chose | None = None


# --------------------------------------------------------------------------- effects


class Mistake(_Model):
    category: str
    title_key: str
    explanation_key: str
    correct_action_key: str | None = None
    citation_ids: list[str] = []


class Say(_Model):
    speaker: str
    text_key: str
    emotion: str = "neutral"

    @model_validator(mode="before")
    @classmethod
    def _short_form(cls, data: Any) -> Any:
        if isinstance(data, (list, tuple)):
            if len(data) not in (2, 3):
                raise ValueError("say short form is [speaker, text_key] or [speaker, text_key, emotion]")
            keys = ("speaker", "text_key", "emotion")
            return dict(zip(keys, data))
        return data


class React(_Model):
    character: str
    reaction: Reaction

    @model_validator(mode="before")
    @classmethod
    def _short_form(cls, data: Any) -> Any:
        if isinstance(data, (list, tuple)):
            if len(data) != 2:
                raise ValueError("react short form is [character, reaction]")
            return {"character": data[0], "reaction": data[1]}
        return data


class LegalNote(_Model):
    citation_id: str
    text_key: str


class ScoreEffect(_Model):
    """Score change with a short human reason (``score`` also accepts a bare number)."""

    delta: int
    reason_key: str | None = None


class Effect(_OneOf):
    """State-changing DSL node. Exactly one key."""

    set_: str | None = Field(None, alias="set")
    unset: str | None = None
    score: int | ScoreEffect | None = None
    say: Say | None = None
    react: React | None = None
    add_evidence: str | None = None
    mistake: Mistake | None = None
    legal_note: LegalNote | None = None
    goto: str | None = None


# --------------------------------------------------------------------------- scenario parts


class PlayerRole(_Model):
    character_id: str
    title_key: str


class Claim(_Model):
    side: Literal["plaintiff", "defendant"]
    text_key: str


class Card(_Model):
    title_key: str
    category_key: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    minutes: int
    topic_keys: list[str]
    cover: str | None = None
    available: bool = True
    # category, open to everyone: "court" = a court case (hearing in the courtroom), "situation" = a life situation
    # (everyday steps; the frontend shows it without the courtroom)
    kind: Literal["court", "situation"] = "court"

    @model_validator(mode="before")
    @classmethod
    def _legacy_audience(cls, data: Any) -> Any:
        """Case files written on 2026-11-21 used ``audience: public|professional``; read them as ``kind``."""
        if isinstance(data, dict) and "audience" in data:
            data = dict(data)
            audience = data.pop("audience")
            data.setdefault("kind", "situation" if audience == "public" else "court")
        return data


class Intro(_Model):
    story_key: str
    player_role: PlayerRole
    claims: list[Claim]
    legal_acts: list[str]


class Character(_Model):
    id: str
    sprite: str
    name_key: str
    role_key: str
    voice: VoiceGender | None = None  # override; empty = inferred from the name / role text


class Evidence(_Model):
    id: str
    title_key: str
    type: Literal["document", "object", "testimony"]
    text_key: str | None = None
    facts: list[str] = []
    in_case_file: bool = True


class Fact(_Model):
    id: str
    text_key: str
    known_by: list[str]


class NpcQuestion(_Model):
    """A free-text question the player may ask a character; answers come only from ``fact_ids``."""

    question_id: str
    character_id: str
    stages: list[str] = []  # empty = any stage except RESULTS
    label_key: str  # canonical wording of the question
    fact_ids: list[str] = Field(min_length=1)
    answer_key: str  # scripted answer: used without AI and as the fallback
    keywords_key: str | None = None  # comma-separated keywords for the no-AI lexical search


class Transition(_Model):
    to: str
    when: Condition


def _always() -> Condition:
    return Condition(always=True)


class Action(_Model):
    id: str
    kind: ActionKind
    label_key: str
    target_character: str | None = None
    evidence_id: str | None = None
    decision_id: str | None = None
    requires: Condition = Field(default_factory=_always)
    effects: list[Effect] = []
    repeatable: bool = False
    hint_citation_ids: list[str] = []

    @model_validator(mode="after")
    def _decision_needs_id(self) -> Action:
        if self.kind == "decision" and not self.decision_id:
            raise ValueError(f"action '{self.id}': kind 'decision' requires decision_id")
        return self


class Stage(_Model):
    id: str
    title_key: str
    goal_key: str | None = None  # what the player must achieve at this stage
    on_enter: list[Effect] = []
    actions: list[Action] = []
    transitions: list[Transition] = []


class Option(_Model):
    id: str
    label_key: str
    when: Condition | None = None


class DecisionPoint(_Model):
    decision_id: str
    stage: str
    label_key: str
    options: list[Option]
    best: str  # an option id, or "@outcome" (options are then outcome ids; the right one is the final outcome)
    consequences: dict[str, list[Effect]] = {}
    score: dict[str, int] = {}
    score_reason_keys: dict[str, str] = {}  # option id -> why these points
    explanation_key: str
    citation_ids: list[str] = []
    kind: DecisionKind = "action"  # for the debrief: a move, a justification or a forecast
    counterfactual_key: str | None = None  # "what if" text shown in the debrief when chosen != best
    skill: Skill | None = None  # which skill the decision trains (for the results screen)
    outcome_score: int = 0  # only with best "@outcome": bonus added at RESULTS when the forecast is right


class EvaluationRule(_Model):
    outcome: str
    when: Condition
    title_key: str
    ruling_key: str
    result_kind: ResultKind | None = None  # default: derived from `outcome` (see below)

    @model_validator(mode="after")
    def _default_kind(self) -> EvaluationRule:
        if self.result_kind is None:
            self.result_kind = {"claim_granted": "win", "claim_partially_granted": "partial"}.get(
                self.outcome, "loss"
            )
        return self


class MistakeRule(_Model):
    when: Condition
    mistake: Mistake


class Recommendation(_Model):
    topic_key: str
    citation_ids: list[str] = []
    scenario_id: str | None = None


class Scenario(_Model):
    scenario_id: str
    schema_version: Literal[1]
    version: str
    legal_date: date
    fictional_notice_key: str
    reveal_mistakes: bool = False
    max_score: int
    card: Card
    intro: Intro
    citations: list[str]
    characters: list[Character]
    narrator_voice: VoiceGender = "female"  # speaker "narrator" is not a character
    evidence: list[Evidence]
    facts: list[Fact]
    npc_questions: list[NpcQuestion] = []
    stages: list[Stage] = Field(min_length=1)
    decisions: list[DecisionPoint]
    evaluation_rules: list[EvaluationRule]
    mistake_rules: list[MistakeRule] = []
    mistake_categories: list[str]
    recommendations: dict[str, Recommendation] = {}


for _m in (Condition,):
    _m.model_rebuild()
