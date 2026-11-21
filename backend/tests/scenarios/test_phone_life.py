"""Жизненная ситуация phone_defect_life_001 «Телефон сломался через 10 дней» (audience public): тот же формат дела,
другие этапы. Загрузка, три исхода, ловушки в папке, разбор с «что если»."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.game_engine import apply, available_actions, evaluate, initial_state
from app.scenarios import load_all
from app.scenarios.loader import LoadedScenario

SCENARIOS_ROOT = Path(__file__).resolve().parents[3] / "scenarios"
SID = "phone_defect_life_001"
Step = tuple[str, dict | None]


@pytest.fixture(scope="module")
def loaded() -> LoadedScenario:
    return load_all(SCENARIOS_ROOT, strict=True)[SID]


@pytest.fixture(scope="module")
def sc(loaded):
    return loaded.scenario


def _opt(action: str, option: str) -> Step:
    return (action, {"option": option})


def path(*, recognize="rights", keep=("receipt", "warranty", "chat", "photo"), who="seller", remedy="replace",
         claim="written", deadline="d7", burden="seller", next_step="complain") -> list[Step]:
    steps: list[Step] = [_opt("recognize", recognize)]
    steps += [(f"keep_{k}", None) for k in keep] + [("evidence_done", None)]
    steps += [_opt("who_to", who), _opt("remedy", remedy)]
    steps += [_opt("claim_form", claim), _opt("deadline", deadline)]
    steps += [_opt("burden", burden), _opt("next_step", next_step)]
    return steps


def run(sc, **kw):
    state, _ = initial_state(sc)
    for action_id, params in path(**kw):
        state, _ = apply(sc, state, action_id, params)
    assert state.finished and state.stage == "RESULTS"
    return state, evaluate(sc, state)


def test_public_card(sc):
    assert sc.card.audience == "public"
    assert sc.stages[0].id == "SITUATION"


def test_best_path_is_a_win_with_max_score(sc):
    state, out = run(sc)
    assert out.outcome == "resolved" and out.result_kind == "win"
    assert state.score == sc.max_score
    assert out.mistakes == () or list(out.mistakes) == []
    assert all(d.correct for d in out.decisions)


def test_partial_when_core_steps_done(sc):
    _, out = run(sc, remedy="refund", next_step="give_up")
    assert out.outcome == "partly_resolved" and out.result_kind == "partial"
    wrong = {d.decision_id: d for d in out.decisions if not d.correct}
    assert set(wrong) == {"remedy", "next_step"}
    assert all(d.counterfactual_key for d in wrong.values())


def test_loss_and_mistakes(sc):
    _, out = run(sc, recognize="my_loss", keep=("review", "flyer"), who="service", remedy="seller_decides",
                 claim="call", deadline="any", burden="buyer", next_step="review")
    assert out.outcome == "unresolved" and out.result_kind == "loss"
    cats = sorted(m.category for m in out.mistakes)
    assert cats.count("evidence") == 2 and "procedure" in cats and "substantive_law" in cats and "remedy_choice" in cats


def test_claim_copy_appears_only_after_written_claim(sc):
    state, _ = initial_state(sc)
    for step in path()[:-4]:  # up to CLAIM
        state, _ = apply(sc, state, *step)
    assert "claim_copy" not in state.evidence
    state, _ = apply(sc, state, "claim_form", {"option": "written"})
    assert "claim_copy" in state.evidence


def test_every_stage_offers_a_way_forward(sc):
    state, _ = initial_state(sc)
    for step in path():
        assert available_actions(sc, state), f"no actions at {state.stage}"
        state, _ = apply(sc, state, *step)
