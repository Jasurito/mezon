"""Condition DSL interpreter. Works on anything with flags, score and choices."""

from __future__ import annotations

from collections.abc import Collection, Mapping
from typing import Protocol

from app.game_engine.errors import ScenarioError
from app.schemas.scenario import Condition


class HasFacts(Protocol):
    flags: Collection[str]
    score: int
    choices: Mapping[str, str]


def eval_condition(cond: Condition, s: HasFacts) -> bool:
    """Evaluate a condition against flags, score and explicit choices."""
    name, val = cond.active()
    if name == "always":
        return True
    if name == "flag":
        return val in s.flags
    if name == "not_":
        return not eval_condition(val, s)
    if name == "all_":
        return all(eval_condition(c, s) for c in val)
    if name == "any_":
        return any(eval_condition(c, s) for c in val)
    if name == "gte":
        have = s.score if val.var == "score" else sum(1 for f in val.count if f in s.flags)
        return have >= val.value
    if name == "chose":
        return s.choices.get(val.decision_id) == val.option
    raise ScenarioError(f"unknown condition '{name}'")
