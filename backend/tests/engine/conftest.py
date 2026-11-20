"""Shared engine test helpers: fixture scenario and golden paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.game_engine import LoggedAction, apply, initial_state
from app.scenarios import load_scenario_dir
from app.schemas.scenario import Scenario

FIXTURES = Path(__file__).parent.parent / "fixtures" / "scenarios"
Step = tuple[str, dict | None]

_REVIEWS = ["review_contract", "review_receipt", "review_warranty", "review_chat", "review_claim_letter"]

BEST: list[Step] = (
    [("enter_courtroom", None)]
    + [(a, None) for a in _REVIEWS]
    + [(a, None) for a in ("to_preparation", "ask_plaintiff_defect", "ask_plaintiff_notice", "to_hearing",
                           "declare_claim", "to_explanations", "give_explanation", "ask_defendant_cause",
                           "to_evidence", "present_contract", "present_receipt", "present_warranty",
                           "present_chat", "present_claim_letter", "object_unverified", "to_motions",
                           "request_expertise", "finish_motions", "review_expert_report",
                           "present_expert_report", "to_debate", "argue_warranty", "argue_burden",
                           "to_decision")]
    + [("final_claim", {"option": "refund"})]
)

PARTIAL: list[Step] = [(a, None) for a in (
    "enter_courtroom", "review_contract", "review_receipt", "review_chat", "to_preparation", "to_hearing",
    "to_explanations", "to_evidence", "present_receipt", "to_motions", "finish_motions",
    "argue_burden", "to_decision")] + [("final_claim", {"option": "refund"})]

LOSS: list[Step] = [(a, None) for a in (
    "enter_courtroom", "review_contract", "review_warranty", "review_claim_letter", "to_preparation",
    "to_hearing", "to_explanations", "to_evidence", "to_motions", "request_witness", "finish_motions",
    "to_decision")] + [("final_claim", {"option": "reduce_price"})]


@pytest.fixture(scope="session")
def scenario() -> Scenario:
    return load_scenario_dir(FIXTURES / "test_consumer").scenario


def play(sc: Scenario, path: list[Step]):
    """Apply a path step by step; returns (final_state, all_events, per_step_events)."""
    state, events = initial_state(sc)
    all_events = list(events)
    per_step = [events]
    for action_id, params in path:
        state, events = apply(sc, state, action_id, params)
        all_events += events
        per_step.append(events)
    return state, all_events, per_step


def to_log(path: list[Step]) -> list[LoggedAction]:
    return [LoggedAction(action_id=a, params=p) for a, p in path]
