import json
import shutil

import pytest

from app.scenarios import ScenarioValidationError, load_all
from tests.engine.conftest import FIXTURES


def copy_fixtures(tmp_path):
    root = tmp_path / "scenarios"
    shutil.copytree(FIXTURES, root)
    return root, root / "test_consumer"


def edit_json(path, fn):
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_load_all_fixtures_ok():
    loaded = load_all(FIXTURES)
    item = loaded["test_consumer"]
    assert item.errors == []
    assert item.quiz is not None and len(item.quiz.pre) == 3 and len(item.quiz.post) == 3
    assert item.warnings  # uz-Cyrl texts are absent in the fixture


def test_missing_ru_key_is_error(tmp_path):
    root, d = copy_fixtures(tmp_path)
    edit_json(d / "texts.ru.json", lambda t: t.pop("act.final_claim"))
    with pytest.raises(ScenarioValidationError) as exc:
        load_all(root)
    assert any("act.final_claim" in e and "ru" in e for e in exc.value.errors)
    assert load_all(root, strict=False)["test_consumer"].errors


def test_missing_quiz_key_is_error(tmp_path):
    root, d = copy_fixtures(tmp_path)
    edit_json(d / "texts.uz-Latn.json", lambda t: t.pop("quiz.pre1.text"))
    with pytest.raises(ScenarioValidationError, match="quiz.pre1.text"):
        load_all(root)


def test_missing_cyrl_key_is_only_warning(tmp_path):
    root, d = copy_fixtures(tmp_path)
    shutil.copy(d / "texts.ru.json", d / "texts.uz-Cyrl.json")
    edit_json(d / "texts.uz-Cyrl.json", lambda t: t.pop("act.final_claim"))
    item = load_all(root)["test_consumer"]
    assert item.errors == []
    assert item.warnings == ["test_consumer: missing text key 'act.final_claim' in uz-Cyrl"]


def test_quiz_scenario_id_mismatch(tmp_path):
    root, d = copy_fixtures(tmp_path)
    edit_json(d / "quiz.json", lambda q: q.update(scenario_id="other"))
    with pytest.raises(ScenarioValidationError, match="quiz.scenario_id"):
        load_all(root)


def test_invalid_scenario_json_collected(tmp_path):
    root, d = copy_fixtures(tmp_path)
    edit_json(d / "scenario.json", lambda s: s.update(bogus=1))
    with pytest.raises(ScenarioValidationError):
        load_all(root)
    assert load_all(root, strict=False) == {}
