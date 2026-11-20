import pytest
from pydantic import ValidationError

from app.game_engine import validate_scenario
from app.schemas.scenario import Action, Condition, Effect, React, Say, Scenario


def test_fixture_loads_and_is_valid(scenario):
    assert scenario.scenario_id == "test_consumer"
    assert validate_scenario(scenario) == []


def test_typo_in_effect_key():
    with pytest.raises(ValidationError):
        Effect.model_validate({"scor": 5})


def test_typo_in_condition_key():
    with pytest.raises(ValidationError):
        Condition.model_validate({"flg": "x"})


def test_exactly_one_key():
    with pytest.raises(ValidationError):
        Effect.model_validate({"set": "a", "unset": "b"})
    with pytest.raises(ValidationError):
        Condition.model_validate({})


def test_typo_in_scenario_json(scenario):
    data = scenario.model_dump(by_alias=True)
    data["max_scor"] = 1
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


def test_say_short_forms():
    assert Say.model_validate(["judge", "line.x"]).emotion == "neutral"
    assert Say.model_validate(["judge", "line.x", "worried"]).emotion == "worried"
    eff = Effect.model_validate({"say": ["judge", "line.x"]})
    assert eff.say == Say(speaker="judge", text_key="line.x", emotion="neutral")


def test_react_short_form_and_bad_reaction():
    eff = Effect.model_validate({"react": ["judge", "nod"]})
    assert eff.react == React(character="judge", reaction="nod")
    with pytest.raises(ValidationError):
        Effect.model_validate({"react": ["judge", "dance"]})


def test_gte_forms():
    Condition.model_validate({"gte": {"var": "score", "value": 3}})
    Condition.model_validate({"gte": {"count": ["a", "b"], "value": 1}})
    with pytest.raises(ValidationError):
        Condition.model_validate({"gte": {"value": 1}})


def test_decision_action_requires_decision_id():
    with pytest.raises(ValidationError):
        Action.model_validate({"id": "a", "kind": "decision", "label_key": "k"})
