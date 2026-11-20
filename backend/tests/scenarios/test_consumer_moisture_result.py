"""Результат дела consumer_moisture_001 в API-виде: result_kind, result_label, kind, counterfactual (без БД)."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app.game_engine import evaluate
from app.scenarios import load_scenario_dir
from app.services.presenter import build_result
from tests.scenarios.test_consumer_moisture import path, play

DIR = Path(__file__).resolve().parents[3] / "scenarios" / "consumer_moisture_001"
SID = uuid.UUID("00000000-0000-0000-0000-000000000002")

LABELS = {
    "ru": {
        "win": "Победа", "partial": "Частичная победа", "loss": "Поражение", "settlement": "Мировое соглашение",
        "procedural_loss": "Иск оставлен без рассмотрения",
    },
    "uz-Latn": {
        "win": "G'alaba", "partial": "Qisman g'alaba", "loss": "Mag'lubiyat", "settlement": "Kelishuv bitimi",
        "procedural_loss": "Da'vo ko'rilmasdan qoldirildi",
    },
}
CASES = {
    "win": {}, "partial": {"final": "refund_penalty"}, "loss": {"expertise": False},
    "settlement": {"settlement": "accept"}, "procedural_loss": {"poa": "poa_verbal"},
}


@pytest.fixture(scope="module")
def loaded():
    return load_scenario_dir(DIR)


def _result(loaded, locale, **kw):
    state, _ = play(loaded.scenario, path(**kw))
    return build_result(loaded, evaluate(loaded.scenario, state), SID, locale, [], 30)


@pytest.mark.parametrize("locale", ["ru", "uz-Latn", "uz-Cyrl"])
@pytest.mark.parametrize("kind", list(CASES))
def test_result_kind_and_label(loaded, locale, kind):
    res = _result(loaded, locale, **CASES[kind])
    assert res.result_kind == kind
    if locale != "uz-Cyrl":
        assert res.result_label == LABELS[locale][kind]
    else:
        assert res.result_label and not res.result_label.startswith("result.kind")  # кириллический перевод есть
    assert res.outcome_title and res.ruling_text


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
def test_counterfactual_only_when_not_best_and_kind_is_exposed(loaded, locale):
    best = _result(loaded, locale)
    assert all(d.counterfactual is None for d in best.decisions)
    assert {d.kind for d in best.decisions} == {"action", "reasoning", "prediction"}

    res = _result(loaded, locale, defendant="service", why_expertise="always", forecast="claim_granted")
    by = {d.decision_id: d for d in res.decisions}
    assert by["defendant"].counterfactual and by["why_expertise"].counterfactual
    assert by["why_expertise"].kind == "reasoning" and by["outcome_forecast"].kind == "prediction"
    assert by["motion_expertise"].counterfactual is None  # верный ход: «что если» не показываем
    assert by["outcome_forecast"].best == "claim_denied" and by["outcome_forecast"].best_label
    for d in res.decisions:
        assert not (d.counterfactual or "").startswith("cf.")
