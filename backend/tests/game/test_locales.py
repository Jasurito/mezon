"""Ни один текст ответа не равен своему ключу (всё переведено) на ru и uz-Latn."""

import re

import pytest

from app.game_engine import collect_text_keys
from app.scenarios import load_scenario_dir
from tests.game.conftest import BEST, SCENARIO_ID, SCENARIOS_FIXTURES

pytestmark = pytest.mark.db

KEY_LIKE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")
TEXT_FIELDS = {
    "label", "text", "title", "stage_title", "story", "name", "role", "fictional_notice", "category",
    "topics", "explanation", "correct_action", "chosen_label", "best_label", "outcome_title",
    "ruling_text", "topic", "disclaimer",
}


def _texts(node, key=None):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "citations":  # текст закона не переводится
                continue
            yield from _texts(v, k)
    elif isinstance(node, list):
        for v in node:
            yield from _texts(v, key)
    elif isinstance(node, str) and key in TEXT_FIELDS:
        yield node


def _check(payload, keys):
    found = list(_texts(payload))
    assert found
    for s in found:
        assert s.strip(), payload
        assert s not in keys and not KEY_LIKE.match(s), f"untranslated: {s!r}"


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
def test_everything_translated(api, locale):
    keys = collect_text_keys(load_scenario_dir(SCENARIOS_FIXTURES / "test_consumer").scenario)
    _check(api.c.get("/api/scenarios", params={"locale": locale}).json(), keys)
    _check(api.c.get(f"/api/scenarios/{SCENARIO_ID}", params={"locale": locale}).json(), keys)

    uid = api.user()
    start = api.start(uid, locale)
    sid = start["session_id"]
    assert start["locale"] == locale
    _check(start, keys)
    for state in api.play(sid, BEST):
        _check(state, keys)
    res = api.c.get(f"/api/sessions/{sid}/result").json()
    _check(res, keys)


def test_uz_cyrl_falls_back(api):
    uid = api.user()
    state = api.start(uid, "uz-Cyrl")
    assert state["locale"] == "uz-Cyrl"
    assert state["stage_title"] and not KEY_LIKE.match(state["stage_title"])
    sid = state["session_id"]
    api.play(sid, BEST)
    res = api.c.get(f"/api/sessions/{sid}/result").json()
    assert "Ўқув" in res["disclaimer"] or "ўқув" in res["disclaimer"].lower()
