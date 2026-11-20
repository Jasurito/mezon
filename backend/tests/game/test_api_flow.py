"""Полный проход игры через HTTP по трём эталонным путям."""

import uuid

import pytest
from sqlalchemy import text

from tests.game.conftest import BEST, LOSS, PARTIAL, SCENARIO_ID

pytestmark = pytest.mark.db

KINDS = {"claim_granted": "win", "claim_partially_granted": "partial", "claim_denied": "loss"}
LABELS_RU = {"win": "Победа", "partial": "Частичная победа", "loss": "Поражение"}
LABELS_UZ = {"win": "G'alaba", "partial": "Qisman g'alaba", "loss": "Mag'lubiyat"}

CASES = [
    ("best", BEST, "claim_granted", 100),
    ("partial", PARTIAL, "claim_partially_granted", 40),
    ("loss", LOSS, "claim_denied", 4),
]


@pytest.mark.parametrize("name,path,outcome,score", CASES, ids=[c[0] for c in CASES])
def test_golden_path_via_api(api, seeded_db, name, path, outcome, score):
    uid = api.user()
    start = api.start(uid)
    sid = start["session_id"]
    assert start["stage"] == "INTRO" and start["stage_index"] == 1
    assert start["finished"] is False and start["events"]

    states = api.play(sid, path)
    last = states[-1]
    assert last["finished"] is True and last["stage"] == "RESULTS"
    assert last["available_actions"] == []
    assert last["score"] == score

    r = api.c.get(f"/api/sessions/{sid}/result")
    assert r.status_code == 200
    res = r.json()
    assert res["outcome"] == outcome and res["score"] == score and res["max_score"] == 100
    assert res["outcome_title"] and res["ruling_text"] and res["disclaimer"]
    # старый сценарий без новых полей: вид исхода выводится из id исхода, разбор остаётся прежним
    assert res["result_kind"] == KINDS[outcome] and res["result_label"] == LABELS_RU[KINDS[outcome]]
    assert all(d["kind"] == "action" and d["counterfactual"] is None for d in res["decisions"])
    assert res["time_spent_sec"] > 0
    assert res["citations"], "citations must not be empty"
    assert all(c["source_url"] for c in res["citations"])
    assert {c["citation_id"] for c in res["citations"]} >= {
        cid for d in res["decisions"] for cid in d["citation_ids"]
    }
    assert [d["decision_id"] for d in res["decisions"]]
    for d in res["decisions"]:
        assert d["chosen_label"] and d["best_label"] and d["explanation"]
    if name == "best":
        assert res["mistakes"] == [] and res["correct_decision_rate"] == 1.0
    else:
        assert res["mistakes"]
        for m in res["mistakes"]:
            assert m["title"] and m["explanation"]

    row = seeded_db.execute(
        text("SELECT outcome, score, finished_at, scenario_version FROM sessions WHERE id = :i"),
        {"i": sid},
    ).one()
    assert row.outcome == outcome and row.score == score and row.finished_at is not None
    assert row.scenario_version == "0.1.0"

    counts = dict(
        seeded_db.execute(
            text("SELECT type, count(*) FROM events WHERE session_id = :i GROUP BY type"), {"i": sid}
        ).all()
    )
    assert counts["session_started"] == 1
    assert counts["action"] == len(path)
    assert counts["session_finished"] == 1
    assert (counts.get("mistake", 0) > 0) == (name != "best")
    assert seeded_db.execute(
        text("SELECT count(*) FROM session_actions WHERE session_id = :i"), {"i": sid}
    ).scalar_one() == len(path)
    if name != "best":
        n = seeded_db.execute(
            text("SELECT count(*) FROM v_mistakes WHERE session_id = :i"), {"i": sid}
        ).scalar_one()
        assert n == counts["mistake"] == len(res["mistakes"])


def test_users_and_scenarios(api):
    r = api.c.post("/api/users", json={})
    assert r.status_code == 201
    uuid.UUID(r.json()["user_id"])
    assert r.json()["display_name"] is None
    assert api.c.post("/api/users").status_code == 201

    cards = api.c.get("/api/scenarios", params={"locale": "uz-Latn"}).json()
    assert [c["scenario_id"] for c in cards] == [SCENARIO_ID]
    assert cards[0]["available"] is True and cards[0]["title"] and cards[0]["fictional_notice"]
    assert api.c.get("/api/scenarios", params={"locale": "de"}).status_code == 422

    d = api.c.get(f"/api/scenarios/{SCENARIO_ID}").json()
    assert d["story"] and d["player_role"]["character_id"] == "plaintiff_rep"
    assert {c["id"] for c in d["characters"]} >= {"judge", "plaintiff_rep"}
    assert [x["side"] for x in d["claims"]] == ["plaintiff", "defendant"]
    assert {x["id"] for x in d["documents"]} >= {"contract", "receipt"}
    assert [a["document_key"] for a in d["legal_acts"]] == ["TEST_CPRL", "TEST_CC", "TEST_CPC"]
    assert d["legal_date"] == "2026-03-01"


def test_openapi_has_game_endpoints(api):
    spec = api.c.get("/openapi.json").json()
    paths = spec["paths"]
    for p, m in [
        ("/api/users", "post"),
        ("/api/scenarios", "get"),
        ("/api/scenarios/{scenario_id}", "get"),
        ("/api/sessions", "post"),
        ("/api/sessions/{session_id}", "get"),
        ("/api/sessions/{session_id}", "patch"),
        ("/api/sessions/{session_id}/actions", "post"),
        ("/api/sessions/{session_id}/result", "get"),
    ]:
        assert m in paths[p], (p, m)
        ok = next(c for c in paths[p][m]["responses"] if c.startswith("2"))
        assert paths[p][m]["responses"][ok]["content"]["application/json"]["schema"]


@pytest.mark.parametrize("locale", ["ru", "uz-Latn"])
def test_result_label_is_localized(api, seeded_db, locale):
    start = api.start(api.user(), locale)
    api.play(start["session_id"], BEST)
    res = api.c.get(f"/api/sessions/{start['session_id']}/result").json()
    expected = (LABELS_RU if locale == "ru" else LABELS_UZ)["win"]
    assert res["result_kind"] == "win" and res["result_label"] == expected
