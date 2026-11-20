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
_PREP = ["to_preparation", "ask_invited", "ask_water", "ask_claim_copy", "ask_act_text"]


def path(
    *,
    committee: bool = False,
    poa: str = "poa_notary",  # poa_notary | poa_verbal | poa_passport
    defendant: str = "seller",
    why_defendant: str = "contract",
    settlement: str = "reject",  # reject | accept
    expertise: bool = True,
    why_expertise: str = "burden",
    phone: str = "hand",  # hand | withhold
    closing: str = "act_interested",
    forecast: str = "claim_granted",
    final: str = "replace_full",
    why_remedy: str = "penalty",
) -> list[Step]:
    """Полный путь до RESULTS; ранние концовки (poa, settlement=accept) обрываются сразу."""
    steps: list[Step] = [("enter_courtroom", None)]
    steps += [(a, None) for a in _REVIEWS + _PREP]
    if committee:
        steps += [("file_committee_complaint", None)]
    steps += [_opt("choose_poa", poa)]
    if poa != "poa_notary":
        return steps
    steps += [("to_hearing", None), _opt("choose_defendant", defendant), _opt("explain_defendant", why_defendant),
              ("hear_settlement_offer", None), _opt("settlement", settlement)]
    if settlement == "accept":
        return steps
    steps += [(a, None) for a in (
        "to_explanations", "give_explanation", "ask_defendant_basis", "ask_defendant_service", "to_evidence",
        "present_sale_docs", "present_warranty", "present_claim_letter", "present_service_act", "to_motions",
    )]
    if expertise:
        steps += [("request_expertise", None), _opt("explain_expertise", why_expertise)]
        steps += [("hand_over_phone" if phone == "hand" else "withhold_phone", None)]
    steps += [("finish_motions", None)]
    if expertise and phone == "hand":
        steps += [("review_expert_report", None), ("present_expert_report", None), ("to_debate", None)]
    steps += [(a, None) for a in ("argue_warranty", "argue_burden")]
    steps += [_opt("closing_argument", closing), ("to_decision", None), _opt("forecast", forecast),
              _opt("final_claim", final), _opt("explain_remedy", why_remedy)]
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
    assert sc.scenario_id == SID and sc.version == "1.1.0" and str(sc.legal_date) == "2026-10-01"
    assert sc.reveal_mistakes is False
    # предупреждения только про отсутствующий uz-Cyrl
    assert loaded.warnings and all("uz-Cyrl" in w for w in loaded.warnings)
    assert loaded.quiz is not None and len(loaded.quiz.pre) == 9 and len(loaded.quiz.post) == 9
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
    assert {d.decision_id: d.chosen for d in out.decisions} == {
        "poa": "poa_notary", "defendant": "seller", "why_defendant": "contract", "settlement": "reject",
        "motion_expertise": "request_expertise", "why_expertise": "burden", "closing_argument": "act_interested",
        "outcome_forecast": "claim_granted", "final_claim": "replace_full", "why_remedy": "penalty",
    }
    assert out.result_kind == "win"
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


def test_best_path_is_the_maximum_and_max_score_is_117(sc):
    scores = []
    for kw in (
        {}, {"final": "refund"}, {"final": "refund_penalty"}, {"final": "replace_moral"}, {"closing": "silent"},
        {"closing": "right_to_attend"}, {"defendant": "service"}, {"expertise": False}, {"phone": "withhold"},
        {"settlement": "accept"}, {"poa": "poa_verbal"}, {"forecast": "claim_denied"}, {"why_remedy": "equal"},
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
    # сначала обоснование хода, и только потом выбор про телефон
    assert "explain_expertise" in ids and not {"hand_over_phone", "withhold_phone", "finish_motions"} & ids
    state, _ = apply(sc, state, "explain_expertise", {"option": "burden"})
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


# --------------------------------------------------------------------------- v1.1.0: five outcomes, reasoning, forecast


def test_five_outcomes_and_result_kinds(sc):
    cases = {
        "win": ({}, "claim_granted"),
        "partial": ({"final": "refund_penalty"}, "claim_partially_granted"),
        "loss": ({"expertise": False}, "claim_denied"),
        "settlement": ({"settlement": "accept"}, "settlement"),
        "procedural_loss": ({"poa": "poa_verbal"}, "procedural_loss"),
    }
    for kind, (kw, outcome) in cases.items():
        state, _, out = run(sc, **kw)
        assert (state.outcome, out.result_kind) == (outcome, kind), kind
    assert run(sc, poa="poa_passport")[2].outcome == "procedural_loss"


def test_settlement_ends_early_with_less_score_and_no_false_mistakes(sc):
    win = run(sc)[0]
    state, events, out = run(sc, settlement="accept")
    assert state.score < win.score and state.score < sc.max_score // 2
    assert mistake_titles(out) == set()  # ходатайства и улики на этом пути не успели возникнуть
    assert {d.decision_id for d in out.decisions} == {"poa", "defendant", "why_defendant", "settlement"}
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.226" for e in events)
    assert "expert_report" not in state.evidence


def test_missing_power_of_attorney_leaves_claim_without_consideration(sc):
    state, events, out = run(sc, poa="poa_verbal")
    assert state.outcome == "procedural_loss" and "poa_missing" in state.flags
    assert mistake_titles(out) == {"mistake.no_poa.title"}
    assert [d.decision_id for d in out.decisions] == ["poa"] and not out.decisions[0].correct
    notes = {e.citation_id for e in events if e.type == "legal_note"}
    assert {"CPC.art.122", "CPC.art.123"} <= notes


def test_rejecting_the_settlement_continues_the_case(sc):
    state, events, out = run(sc, settlement="reject")
    assert state.outcome == "claim_granted" and out.result_kind == "win"
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.225" for e in events)


@pytest.mark.parametrize(
    "kw,title,decision",
    [
        ({"why_defendant": "act"}, "mistake.why_defendant.title", "why_defendant"),
        ({"why_expertise": "always"}, "mistake.why_expertise.title", "why_expertise"),
        ({"why_remedy": "only"}, "mistake.why_remedy.title", "why_remedy"),
    ],
)
def test_wrong_reasoning_lowers_score_and_is_a_mistake_but_keeps_outcome(sc, kw, title, decision):
    state, _, out = run(sc, **kw)
    assert state.outcome == "claim_granted"
    assert state.score == sc.max_score - 3 - 2
    assert mistake_titles(out) == {title}
    d = next(x for x in out.decisions if x.decision_id == decision)
    assert d.kind == "reasoning" and not d.correct


def test_forecast_is_checked_against_the_real_outcome(sc):
    state, _, out = run(sc, forecast="claim_granted")
    f = next(d for d in out.decisions if d.decision_id == "outcome_forecast")
    assert f.kind == "prediction" and f.best == "claim_granted" and f.correct and state.score == sc.max_score

    state, _, out = run(sc, forecast="claim_denied")
    f = next(d for d in out.decisions if d.decision_id == "outcome_forecast")
    assert f.best == "claim_granted" and not f.correct and state.score == sc.max_score - 4
    assert state.outcome == "claim_granted" and out.mistakes == ()  # прогноз не влияет на исход и ошибки

    # прогноз сверяется с реальным исходом, а не с «лучшим» ответом
    _, _, out = run(sc, final="refund_penalty", forecast="claim_partially_granted")
    f = next(d for d in out.decisions if d.decision_id == "outcome_forecast")
    assert f.best == "claim_partially_granted" and f.correct


def test_every_decision_has_a_counterfactual_and_kind(sc):
    assert all(d.counterfactual_key for d in sc.decisions)
    assert {d.kind for d in sc.decisions} == {"action", "reasoning", "prediction"}
    _, _, out = run(sc, defendant="service")
    assert all(d.counterfactual_key for d in out.decisions)


def test_committee_complaint_is_optional_and_changes_nothing(sc):
    a = run(sc)
    b = run(sc, committee=True)
    assert (a[0].outcome, a[0].score) == (b[0].outcome, b[0].score)
    assert "committee_complaint" in b[0].flags


def test_constitution_and_new_citations_in_scenario(sc, loaded):
    state, events = initial_state(sc)
    assert {"CONST.art.55", "CONST.art.65"} <= {e.citation_id for e in events if e.type == "legal_note"}
    ids = {c for q in loaded.quiz.pre + loaded.quiz.post for c in q.citation_ids}
    assert {"CONST.art.55", "CONST.art.65"} <= ids
    for c in ("CPC.art.68", "CPC.art.122", "CPC.art.123", "CPC.art.225", "CPC.art.226"):
        assert c in sc.citations


def test_setting_is_uzbekistan_and_official_figure_is_exact(loaded):
    for loc, city in (("ru", "Чиланзар"), ("uz-Latn", "Chilonzor")):
        story = loaded.texts[loc]["intro.story"]
        assert "53 670" in story and "raqobat.gov.uz" in story and city in story
