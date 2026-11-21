"""HTTP: /api/glossary и блок scoring в деталях дела; /result и события с новыми полями."""

import pytest

from tests.engine.test_score_explained import explained_dir
from tests.game.conftest import BEST, SCENARIO_ID, Api

pytestmark = pytest.mark.db

TERMS = {
    "motion", "expertise", "settlement", "burden_of_proof", "statement_of_claim", "defendant", "plaintiff",
    "power_of_attorney", "penalty", "moral_damage", "warranty_period", "claim_letter", "evidence",
    "claim_left_without_consideration", "unjust_enrichment",
}


@pytest.mark.parametrize("locale", ["ru", "uz-Latn", "uz-Cyrl"])
def test_glossary(api, locale):
    r = api.c.get("/api/glossary", params={"locale": locale})
    assert r.status_code == 200
    items = r.json()
    assert {i["id"] for i in items} == TERMS
    for i in items:
        assert i["term"] and i["definition"] and i["aliases"]
        assert i["term"] != i["id"]
    if locale == "uz-Cyrl":
        assert not any(c in "".join(i["term"] + i["definition"] for i in items) for c in "abdgqxz")
    if locale == "ru":
        assert next(i for i in items if i["id"] == "defendant")["term"] == "ответчик"
    assert "reference" in api.c.get("/openapi.json").json()["paths"]["/api/glossary"]["get"]["tags"]


def test_scenario_detail_has_scoring(api):
    d = api.c.get(f"/api/scenarios/{SCENARIO_ID}", params={"locale": "uz-Latn"}).json()
    sc = d["scoring"]
    assert sc["max_score"] == 100
    assert [s["skill"] for s in sc["skills"]] == ["procedure", "evidence", "substantive_law", "remedy_choice"]
    assert sc["skills"][0]["label"] == "Protsedura" and sc["skills"][0]["description"]
    assert [o["result_kind"] for o in sc["outcomes"]] == ["win", "partial", "loss"]


def test_result_and_events_with_new_fields(make_client, tmp_path):
    root, _ = explained_dir(tmp_path)
    with make_client(scenarios_dir=root) as c:
        api = Api(c)
        start = api.start(api.user())
        sid = start["session_id"]
        assert start["stage_goal"] is None
        states = api.play(sid, BEST)
        reasons = [e["reason"] for s in states for e in s["events"] if e["type"] == "score"]
        assert "суд видит факт покупки" in reasons and None in reasons
        res = c.get(f"/api/sessions/{sid}/result").json()
        by = {s["skill"]: s for s in res["skills"]}
        assert by["substantive_law"]["percent"] == 100 and by["evidence"]["percent"] is None
        assert res["main_mistake"] is None
        mid = api.start(api.user())
        sid2 = mid["session_id"]
        api.play(sid2, BEST[:-1])
        st = c.get(f"/api/sessions/{sid2}").json()
        assert st["stage"] == "DECISION" and st["stage_goal"] == "Выберите требование"
