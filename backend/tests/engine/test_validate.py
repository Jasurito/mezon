"""validate_scenario must catch each class of broken scenario."""

import copy

from app.game_engine import collect_citation_ids, collect_text_keys, validate_scenario
from app.schemas.scenario import Scenario


def broken(sc: Scenario, mutate) -> list[str]:
    data = copy.deepcopy(sc.model_dump(mode="json", by_alias=True))
    mutate(data)
    return validate_scenario(Scenario.model_validate(data))


def stage(data, sid):
    return next(s for s in data["stages"] if s["id"] == sid)


def action(data, aid):
    return next(a for s in data["stages"] for a in s["actions"] if a["id"] == aid)


def has(errors: list[str], text: str) -> bool:
    return any(text in e for e in errors)


def test_unreachable_stage(scenario):
    def m(d):
        d["stages"].insert(-1, {"id": "ORPHAN", "title_key": "stage.intro",
                                "transitions": [{"to": "RESULTS", "when": {"always": True}}]})
    assert has(broken(scenario, m), "'ORPHAN' is unreachable")


def test_dead_end_stage(scenario):
    def m(d):
        d["stages"].insert(-1, {"id": "TRAP", "title_key": "stage.intro"})
        action(d, "argue_warranty")["effects"].append({"goto": "TRAP"})
    errs = broken(scenario, m)
    assert has(errs, "'TRAP' cannot reach RESULTS")


def test_last_rule_not_always(scenario):
    def m(d):
        d["evaluation_rules"][-1]["when"] = {"flag": "x"}
    assert has(broken(scenario, m), "last evaluation rule")


def test_unknown_evidence(scenario):
    def m(d):
        action(d, "present_receipt")["evidence_id"] = "ghost"
    assert has(broken(scenario, m), "unknown evidence 'ghost'")


def test_add_evidence_unknown(scenario):
    def m(d):
        action(d, "request_expertise")["effects"].append({"add_evidence": "ghost"})
    assert has(broken(scenario, m), "add_evidence unknown evidence 'ghost'")


def test_goto_not_last(scenario):
    def m(d):
        action(d, "enter_courtroom")["effects"] = [{"goto": "CASE_REVIEW"}, {"set": "x"}]
    assert has(broken(scenario, m), "goto must be the last effect")


def test_citation_not_listed(scenario):
    def m(d):
        d["citations"].remove("TEST_CPC.art.2")
    assert has(broken(scenario, m), "citation 'TEST_CPC.art.2' is used but not listed")


def test_misc_references(scenario):
    def m(d):
        d["stages"][0]["transitions"][0]["to"] = "NOWHERE"
        d["decisions"][2]["best"] = "nothing"
        d["evaluation_rules"][0]["when"] = {"chose": {"decision_id": "final_claim", "option": "zzz"}}
        d["characters"].append(dict(d["characters"][0]))
        action(d, "ask_plaintiff_defect")["target_character"] = "nobody"
    errs = broken(scenario, m)
    for text in ("unknown stage 'NOWHERE'", "best 'nothing'", "unknown option 'zzz'",
                 "duplicate character id 'judge'", "unknown target_character 'nobody'"):
        assert has(errs, text), text


def test_results_must_be_terminal(scenario):
    def m(d):
        stage(d, "RESULTS")["actions"] = [action(d, "enter_courtroom")]
    assert has(broken(scenario, m), "RESULTS must have no actions")


def test_collectors(scenario):
    keys = collect_text_keys(scenario)
    assert "act.final_claim" in keys and "card.topic1" in keys
    cites = collect_citation_ids(scenario)
    assert cites == set(scenario.citations)


def test_outcome_best_needs_outcome_options_and_prediction_kind(scenario):
    def m(d):
        dp = d["decisions"][0]
        dp["best"] = "@outcome"
    errs = broken(scenario, m)
    assert has(errs, "is not an outcome id") and has(errs, "requires kind 'prediction'")


def test_outcome_score_needs_outcome_best(scenario):
    def m(d):
        d["decisions"][0]["outcome_score"] = 3
    assert has(broken(scenario, m), "outcome_score needs best @outcome")


def test_result_kind_defaults_from_outcome(scenario):
    kinds = {r.outcome: r.result_kind for r in scenario.evaluation_rules}
    assert kinds["claim_granted"] == "win" and kinds["claim_partially_granted"] == "partial"
    assert kinds["claim_denied"] == "loss"
