"""Схема npc_questions и проверки validate_scenario."""

import copy

from app.game_engine import collect_text_keys, validate_scenario
from app.schemas.scenario import Scenario


def broken(sc: Scenario, mutate) -> list[str]:
    data = copy.deepcopy(sc.model_dump(mode="json", by_alias=True))
    mutate(data)
    return validate_scenario(Scenario.model_validate(data))


def has(errors: list[str], text: str) -> bool:
    return any(text in e for e in errors)


def q(data, qid="plaintiff_defect"):
    return next(x for x in data["npc_questions"] if x["question_id"] == qid)


def test_fixture_is_valid(scenario):
    assert validate_scenario(scenario) == []
    assert len(scenario.npc_questions) >= 4


def test_old_scenario_without_field_is_valid(scenario):
    data = scenario.model_dump(mode="json", by_alias=True)
    del data["npc_questions"]
    data["facts"] = [f for f in data["facts"] if not f["id"].startswith(("F_DEFECT_DATE", "F_COMPLAINT", "F_DEFENDANT"))]
    old = Scenario.model_validate(data)
    assert old.npc_questions == []
    assert validate_scenario(old) == []


def test_unknown_character(scenario):
    assert has(broken(scenario, lambda d: q(d).update(character_id="ghost")), "unknown character 'ghost'")


def test_unknown_fact(scenario):
    assert has(broken(scenario, lambda d: q(d).update(fact_ids=["F_NOPE"])), "unknown fact 'F_NOPE'")


def test_unknown_stage(scenario):
    assert has(broken(scenario, lambda d: q(d).update(stages=["NOWHERE"])), "unknown stage 'NOWHERE'")


def test_results_stage_not_allowed(scenario):
    assert has(broken(scenario, lambda d: q(d).update(stages=["RESULTS"])), "RESULTS")


def test_character_does_not_know_fact(scenario):
    errs = broken(scenario, lambda d: q(d).update(fact_ids=["F_DEFECT"]))  # F_DEFECT знает только эксперт
    assert has(errs, "does not know fact 'F_DEFECT'")


def test_duplicate_question_id(scenario):
    def m(d):
        d["npc_questions"].append(copy.deepcopy(q(d)))

    assert has(broken(scenario, m), "duplicate npc question id 'plaintiff_defect'")


def test_text_keys_collected(scenario):
    keys = collect_text_keys(scenario)
    for item in scenario.npc_questions:
        assert {item.label_key, item.answer_key, item.keywords_key} <= keys
    assert "fact.defect_date" in keys
