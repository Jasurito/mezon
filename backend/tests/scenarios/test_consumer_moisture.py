"""Дело consumer_moisture_001 «Влага по акту продавца»: загрузка, три исхода, второстепенные пути, случайные прогулки."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from app.game_engine import apply, available_actions, evaluate, initial_state
from app.scenarios import load_all
from app.scenarios.loader import LoadedScenario

SCENARIOS_ROOT = Path(__file__).resolve().parents[3] / "scenarios"
SID = "consumer_moisture_001"
Step = tuple[str, dict | None]


@pytest.fixture(scope="module")
def loaded() -> LoadedScenario:
    return load_all(SCENARIOS_ROOT, strict=True)[SID]


@pytest.fixture(scope="module")
def sc(loaded):
    return loaded.scenario


def _opt(decision_action: str, option: str) -> Step:
    return (decision_action, {"option": option})


_REVIEWS = ["review_sale_docs", "review_warranty", "review_claim_letter", "review_service_act"]
_PREP = ["to_preparation", "ask_invited", "ask_water", "ask_claim_copy", "ask_act_text", "to_hearing"]


def path(
    *,
    defendant: str = "seller",
    expertise: bool = True,
    phone: str = "hand",  # hand | withhold
    closing: str = "act_interested",
    final: str = "replace_full",
) -> list[Step]:
    steps: list[Step] = [("enter_courtroom", None)]
    steps += [(a, None) for a in _REVIEWS + _PREP]
    steps += [_opt("choose_defendant", defendant)]
    steps += [(a, None) for a in (
        "to_explanations", "give_explanation", "ask_defendant_basis", "ask_defendant_service", "to_evidence",
        "present_sale_docs", "present_warranty", "present_claim_letter", "present_service_act", "to_motions",
    )]
    if expertise:
        steps += [("request_expertise", None)]
        steps += [("hand_over_phone" if phone == "hand" else "withhold_phone", None)]
    steps += [("finish_motions", None)]
    if expertise and phone == "hand":
        steps += [("review_expert_report", None), ("present_expert_report", None), ("to_debate", None)]
    steps += [(a, None) for a in ("argue_warranty", "argue_burden")]
    steps += [_opt("closing_argument", closing), ("to_decision", None), _opt("final_claim", final)]
    return steps


def play(sc, steps: list[Step]):
    state, events = initial_state(sc)
    all_events = list(events)
    for action_id, params in steps:
        state, events = apply(sc, state, action_id, params)
        all_events += events
    return state, all_events


def run(sc, **kw):
    state, events = play(sc, path(**kw))
    assert state.finished and state.stage == "RESULTS"
    return state, events, evaluate(sc, state)


def mistake_titles(out) -> set[str]:
    return {m.title_key for m in out.mistakes}


# --------------------------------------------------------------------------- loading


def test_loads_strict_without_errors(loaded, sc):
    assert loaded.errors == []
    assert sc.scenario_id == SID and sc.version == "1.0.0" and str(sc.legal_date) == "2026-10-01"
    assert sc.reveal_mistakes is False
    # предупреждения только про отсутствующий uz-Cyrl
    assert loaded.warnings and all("uz-Cyrl" in w for w in loaded.warnings)
    assert loaded.quiz is not None and len(loaded.quiz.pre) == 8 and len(loaded.quiz.post) == 8
    assert [s.id for s in sc.stages] == [
        "INTRO", "CASE_REVIEW", "PREPARATION", "HEARING_OPENING", "PARTY_EXPLANATIONS",
        "EVIDENCE_EXAMINATION", "MOTIONS", "DEBATE", "DECISION", "RESULTS",
    ]


def test_ru_and_uz_latn_cover_the_same_keys(loaded):
    assert set(loaded.texts["ru"]) == set(loaded.texts["uz-Latn"])


def test_quiz_citations_are_in_scenario(loaded, sc):
    quiz_ids = {c for q in loaded.quiz.pre + loaded.quiz.post for c in q.citation_ids}
    assert quiz_ids and quiz_ids <= set(sc.citations)


# --------------------------------------------------------------------------- outcomes


def test_best_path_is_granted_and_gives_max_score(sc):
    state, events, out = run(sc)
    assert state.outcome == "claim_granted"
    assert state.score == sc.max_score
    assert out.correct_decision_rate == 1.0 and out.mistakes == ()
    assert [d.chosen for d in out.decisions] == ["seller", "request_expertise", "act_interested", "replace_full"]
    assert "expert_report" in state.evidence and "defect_proven" in state.flags
    notes = {e.citation_id for e in events if e.type == "legal_note"}
    assert {"CPRL.art.14", "CPC.art.95", "CC2.art.409"} <= notes


def test_refund_without_penalty_is_granted_too(sc):
    state, _, out = run(sc, final="refund")
    assert state.outcome == "claim_granted"
    assert state.score < sc.max_score
    assert mistake_titles(out) == set()


def test_wrong_closing_argument_lowers_score_but_not_outcome(sc):
    state, _, out = run(sc, closing="right_to_attend")
    assert state.outcome == "claim_granted"
    assert state.score == sc.max_score - 8 - 3
    assert mistake_titles(out) == {"mistake.no_right_to_attend.title"}
    assert {m.category for m in out.mistakes} == {"substantive_law"}


def test_refund_with_penalty_is_partial(sc):
    state, _, out = run(sc, final="refund_penalty")
    assert state.outcome == "claim_partially_granted"
    assert mistake_titles(out) == {"mistake.refund_penalty.title"}
    assert {m.category for m in out.mistakes} == {"remedy_choice"}


@pytest.mark.parametrize("final", ["replace_moral", "refund_moral"])
def test_unproven_moral_damage_is_partial(sc, final):
    state, _, out = run(sc, final=final)
    assert state.outcome == "claim_partially_granted"
    assert mistake_titles(out) == {"mistake.moral_unproven.title"}


def test_no_expertise_is_denied(sc):
    state, _, out = run(sc, expertise=False)
    assert state.outcome == "claim_denied"
    assert "mistake.no_expertise.title" in mistake_titles(out)
    assert {m.category for m in out.mistakes} == {"procedure"}
    assert "expert_report" not in state.evidence


def test_wrong_defendant_is_denied(sc):
    state, _, out = run(sc, defendant="service")
    assert state.outcome == "claim_denied"
    assert mistake_titles(out) == {"mistake.wrong_defendant.title"}
    assert {m.category for m in out.mistakes} == {"procedure"}


def test_withholding_the_phone_is_denied(sc):
    state, events, out = run(sc, phone="withhold")
    assert state.outcome == "claim_denied"
    assert "mistake.phone_withheld.title" in mistake_titles(out)
    assert "defect_proven" not in state.flags
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.95" for e in events)


def test_best_path_is_the_maximum(sc):
    scores = []
    for kw in (
        {}, {"final": "refund"}, {"final": "refund_penalty"}, {"final": "replace_moral"}, {"closing": "silent"},
        {"closing": "right_to_attend"}, {"defendant": "service"}, {"expertise": False}, {"phone": "withhold"},
    ):
        scores.append(run(sc, **kw)[0].score)
    assert max(scores) == scores[0] == sc.max_score


# --------------------------------------------------------------------------- engine behaviour


def test_expertise_without_phone_choice_cannot_finish_motions(sc):
    state, _ = initial_state(sc)
    for step in path()[: path().index(("request_expertise", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert state.stage == "MOTIONS"
    ids = {a.id for a in available_actions(sc, state)}
    assert "finish_motions" not in ids and {"hand_over_phone", "withhold_phone"} <= ids
    state, _ = apply(sc, state, "withhold_phone")
    ids = {a.id for a in available_actions(sc, state)}
    assert "hand_over_phone" not in ids and "finish_motions" in ids


def test_expert_report_is_examined_after_motions(sc):
    state, _ = initial_state(sc)
    for step in path()[: path().index(("finish_motions", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert state.stage == "EVIDENCE_EXAMINATION"
    assert "review_expert_report" in {a.id for a in available_actions(sc, state)}


def test_random_walks_reach_results_without_exceeding_max(sc):
    for seed in range(200):
        rng = random.Random(seed)
        state, _ = initial_state(sc)
        steps = 0
        while not state.finished:
            actions = available_actions(sc, state)
            assert actions, f"seed {seed}: dead end on {state.stage}"
            a = rng.choice(actions)
            params = {"option": rng.choice(a.options).id} if a.kind == "decision" else None
            state, _ = apply(sc, state, a.id, params)
            steps += 1
            assert steps <= 200, f"seed {seed}: no RESULTS within 200 steps"
        assert state.stage == "RESULTS" and state.outcome
        assert state.score <= sc.max_score, f"seed {seed}: score {state.score} > max {sc.max_score}"
