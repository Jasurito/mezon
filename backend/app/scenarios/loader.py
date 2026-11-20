"""Load scenarios from disk and run static checks (no database access)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import ValidationError

from app.game_engine.validate import collect_text_keys, iter_text_keys, validate_scenario
from app.schemas.quiz import Quiz
from app.schemas.scenario import Scenario

LOCALES = ("ru", "uz-Latn", "uz-Cyrl")
REQUIRED_LOCALES = ("ru", "uz-Latn")


class ScenarioValidationError(Exception):
    """Raised by load_all(strict=True) with every error of every scenario."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("scenario validation failed:\n" + "\n".join(errors))
        self.errors = errors


@dataclass
class LoadedScenario:
    scenario: Scenario
    texts: dict[str, dict[str, str]]
    quiz: Quiz | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_scenario_dir(path: Path) -> LoadedScenario:
    """Read scenario.json, texts.<locale>.json and quiz.json from a directory."""
    scenario = Scenario.model_validate(_read_json(path / "scenario.json"))
    texts: dict[str, dict[str, str]] = {}
    for loc in LOCALES:
        f = path / f"texts.{loc}.json"
        texts[loc] = _read_json(f) if f.exists() else {}
    quiz_file = path / "quiz.json"
    quiz = Quiz.model_validate(_read_json(quiz_file)) if quiz_file.exists() else None

    errors = [f"{scenario.scenario_id}: {e}" for e in validate_scenario(scenario)]
    keys = collect_text_keys(scenario)
    if quiz is not None:
        keys |= set(iter_text_keys(quiz.model_dump(mode="json")))
        if quiz.scenario_id != scenario.scenario_id:
            errors.append(
                f"{scenario.scenario_id}: quiz.scenario_id is '{quiz.scenario_id}'"
            )
    warnings: list[str] = []
    for loc in LOCALES:
        for key in sorted(k for k in keys if not texts[loc].get(k)):
            msg = f"{scenario.scenario_id}: missing text key '{key}' in {loc}"
            (errors if loc in REQUIRED_LOCALES else warnings).append(msg)
    return LoadedScenario(scenario, texts, quiz, errors, warnings)


def load_all(root: Path, strict: bool = True) -> dict[str, LoadedScenario]:
    """Load every subfolder of `root` that has scenario.json.

    strict=True raises ScenarioValidationError listing all errors; otherwise
    scenarios with errors are returned with `errors` filled and unparseable ones are skipped.
    """
    loaded: dict[str, LoadedScenario] = {}
    errors: list[str] = []
    for d in sorted(p for p in root.iterdir() if (p / "scenario.json").is_file()):
        try:
            item = load_scenario_dir(d)
        except (ValidationError, json.JSONDecodeError) as exc:
            errors.append(f"{d.name}: cannot parse: {exc}")
            continue
        loaded[item.scenario.scenario_id] = item
        errors += item.errors
    if strict and errors:
        raise ScenarioValidationError(errors)
    return loaded
