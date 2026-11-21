"""Дело rent_deposit_003 «Залог за квартиру»: загрузка, пять исходов, поворот «закон о потребителях не применяется», ловушки, случайные прогулки."""

from __future__ import annotations

import random
import re
import uuid
from pathlib import Path

import pytest

from app.game_engine import apply, available_actions, evaluate, initial_state
from app.scenarios import load_all
from app.scenarios.loader import LoadedScenario
from app.services.presenter import build_result

SCENARIOS_ROOT = Path(__file__).resolve().parents[3] / "scenarios"
SID = "rent_deposit_003"
Step = tuple[str, dict | None]


@pytest.fixture(scope="module")
def loaded() -> LoadedScenario:
    return load_all(SCENARIOS_ROOT, strict=True)[SID]


@pytest.fixture(scope="module")
def sc(loaded):
    return loaded.scenario


def _opt(action: str, option: str) -> Step:
    return (action, {"option": option})


def path(
    *,
    poa: str = "poa_notary",  # poa_notary | poa_verbal | poa_passport
    basis: str = "cc_rent",  # cc_rent | cprl | hybrid
    why_basis: str = "private_person",
    settlement: str = "reject",  # reject | accept
    video: bool = True,
    receipt: bool = True,
    sofa: str = "contest",  # contest | admit_minor | ignore
    photo: bool = True,  # заявить ходатайство об оригинале и осмотреть его
    accept_photo: bool = False,
    site_visit: bool = False,
    closing: str = "act_duty",
    why_burden: str = "landlady_proves",
    forecast: str = "claim_granted",
    final: str = "deposit_interest",
    why_remedy: str = "interest_not_penalty",
) -> list[Step]:
    """Полный путь до RESULTS; ранние концовки (poa, settlement=accept) обрываются сразу."""
    steps: list[Step] = [("enter_courtroom", None)]
    steps += [("review_contract", None), ("review_receipt", None), ("review_act", None), ("to_preparation", None)]
    steps += [("ask_status", None)] + ([("ask_video", None)] if video else []) + [("ask_act", None), ("ask_vacate", None)]
    steps += [_opt("choose_poa", poa)]
    if poa != "poa_notary":
        return steps
    steps += [("to_hearing", None), _opt("choose_basis", basis), _opt("explain_basis", why_basis),
              ("hear_settlement_offer", None), _opt("settlement", settlement)]
    if settlement == "accept":
        return steps
    steps += [("to_explanations", None), ("give_explanation", None), ("ask_defendant_claim", None), ("ask_defendant_photo", None),
              _opt("choose_sofa_position", sofa), ("to_evidence", None), ("present_contract", None)]
    if receipt:
        steps += [("present_receipt", None)]
    steps += [("present_act", None)]
    if video:
        steps += [("present_video", None)]
    steps += [("to_motions", None)]
    if photo:
        steps += [("request_original_photo", None), ("inspect_photo", None)]
    if accept_photo:
        steps += [("accept_photo_print", None)]
    if site_visit:
        steps += [("request_site_visit", None)]
    steps += [("finish_motions", None), ("argue_burden", None), ("argue_return_state", None),
              _opt("closing_argument", closing), _opt("explain_burden", why_burden), ("to_decision", None),
              _opt("forecast", forecast), _opt("final_claim", final), _opt("explain_remedy", why_remedy)]
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


def _ids(sc, state) -> set[str]:
    return {a.id for a in available_actions(sc, state)}


# --------------------------------------------------------------------------- загрузка


def test_loads_strict_without_errors(loaded, sc):
    assert loaded.errors == []
    assert sc.scenario_id == SID and sc.version == "1.0.0" and str(sc.legal_date) == "2026-10-01"
    assert sc.reveal_mistakes is False and sc.card.difficulty == "advanced"
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
        assert city in story and "5 000 000" in story and "2 500 000" in story and "6 000 000" in story


def test_no_state_duty_amounts_are_named(loaded):
    # закона о госпошлине в базе нет: сумм пошлины в предложениях о пошлине быть не должно
    amount = re.compile(r"\d[\d  ]*\s*(сум|so.m)")
    for loc, word in (("ru", "пошлин"), ("uz-Latn", "boj")):
        for key, text in loaded.texts[loc].items():
            for sentence in text.split(". "):
                if word in sentence.lower():
                    assert not amount.search(sentence.lower()), key


# --------------------------------------------------------------------------- исходы


def test_best_path_is_granted_and_gives_max_score(sc):
    state, events, out = run(sc)
    assert state.outcome == "claim_granted" and out.result_kind == "win"
    assert state.score == sc.max_score
    assert out.correct_decision_rate == 1.0 and out.mistakes == ()
    assert {d.decision_id: d.chosen for d in out.decisions} == {
        "poa": "poa_notary", "legal_basis": "cc_rent", "why_basis": "private_person", "settlement": "reject",
        "sofa_position": "contest", "motion_photo": "request_photo", "closing_argument": "act_duty",
        "why_burden": "landlady_proves", "outcome_forecast": "claim_granted", "final_claim": "deposit_interest",
        "why_remedy": "interest_not_penalty",
    }
    assert {"checkin_video", "sofa_photo", "specialist_report"} <= set(state.evidence)
    notes = {e.citation_id for e in events if e.type == "legal_note"}
    assert {"CC2.art.554", "CC2.art.1023", "CPRL.art.29", "CPC.art.89⁴", "CPC.art.89³", "CC1.art.327", "CC2.art.541"} <= notes


def test_deposit_without_interest_is_granted_with_less_score(sc):
    state, _, out = run(sc, final="deposit_only")
    assert state.outcome == "claim_granted" and state.score == sc.max_score - 12 and out.mistakes == ()


def test_claim_under_consumer_law_loses(sc):
    state, events, out = run(sc, basis="cprl")
    assert state.outcome == "claim_denied" and out.result_kind == "loss"
    assert "mistake.consumer_law.title" in mistake_titles(out)
    assert state.score < sc.max_score - 10
    assert any(e.type == "legal_note" and e.citation_id == "CPRL.art.1" for e in events)


def test_hybrid_basis_loses_points_but_not_the_case(sc):
    state, _, out = run(sc, basis="hybrid")
    assert state.outcome == "claim_granted"
    assert state.score == sc.max_score - 5  # 3 балла за основание вместо 8
    assert mistake_titles(out) == {"mistake.cprl_mixed.title"}


def test_no_proof_of_transfer_loses(sc):
    state, _, out = run(sc, receipt=False)
    assert state.outcome == "claim_denied"
    assert "mistake.no_transfer_proof.title" in mistake_titles(out)


@pytest.mark.parametrize("sofa", ["admit_minor", "ignore"])
def test_admitted_or_unanswered_sofa_claim_gives_partial(sc, sofa):
    state, _, out = run(sc, sofa=sofa)
    assert state.outcome == "claim_partially_granted" and out.result_kind == "partial"
    assert ("mistake.admitted_damage.title" if sofa == "admit_minor" else "mistake.sofa_unanswered.title") in mistake_titles(out)
    assert state.score < sc.max_score - 8


def test_video_alone_or_photo_date_alone_refutes_the_sofa_claim(sc):
    s1, _, o1 = run(sc, photo=False)  # есть видео, даты файла нет
    assert s1.outcome == "claim_granted" and mistake_titles(o1) == {"mistake.photo_not_checked.title"}
    s2, _, o2 = run(sc, video=False)  # есть дата файла, видео не найдено
    assert s2.outcome == "claim_granted" and mistake_titles(o2) == {"mistake.video_not_found.title"}
    s3, _, o3 = run(sc, photo=False, video=False)  # ни того ни другого
    assert s3.outcome == "claim_partially_granted"
    assert {"mistake.photo_not_checked.title", "mistake.video_not_found.title"} <= mistake_titles(o3)


def test_accepting_the_photo_print_is_a_trap(sc):
    # согласие с распечаткой: ходатайство о подлиннике уже недоступно, видео спасает исход, но это ошибка
    steps = path(photo=False, accept_photo=True)
    state, _ = play(sc, steps)
    out = evaluate(sc, state)
    assert "mistake.photo_accepted.title" in mistake_titles(out) and state.outcome == "claim_granted"
    assert state.score < sc.max_score - 6 - 4


@pytest.mark.parametrize(
    "final,title",
    [("deposit_penalty", "mistake.penalty_no_basis.title"), ("deposit_moral", "mistake.moral_no_basis.title")],
)
def test_penalty_and_moral_damages_are_partial(sc, final, title):
    state, _, out = run(sc, final=final)
    assert state.outcome == "claim_partially_granted"
    assert mistake_titles(out) == {title} and {m.category for m in out.mistakes} == {"remedy_choice"}


@pytest.mark.parametrize("poa", ["poa_verbal", "poa_passport"])
def test_missing_power_of_attorney_leaves_claim_without_consideration(sc, poa):
    state, events, out = run(sc, poa=poa)
    assert state.outcome == "procedural_loss" and out.result_kind == "procedural_loss" and "poa_missing" in state.flags
    assert mistake_titles(out) == {"mistake.no_poa.title"}
    assert [d.decision_id for d in out.decisions] == ["poa"] and not out.decisions[0].correct
    notes = {e.citation_id for e in events if e.type == "legal_note"}
    assert {"CPC.art.122", "CPC.art.123"} <= notes


def test_settlement_ends_early_with_less_score(sc):
    win = run(sc)[0]
    state, events, out = run(sc, settlement="accept")
    assert state.outcome == "settlement" and out.result_kind == "settlement"
    assert state.score < win.score and state.score < sc.max_score // 2
    assert mistake_titles(out) == set()
    assert {d.decision_id for d in out.decisions} == {"poa", "legal_basis", "why_basis", "settlement"}
    assert any(e.type == "legal_note" and e.citation_id == "CPC.art.226" for e in events)


def test_irrelevant_site_visit_motion_costs_points(sc):
    state, _, out = run(sc, site_visit=True)
    assert state.outcome == "claim_granted" and state.score == sc.max_score - 2
    assert mistake_titles(out) == {"mistake.irrelevant.title"}


def test_act_arguments(sc):
    s1, _, o1 = run(sc, closing="act_unsigned_ok")
    assert s1.outcome == "claim_partially_granted"  # допущено, что акт без замечаний: довод о диване не считается опровергнутым
    assert mistake_titles(o1) == {"mistake.act_conceded.title"}
    s2, _, o2 = run(sc, closing="silent")
    assert s2.outcome == "claim_granted" and s2.score == sc.max_score - 8
    assert mistake_titles(o2) == {"mistake.act_silent.title"}


@pytest.mark.parametrize(
    "kw,title,decision",
    [
        ({"why_basis": "any_citizen"}, "mistake.why_basis.title", "why_basis"),
        ({"why_burden": "court_collects"}, "mistake.why_burden.title", "why_burden"),
        ({"why_remedy": "penalty_ok"}, "mistake.why_remedy.title", "why_remedy"),
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
    _, _, out = run(sc, basis="cprl", forecast="claim_denied")
    assert next(d for d in out.decisions if d.decision_id == "outcome_forecast").correct


def test_best_path_is_the_maximum_and_max_score_matches(sc):
    scores = []
    for kw in (
        {}, {"final": "deposit_only"}, {"final": "deposit_penalty"}, {"basis": "cprl"}, {"basis": "hybrid"}, {"receipt": False},
        {"sofa": "admit_minor"}, {"sofa": "ignore"}, {"photo": False}, {"video": False}, {"site_visit": True},
        {"closing": "silent"}, {"settlement": "accept"}, {"poa": "poa_verbal"}, {"forecast": "claim_denied"}, {"why_remedy": "nothing_more"},
    ):
        scores.append(run(sc, **kw)[0].score)
    assert max(scores) == scores[0] == sc.max_score


# --------------------------------------------------------------------------- механики: скрытый факт, ловушка «ложь документом»


def test_video_appears_only_after_the_right_question(sc):
    state, _ = initial_state(sc)
    for step in path()[: path().index(("ask_status", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert "checkin_video" not in state.evidence
    state, _ = apply(sc, state, "ask_video")
    assert "checkin_video" in state.evidence and "video_known" in state.flags


def test_video_cannot_be_presented_without_asking(sc):
    state, _ = initial_state(sc)
    steps = path(video=False)
    for step in steps[: steps.index(("to_evidence", None)) + 1]:
        state, _ = apply(sc, state, *step)
    assert "present_video" not in _ids(sc, state)


def test_photo_inspection_needs_the_motion_and_excludes_acceptance(sc):
    state, _ = initial_state(sc)
    for step in path()[: path().index(("to_motions", None)) + 1]:
        state, _ = apply(sc, state, *step)
    ids = _ids(sc, state)
    assert {"request_original_photo", "accept_photo_print"} <= ids and "inspect_photo" not in ids
    s2, _ = apply(sc, state, "request_original_photo")
    assert "inspect_photo" in _ids(sc, s2) and "accept_photo_print" not in _ids(sc, s2)
    s3, _ = apply(sc, state, "accept_photo_print")
    assert "request_original_photo" not in _ids(sc, s3)


def test_photo_date_fact_is_known_only_to_the_specialist(sc):
    fact = next(f for f in sc.facts if f.id == "F_PHOTO_DATE")
    assert fact.known_by == ["specialist"]
    q = {x.question_id: x for x in sc.npc_questions}
    assert q["spec_date"].character_id == "specialist" and q["spec_date"].stages == ["MOTIONS"]
    assert next(f for f in sc.facts if f.id == "F_VIDEO").known_by == ["plaintiff"]


def test_consumer_law_is_explained_through_article_one_and_fee_contrast(loaded, sc):
    ids = {c for d in sc.decisions if d.decision_id in ("legal_basis", "why_basis") for c in d.citation_ids}
    assert {"CPRL.art.1", "CPRL.art.29"} <= ids
    for loc in ("ru", "uz-Latn"):
        assert loaded.texts[loc]["note.cprl29"] and "29" in loaded.texts[loc]["note.cprl29"]


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
    "ru": {"win": "Победа", "partial": "Частичная победа", "loss": "Поражение", "settlement": "Мировое соглашение",
           "procedural_loss": "Иск оставлен без рассмотрения"},
    "uz-Latn": {"win": "G'alaba", "partial": "Qisman g'alaba", "loss": "Mag'lubiyat", "settlement": "Kelishuv bitimi",
                "procedural_loss": "Da'vo ko'rilmasdan qoldirildi"},
}
CASES = {
    "win": {}, "partial": {"sofa": "ignore"}, "loss": {"basis": "cprl"}, "settlement": {"settlement": "accept"},
    "procedural_loss": {"poa": "poa_verbal"},
}


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
@pytest.mark.parametrize("kind", list(CASES))
def test_result_kind_label_and_texts(loaded, locale, kind):
    state, _ = play(loaded.scenario, path(**CASES[kind]))
    res = build_result(loaded, evaluate(loaded.scenario, state), uuid.UUID(int=4), locale, [], 30)
    assert res.result_kind == kind and res.result_label == LABELS[locale][kind]
    assert res.outcome_title and res.ruling_text
    for d in res.decisions:
        assert not (d.counterfactual or "").startswith("cf.")
