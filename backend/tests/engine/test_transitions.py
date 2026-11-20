import pytest

from app.game_engine import (
    IllegalAction, SessionFinished, apply, available_actions, initial_state,
)
from tests.engine.conftest import BEST, LOSS, play


def test_every_stage_reachable_by_real_actions(scenario):
    _, events, _ = play(scenario, BEST)
    visited = {e.stage for e in events if e.type == "stage_changed"}
    assert visited == {s.id for s in scenario.stages}


def test_motions_and_evidence_are_linked_both_ways(scenario):
    _, events, _ = play(scenario, BEST)
    seq = [e.stage for e in events if e.type == "stage_changed"]
    i = seq.index("MOTIONS")
    assert seq[i - 1] == "EVIDENCE_EXAMINATION" and seq[i + 1] == "EVIDENCE_EXAMINATION"


def test_unavailable_action_is_illegal(scenario):
    state, _ = initial_state(scenario)
    with pytest.raises(IllegalAction) as exc:
        apply(scenario, state, "final_claim", {"option": "refund"})
    assert exc.value.action_id == "final_claim" and exc.value.stage == "INTRO"
    with pytest.raises(IllegalAction):
        apply(scenario, state, "no_such_action")


def test_requires_blocks_action(scenario):
    # on EVIDENCE_EXAMINATION without having reviewed the receipt
    state, _, _ = play(scenario, LOSS[:8])
    assert state.stage == "EVIDENCE_EXAMINATION" and "receipt_reviewed" not in state.flags
    assert "present_receipt" not in {a.id for a in available_actions(scenario, state)}
    with pytest.raises(IllegalAction):
        apply(scenario, state, "present_receipt")


def test_after_finish_session_finished(scenario):
    state, _, _ = play(scenario, BEST)
    assert state.finished and available_actions(scenario, state) == []
    with pytest.raises(SessionFinished):
        apply(scenario, state, "enter_courtroom")


def _at_decision(scenario):
    return play(scenario, BEST[:-1])[0]


def test_decision_needs_valid_option(scenario):
    state = _at_decision(scenario)
    assert state.stage == "DECISION"
    for params in (None, {}, {"option": "bogus"}):
        with pytest.raises(IllegalAction):
            apply(scenario, state, "final_claim", params)


def test_decision_offers_options(scenario):
    (act,) = available_actions(scenario, _at_decision(scenario))
    assert act.kind == "decision"
    assert [o.id for o in act.options] == ["repair", "replace", "refund", "reduce_price"]


def test_non_repeatable_action_disappears(scenario):
    state, _ = initial_state(scenario)
    state, _ = apply(scenario, state, "enter_courtroom")
    ids = lambda s: {a.id for a in available_actions(scenario, s)}
    assert "review_contract" in ids(state)
    state, _ = apply(scenario, state, "review_contract")
    assert "review_contract" not in ids(state)
    with pytest.raises(IllegalAction):
        apply(scenario, state, "review_contract")


def test_repeatable_action_stays(scenario):
    sc = scenario.model_copy(deep=True)
    next(a for s in sc.stages for a in s.actions if a.id == "review_contract").repeatable = True
    state, _ = initial_state(sc)
    state, _ = apply(sc, state, "enter_courtroom")
    state, _ = apply(sc, state, "review_contract")
    state, _ = apply(sc, state, "review_contract")
    assert state.performed.count("review_contract") == 2


def test_apply_does_not_mutate_old_state(scenario):
    s0, _ = initial_state(scenario)
    snapshot = s0.model_dump()
    apply(scenario, s0, "enter_courtroom")
    assert s0.model_dump() == snapshot
