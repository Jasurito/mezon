"""Дело wedding_photo_002 «Фотограф потерял свадьбу»: загрузка, исходы, ловушки, ресурс «два вопроса эксперту», случайные прогулки."""

from __future__ import annotations

import random
import uuid
from pathlib import Path

import pytest

from app.game_engine import apply, available_actions, evaluate, initial_state
from app.scenarios import load_all
from app.scenarios.loader import LoadedScenario
from app.services.presenter import build_result

SCENARIOS_ROOT = Path(__file__).resolve().parents[3] / "scenarios"
SID = "wedding_photo_002"
Step = tuple[str, dict | None]


@pytest.fixture(scope="module")
def loaded() -> LoadedScenario:
    return load_all(SCENARIOS_ROOT, strict=True)[SID]


@pytest.fixture(scope="module")
def sc(loaded):
    return loaded.scenario


def _opt(action: str, option: str) -> Step:
    return (action, {"option": option})


_REVIEWS = ["review_payment", "review_chat", "review_website", "review_claim"]
_ASKS = ["ask_prepay", "ask_chat_phone", "ask_admission", "ask_losses"]


def path(
    *,
    proof: str = "original_phone",  # original_phone | notary | print_screens
    why_proof: str = "print_not_written",
    defendant: str = "studio",
    why_defendant: str = "contract_party",
    settlement: str = "reject",  # reject | accept
    guest: str = "chat_refute",  # chat_refute | just_deny | accept_guest
    witness: bool = True,
    expertise: bool = True,
    expert_qs: tuple[str, ...] = ("recovery", "cause"),
    closing: str = "no_result",
    forecast: str = "claim_granted",
    final: str = "refund_damages_moral",
    why_moral: str = "fault_reasonable",
) -> list[Step]:
    """Полный путь до RESULTS; settlement=accept обрывается сразу."""
    steps: list[Step] = [("enter_courtroom", None)]
    steps += [(a, None) for a in _REVIEWS] + [("to_preparation", None)]
    steps += [(a, None) for a in _ASKS]
    steps += [_opt("choose_proof", proof), _opt("explain_proof", why_proof), ("to_hearing", None)]
    steps += [_opt("choose_defendant", defendant), _opt("explain_defendant", why_defendant),
              ("hear_settlement_offer", None), _opt("settlement", settlement)]
    if settlement == "accept":
        return steps
    steps += [("to_explanations", None), ("give_explanation", None), ("ask_studio_cause", None),
              ("ask_studio_site", None), ("to_evidence", None)]
    ok = proof != "print_screens"
    steps += [("present_payment" if ok else "present_payment_print", None),
              ("present_chat" if ok else "present_chat_print", None),
              ("present_website", None), ("present_claim", None), _opt("answer_guest_claim", guest), ("to_motions", None)]
    if witness:
        steps += [("request_witness", None), ("ask_witness_backup", None), ("ask_witness_guests", None)]
    if expertise:
        steps += [("request_expertise", None)] + [(f"ask_expert_{q}", None) for q in expert_qs]
    steps += [("finish_motions", None), ("argue_terms", None)]
    if ok:
        steps += [("argue_original", None)]
    steps += [_opt("closing_argument", closing), ("to_decision", None), _opt("forecast", forecast),
              _opt("final_claim", final), _opt("explain_moral", why_moral)]
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


# --------------------------------------------------------------------------- загрузка


def test_loads_strict_without_errors(loaded, sc):
    assert loaded.errors == []
    assert sc.scenario_id == SID and sc.version == "1.1.0" and str(sc.legal_date) == "2026-10-01"
    assert sc.reveal_mistakes is False and sc.card.difficulty == "intermediate"
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


def test_every_decision_has_a_counterfactual_and_kind(sc):
    assert all(d.counterfactual_key for d in sc.decisions)
    assert {d.kind for d in sc.decisions} == {"action", "reasoning", "prediction"}
    assert next(d for d in sc.decisions if d.decision_id == "outcome_forecast").best == "@outcome"


def test_setting_is_uzbekistan_and_amounts_are_exact(loaded):
    for loc, city in (("ru", "Ташкент"), ("uz-Latn", "Toshkent")):
        story = loaded.texts[loc]["intro.story"]
        assert city in story and "8 000 000" in story and "4 000 000" in story and "2 500 000" in story


# --------------------------------------------------------------------------- исходы


def test_best_path_is_granted_and_gives_max_score(sc):
    state, events, out = run(sc)
    assert state.outcome == "claim_granted" and out.result_kind == "win"
    assert state.score == sc.max_score
    assert out.correct_decision_rate == 1.0 and out.mistakes == ()
    assert {d.decision_id: d.chosen for d in out.decisions} == {
        "proof_form": "original_phone", "why_proof": "print_not_written", "defendant": "studio",
        "why_defendant": "contract_party", "settlement": "reject", "guest_claim": "chat_refute",
        "motion_witness": "request_witness", "motion_expertise": "request_expertise",
        "closing_argument": "no_result", "outcome_forecast": "claim_granted", "final_claim": "refund_damages_moral",
        "why_moral": "fault_reasonable",
    }
    assert {"expert_report", "witness_testimony"} <= set(state.evidence)
    notes = {e.citation_id for e in events if e.type == "legal_note"}
    assert {"CPC.art.89²", "CPC.art.89¹", "CPC.art.82", "CPC.art.95", "CPRL.art.19", "CPRL.art.22", "CPRL.art.29"} <= notes


def test_notarized_copies_are_also_admissible_but_score_less(sc):
    state, _, out = run(sc, proof="notary")
    assert state.outcome == "claim_granted" and state.score == sc.max_score - 2 and out.mistakes == ()


def test_refund_without_moral_is_granted_with_less_score(sc):
    state, _, out = run(sc, final="refund_damages")
    assert state.outcome == "claim_granted" and state.score == sc.max_score - 12 and out.mistakes == ()


def test_printed_screenshots_without_original_lose_the_case(sc):
    state, events, out = run(sc, proof="print_screens")
    assert state.outcome == "claim_denied" and out.result_kind == "loss"
    assert "mistake.printed_screens.title" in mistake_titles(out)
    assert {"payment_rejected", "chat_rejected"} <= set(state.flags) and "chat_presented" not in state.flags
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.89²" for e in events)


def test_wrong_defendant_is_denied(sc):
    for wrong in ("photographer", "payment_app"):
        state, _, out = run(sc, defendant=wrong)
        assert state.outcome == "claim_denied"
        assert "mistake.wrong_defendant.title" in mistake_titles(out)


def test_chat_admission_alone_proves_fault_without_witness_and_expert(sc):
    state, _, out = run(sc, witness=False, expertise=False)
    assert state.outcome == "claim_granted"
    assert mistake_titles(out) == {"mistake.no_witness.title", "mistake.no_expertise.title"}


def test_witness_plus_expert_prove_fault_without_chat_refutation(sc):
    state, _, out = run(sc, guest="just_deny")
    assert state.outcome == "claim_granted"  # вина доказана вторым путём: свидетель про вторую карту и причина износа
    assert mistake_titles(out) == {"mistake.guest_unrefuted.title"}


def test_unrefuted_guest_version_without_other_proof_is_partial(sc):
    state, _, out = run(sc, guest="just_deny", witness=False)
    assert state.outcome == "claim_partially_granted" and out.result_kind == "partial"
    assert {"mistake.guest_unrefuted.title", "mistake.no_witness.title", "mistake.fault_not_proven.title"} <= mistake_titles(out)


def test_accepting_the_guest_version_is_partial(sc):
    state, _, out = run(sc, guest="accept_guest")
    assert state.outcome == "claim_partially_granted"
    assert "mistake.guest_accepted.title" in mistake_titles(out)


@pytest.mark.parametrize(
    "final,title",
    [("refund_damages_penalty", "mistake.penalty_misuse.title"), ("refund_moral_billion", "mistake.moral_billion.title")],
)
def test_unjustified_claims_are_partial(sc, final, title):
    state, _, out = run(sc, final=final)
    assert state.outcome == "claim_partially_granted"
    assert mistake_titles(out) == {title}
    assert {m.category for m in out.mistakes} == {"remedy_choice"}


def test_settlement_accepted_ends_early(sc):
    win = run(sc)[0]
    state, events, out = run(sc, settlement="accept")
    assert state.outcome == "settlement" and out.result_kind == "settlement"
    assert state.score < win.score and state.score < sc.max_score // 2
    assert mistake_titles(out) == set()
    assert {d.decision_id for d in out.decisions} == {"proof_form", "why_proof", "defendant", "why_defendant", "settlement"}
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.226" for e in events)


def test_closing_argument_variants(sc):
    s1, _, o1 = run(sc, closing="double_price")
    assert s1.outcome == "claim_granted" and s1.score == sc.max_score - 8 - 3
    assert mistake_titles(o1) == {"mistake.double_price.title"}
    s2, _, o2 = run(sc, closing="silent")
    assert s2.score == sc.max_score - 8 and mistake_titles(o2) == {"mistake.closing_silent.title"}


@pytest.mark.parametrize(
    "kw,title,decision",
    [
        ({"why_proof": "print_enough"}, "mistake.why_proof.title", "why_proof"),
        ({"why_defendant": "who_shot"}, "mistake.why_defendant.title", "why_defendant"),
        ({"why_moral": "automatic"}, "mistake.why_moral.title", "why_moral"),
    ],
)
def test_wrong_reasoning_lowers_score_but_keeps_outcome(sc, kw, title, decision):
    state, _, out = run(sc, **kw)
    assert state.outcome == "claim_granted" and state.score == sc.max_score - 3 - 2
    assert mistake_titles(out) == {title}
    d = next(x for x in out.decisions if x.decision_id == decision)
    assert d.kind == "reasoning" and not d.correct


def test_forecast_is_checked_against_the_real_outcome(sc):
    state, _, out = run(sc, forecast="claim_granted")
    f = next(d for d in out.decisions if d.decision_id == "outcome_forecast")
    assert f.kind == "prediction" and f.best == "claim_granted" and f.correct and state.score == sc.max_score
    state, _, out = run(sc, forecast="claim_denied")
    f = next(d for d in out.decisions if d.decision_id == "outcome_forecast")
    assert not f.correct and state.score == sc.max_score - 4 and state.outcome == "claim_granted"
    _, _, out = run(sc, final="refund_moral_billion", forecast="claim_partially_granted")
    assert next(d for d in out.decisions if d.decision_id == "outcome_forecast").correct


def test_best_path_is_the_maximum_and_max_score_matches(sc):
    scores = []
    for kw in (
        {}, {"proof": "notary"}, {"proof": "print_screens"}, {"final": "refund_damages"}, {"final": "refund_moral_billion"},
        {"guest": "just_deny"}, {"guest": "accept_guest"}, {"witness": False}, {"expertise": False},
        {"expert_qs": ("price", "guest")}, {"closing": "double_price"}, {"settlement": "accept"}, {"defendant": "payment_app"},
        {"forecast": "claim_denied"}, {"why_moral": "never"},
    ):
        scores.append(run(sc, **kw)[0].score)
    assert max(scores) == scores[0] == sc.max_score


# --------------------------------------------------------------------------- механики: цифровые доказательства, свидетель, эксперт


def _reach_motions(sc, **kw):
    steps = path(**kw)
    state, _ = initial_state(sc)
    for step in steps[: steps.index(("to_motions", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert state.stage == "MOTIONS"
    return state


def _ids(sc, state) -> set[str]:
    return {a.id for a in available_actions(sc, state)}


def test_printed_variants_are_offered_only_after_the_weak_choice(sc):
    state, _ = initial_state(sc)
    for step in path()[: path().index(("to_evidence", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert {"present_payment", "present_chat"} <= _ids(sc, state)
    assert not {"present_payment_print", "present_chat_print"} & _ids(sc, state)

    state, _ = initial_state(sc)
    weak = path(proof="print_screens")
    for step in weak[: weak.index(("to_evidence", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert {"present_payment_print", "present_chat_print"} <= _ids(sc, state)
    assert not {"present_payment", "present_chat"} & _ids(sc, state)


def test_witness_and_expert_questions_need_the_motions(sc):
    state = _reach_motions(sc)
    ids = _ids(sc, state)
    assert not {"ask_witness_backup", "ask_witness_guests", "ask_expert_recovery", "ask_expert_cause"} & ids
    state, _ = apply(sc, state, "request_witness")
    ids = _ids(sc, state)
    assert {"ask_witness_backup", "ask_witness_guests"} <= ids and "ask_expert_recovery" not in ids
    state, _ = apply(sc, state, "request_expertise")
    assert {"ask_expert_recovery", "ask_expert_cause", "ask_expert_price", "ask_expert_guest"} <= _ids(sc, state)


@pytest.mark.parametrize("pair", [("recovery", "cause"), ("price", "guest"), ("cause", "price"), ("guest", "recovery")])
def test_expert_can_answer_only_two_of_four_questions(sc, pair):
    state = _reach_motions(sc)
    state, _ = apply(sc, state, "request_expertise")
    for q in pair:
        assert f"ask_expert_{q}" in _ids(sc, state)
        state, _ = apply(sc, state, f"ask_expert_{q}")
    left = {a for a in _ids(sc, state) if a.startswith("ask_expert_")}
    assert left == set()  # лимит исчерпан, остальные вопросы недоступны
    assert "finish_motions" in _ids(sc, state)


def test_wasted_expert_question_is_a_mistake_and_costs_proof(sc):
    state, _, out = run(sc, expert_qs=("recovery", "price"), guest="just_deny")
    assert "mistake.expert_wasted.title" in mistake_titles(out)
    assert "eq_cause" not in state.flags
    # вина тогда не доказана вторым путём (нет причины повреждения), а первый путь отвергнут
    assert state.outcome == "claim_partially_granted"
    assert state.score < sc.max_score - 10


def test_hidden_fact_about_the_second_card_comes_only_from_the_witness(loaded, sc):
    q = {x.question_id: x for x in sc.npc_questions}
    assert q["wit_second_card"].character_id == "witness" and q["wit_second_card"].stages == ["MOTIONS"]
    fact = next(f for f in sc.facts if f.id == "F_NO_SECOND_CARD")
    assert fact.known_by == ["witness"]
    # у эксперта нет свободных вопросов: ресурс «два вопроса» нельзя обойти текстом
    assert not [x for x in sc.npc_questions if x.character_id == "expert"]
    for loc in ("ru", "uz-Latn"):
        assert "две карты" in loaded.texts[loc]["fact.F_SITE_AD"] or "ikki" in loaded.texts[loc]["fact.F_SITE_AD"]


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


# --------------------------------------------------------------------------- результат в API-виде

LABELS = {
    "ru": {"win": "Победа", "partial": "Частичная победа", "loss": "Поражение", "settlement": "Мировое соглашение"},
    "uz-Latn": {"win": "G'alaba", "partial": "Qisman g'alaba", "loss": "Mag'lubiyat", "settlement": "Kelishuv bitimi"},
}
CASES = {
    "win": {}, "partial": {"final": "refund_moral_billion"}, "loss": {"proof": "print_screens"},
    "settlement": {"settlement": "accept"},
}


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
@pytest.mark.parametrize("kind", list(CASES))
def test_result_kind_label_and_texts(loaded, locale, kind):
    state, _ = play(loaded.scenario, path(**CASES[kind]))
    res = build_result(loaded, evaluate(loaded.scenario, state), uuid.UUID(int=3), locale, [], 30)
    assert res.result_kind == kind and res.result_label == LABELS[locale][kind]
    assert res.outcome_title and res.ruling_text
    for d in res.decisions:
        assert not (d.counterfactual or "").startswith("cf.")
