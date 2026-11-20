"""SCENARIOS_DIR с несколькими каталогами через os.pathsep."""

import os
import shutil
from contextlib import contextmanager

import pytest

from app.config import Settings
from app.scenarios import ScenarioValidationError
from app.scenarios.registry import load_from_roots, load_registry, scenario_roots
from tests.engine.conftest import FIXTURES


def _copy_as(tmp_path, folder: str, new_id: str | None):
    """Копия фикстуры test_consumer в tmp_path/folder (при new_id меняет scenario_id)."""
    import json

    root = tmp_path / folder
    shutil.copytree(FIXTURES / "test_consumer", root / "case")
    if new_id:
        for name in ("scenario.json", "quiz.json"):
            f = root / "case" / name
            data = json.loads(f.read_text(encoding="utf-8"))
            data["scenario_id"] = new_id
            f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return root


@contextmanager
def _no_db():
    raise RuntimeError("no db in this test")
    yield  # pragma: no cover


def test_scenario_roots_splits_by_pathsep(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    s = Settings(SCENARIOS_DIR=f"{a}{os.pathsep}{b}")
    assert scenario_roots(s) == [a, b]
    assert scenario_roots(Settings(SCENARIOS_DIR=str(a))) == [a]


def test_scenarios_from_several_roots_are_merged(tmp_path):
    a = _copy_as(tmp_path, "a", None)
    b = _copy_as(tmp_path, "b", "second_case")
    registry = load_from_roots([a, b, tmp_path / "missing"])
    assert set(registry) == {"test_consumer", "second_case"}


def test_duplicate_scenario_id_across_roots_is_error(tmp_path):
    a = _copy_as(tmp_path, "a", None)
    b = _copy_as(tmp_path, "b", None)
    with pytest.raises(ScenarioValidationError) as exc:
        load_from_roots([a, b])
    assert any("test_consumer" in e and "duplicate" in e for e in exc.value.errors)


def test_load_registry_uses_all_roots(tmp_path):
    a = _copy_as(tmp_path, "a", None)
    b = _copy_as(tmp_path, "b", "second_case")
    settings = Settings(SCENARIOS_DIR=f"{a}{os.pathsep}{b}", STRICT_CITATIONS=False)
    registry = load_registry(settings, _no_db)
    assert set(registry) == {"test_consumer", "second_case"}
