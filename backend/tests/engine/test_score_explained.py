"""Понятная оценка: причина очков, цель этапа, навыки, «как оценивается», словарик. Без БД."""

import json
import shutil
import uuid

import pytest

from app.game_engine import LoggedAction, evaluate, replay
from app.scenarios import ScenarioValidationError, load_all, load_scenario_dir
from app.schemas.scenario import Effect
from app.services.presenter import build_game_state, build_result, build_scenario_detail
from tests.engine.conftest import BEST, FIXTURES, LOSS, play

SID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _edit(path, fn):
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _find_action(data, action_id):
    return next(a for s in data["stages"] for a in s["actions"] if a["id"] == action_id)


def explained_dir(tmp_path):
    """Копия test_consumer с новыми необязательными полями; возвращает (корень, папка дела)."""
    root = tmp_path / "scenarios"
    shutil.copytree(FIXTURES, root)
    d = root / "test_consumer"

    def sc(data):
        _find_action(data, "present_receipt")["effects"] = [
            e if "score" not in e else {"score": {"delta": e["score"], "reason_key": "why.receipt"}}
            for e in _find_action(data, "present_receipt")["effects"]
        ]
        for st in data["stages"]:
            if st["id"] == "DECISION":
                st["goal_key"] = "goal.decision"
        for dp in data["decisions"]:
            if dp["decision_id"] == "final_claim":
                dp["skill"] = "substantive_law"
                dp["score_reason_keys"] = {"refund": "why.refund"}
            if dp["decision_id"] == "motion_expertise":
                dp["skill"] = "procedure"

    _edit(d / "scenario.json", sc)
    for loc, vals in (
        ("ru", {"why.receipt": "суд видит факт покупки", "why.refund": "верное требование", "goal.decision": "Выберите требование"}),
        ("uz-Latn", {"why.receipt": "sud xaridni ko'radi", "why.refund": "to'g'ri talab", "goal.decision": "Talabni tanlang"}),
    ):
        _edit(d / f"texts.{loc}.json", lambda t, v=vals: t.update(v))
    return root, d


def _score_events(events):
    return [e for e in events if e.type == "score"]


def test_legacy_scenario_has_no_reasons_or_goals():
    loaded = load_scenario_dir(FIXTURES / "test_consumer")
    assert loaded.errors == []
    _, events, per_step = play(loaded.scenario, BEST)
    scores = _score_events(events)
    assert scores and all(e.reason_key is None for e in scores)
    gs = build_game_state(loaded, replay(loaded.scenario, [])[0], [], SID, "ru")
    assert gs.stage_goal is None
    state, _, last = play(loaded.scenario, BEST)
    gs = build_game_state(loaded, state, events, SID, "ru")
    assert all(e.reason is None for e in gs.events if e.type == "score")


def test_effect_score_accepts_number_and_object():
    assert Effect.model_validate({"score": 5}).active() == ("score", 5)
    name, val = Effect.model_validate({"score": {"delta": 5, "reason_key": "k"}}).active()
    assert (name, val.delta, val.reason_key) == ("score", 5, "k")
    assert Effect.model_validate({"score": {"delta": -2}}).active()[1].reason_key is None


def test_reason_in_score_event_and_same_totals(tmp_path):
    root, d = explained_dir(tmp_path)
    loaded = load_scenario_dir(d)
    assert loaded.errors == []
    base = load_scenario_dir(FIXTURES / "test_consumer")
    state, events, per_step = play(loaded.scenario, BEST)
    base_state, _, _ = play(base.scenario, BEST)
    assert state.score == base_state.score  # причины не меняют очки

    receipt = next(i for i, s in enumerate(per_step) if any(e.type == "score" and e.reason_key == "why.receipt" for e in s))
    gs = build_game_state(loaded, state, per_step[receipt], SID, "ru")
    ev = next(e for e in gs.events if e.type == "score")
    assert ev.delta == 6 and ev.reason == "суд видит факт покупки"
    gs_uz = build_game_state(loaded, state, per_step[receipt], SID, "uz-Latn")
    assert next(e for e in gs_uz.events if e.type == "score").reason == "sud xaridni ko'radi"
    cyr = build_game_state(loaded, state, per_step[receipt], SID, "uz-Cyrl")
    assert next(e for e in cyr.events if e.type == "score").reason == "суд харидни кўради"

    # очки за вариант решения
    last = next(s for s in reversed(per_step) if _score_events(s))
    final = _score_events(last)[0]
    assert final.reason_key == "why.refund"
    # очки без причины остаются без неё
    assert any(e.reason_key is None for e in _score_events(events))


def test_forecast_bonus_reason_is_generic_message(tmp_path):
    root, d = explained_dir(tmp_path)

    def sc(data):
        data["decisions"].append({
            "decision_id": "forecast", "stage": "DECISION", "label_key": "dec.final_claim", "kind": "prediction",
            "options": [{"id": o, "label_key": "opt.refund"} for o in ("claim_granted", "claim_partially_granted", "claim_denied")],
            "best": "@outcome", "explanation_key": "expl.final_claim", "outcome_score": 4,
        })
        for st in data["stages"]:
            if st["id"] == "DECISION":
                st["actions"].append({"id": "forecast", "kind": "decision", "label_key": "act.final_claim", "decision_id": "forecast"})
    _edit(d / "scenario.json", sc)
    loaded = load_scenario_dir(d)
    assert loaded.errors == []
    path = BEST[:-1] + [("forecast", {"option": "claim_granted"}), BEST[-1]]
    state, events, per_step = play(loaded.scenario, path)
    bonus = [e for e in _score_events(events) if e.reason_key == "score.forecast_correct"]
    assert len(bonus) == 1 and bonus[0].delta == 4
    gs = build_game_state(loaded, state, per_step[-1], SID, "ru")
    assert next(e for e in gs.events if e.type == "score" and e.delta == 4).reason == "верный прогноз решения суда"


def test_stage_goal(tmp_path):
    root, d = explained_dir(tmp_path)
    loaded = load_scenario_dir(d)
    state, _, per_step = play(loaded.scenario, BEST)  # заканчивается на RESULTS: цели нет
    state_mid, _, per_mid = play(loaded.scenario, BEST[:-1])  # DECISION
    assert state_mid.stage == "DECISION"
    gs = build_game_state(loaded, state_mid, per_mid[-1], SID, "ru")
    assert gs.stage_goal == "Выберите требование"
    assert build_game_state(loaded, state_mid, per_mid[-1], SID, "uz-Latn").stage_goal == "Talabni tanlang"
    first = replay(loaded.scenario, [])[0]
    assert build_game_state(loaded, first, [], SID, "ru").stage_goal is None


def test_skills_and_main_mistake(tmp_path):
    root, d = explained_dir(tmp_path)
    loaded = load_scenario_dir(d)
    state, _, _ = play(loaded.scenario, LOSS)
    outcome = evaluate(loaded.scenario, state)
    res = build_result(loaded, outcome, SID, "ru", [], 10)
    assert [s.skill for s in res.skills] == ["procedure", "evidence", "substantive_law", "remedy_choice"]
    assert [s.label for s in res.skills] == ["Процедура", "Доказательства", "Нормы права", "Выбор требования"]
    by = {s.skill: s for s in res.skills}
    assert (by["substantive_law"].correct, by["substantive_law"].total, by["substantive_law"].percent) == (0, 1, 0)
    assert (by["procedure"].total, by["procedure"].correct) == (1, 0)
    assert by["evidence"].total == 0 and by["evidence"].percent is None
    assert by["remedy_choice"].percent is None
    assert by["procedure"].mistakes >= 1 and by["evidence"].mistakes >= 1
    assert res.main_mistake is not None and res.main_mistake.title == res.mistakes[0].title

    state, _, _ = play(loaded.scenario, BEST)
    res = build_result(loaded, evaluate(loaded.scenario, state), SID, "uz-Latn", [], 10)
    by = {s.skill: s for s in res.skills}
    assert by["substantive_law"].percent == 100 and by["substantive_law"].label == "Huquq normalari"
    assert res.main_mistake is None and all(s.mistakes == 0 for s in res.skills)


def test_legacy_result_has_empty_skills():
    loaded = load_scenario_dir(FIXTURES / "test_consumer")
    state, _, _ = play(loaded.scenario, BEST)
    res = build_result(loaded, evaluate(loaded.scenario, state), SID, "ru", [], 1)
    assert len(res.skills) == 4 and all(s.total == 0 and s.percent is None for s in res.skills)


def test_scoring_card():
    loaded = load_scenario_dir(FIXTURES / "test_consumer")
    detail = build_scenario_detail(loaded, [], "ru")
    sc = detail.scoring
    assert sc.max_score == loaded.scenario.max_score
    assert [s.skill for s in sc.skills] == ["procedure", "evidence", "substantive_law", "remedy_choice"]
    assert all(s.label and s.description and not s.description.startswith("skill.") for s in sc.skills)
    assert [(o.result_kind, o.label) for o in sc.outcomes] == [
        ("win", "Победа"), ("partial", "Частичная победа"), ("loss", "Поражение")
    ]
    uz = build_scenario_detail(loaded, [], "uz-Cyrl").scoring
    assert uz.skills[0].label == "Процедура" and uz.outcomes[0].label == "Ғалаба"


def test_validate_catches_missing_reason_key(tmp_path):
    root, d = explained_dir(tmp_path)
    _edit(d / "texts.ru.json", lambda t: t.pop("why.receipt"))
    with pytest.raises(ScenarioValidationError) as exc:
        load_all(root)
    assert any("why.receipt" in e and "ru" in e for e in exc.value.errors)


def test_validate_catches_missing_score_reason_key_text_and_goal(tmp_path):
    root, d = explained_dir(tmp_path)
    _edit(d / "texts.uz-Latn.json", lambda t: (t.pop("why.refund"), t.pop("goal.decision")))
    errs = load_all(root, strict=False)["test_consumer"].errors
    assert any("why.refund" in e for e in errs) and any("goal.decision" in e for e in errs)


def test_validate_score_reason_key_for_unknown_option(tmp_path):
    root, d = explained_dir(tmp_path)

    def sc(data):
        next(x for x in data["decisions"] if x["decision_id"] == "final_claim")["score_reason_keys"]["ghost"] = "why.refund"
    _edit(d / "scenario.json", sc)
    errs = load_all(root, strict=False)["test_consumer"].errors
    assert any("'ghost' is not an option" in e for e in errs)
