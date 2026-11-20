"""История в MongoDB: живая запись, идемпотентность, деградация без Mongo, /history и /activity, backfill."""

import logging
from datetime import datetime

import pytest

from app.history.backfill import backfill
from app.history.mongo import MongoHistoryStore
from app.history.store import InMemoryHistoryStore, NullHistoryStore
from tests.history.conftest import BEST, LOSS, PARTIAL, Api, post_quiz

pytestmark = pytest.mark.db

ALL_TYPES = {"session_started", "session_finished", "quiz_attempt", "screen_view", "npc_question", "mentor_question"}


def play_everything(c, api: Api) -> dict:
    """Две игры (BEST завершена, PARTIAL не дойдена), квиз, клиентское событие, вопросы NPC и наставнику."""
    uid = api.user()
    s1 = api.start(uid)["session_id"]
    api.play(s1, BEST)
    s2 = api.start(uid)["session_id"]
    api.play(s2, PARTIAL[:7])
    post_quiz(c, uid, "pre")
    r = c.post("/api/events", json={
        "user_id": uid, "session_id": s2, "events": [{"type": "screen_view", "payload": {"screen": "case"}}]})
    assert r.status_code == 202 and r.json()["accepted"] == 1
    r = c.post(f"/api/sessions/{s2}/npc/plaintiff/ask", json={"text": "Когда вы обнаружили недостаток?"})
    assert r.status_code == 200, r.text
    r = c.post("/api/mentor/ask", json={"question": "Можно ли вернуть товар с недостатком?", "locale": "ru", "session_id": s2})
    assert r.status_code == 200 and "event: done" in r.text
    return {"user": uid, "done": s1, "open": s2}


def mongo_docs(store: MongoHistoryStore):
    sessions = {d["_id"]: d for d in store.sessions.find()}
    activity = {d["_id"]: d for d in store.activity.find()}
    return sessions, activity


# --------------------------------------------------------------------------- Mongo вживую


def test_live_session_document_grows_and_finishes(hclient, mongo_store):
    with hclient(mongo_store) as c:
        api = Api(c)
        uid = api.user()
        sid = api.start(uid)["session_id"]
        doc = mongo_store.get_session(sid)
        assert doc["_id"] == sid and doc["user_id"] == uid and doc["scenario_id"] == "test_consumer"
        assert doc["finished_at"] is None and doc["outcome"] is None and doc["score"] is None
        assert [s["seq"] for s in doc["steps"]] == [0]
        s0 = doc["steps"][0]
        assert s0["action_id"] is None and s0["stage_before"] is None and s0["events"]
        assert {"type", "text_key", "speaker"} <= set(s0["events"][0]) or s0["events"][0]["type"] == "stage_changed"

        api.play(sid, BEST[:3])
        doc = mongo_store.get_session(sid)
        assert [s["seq"] for s in doc["steps"]] == [0, 1, 2, 3]
        assert doc["steps"][1]["action_id"] == BEST[0][0]
        assert doc["steps"][1]["stage_before"] == s0["stage_after"]
        assert doc["finished_at"] is None

        states = api.play(sid, BEST[3:])
        doc = mongo_store.get_session(sid)
        assert [s["seq"] for s in doc["steps"]] == list(range(len(BEST) + 1))
        assert doc["steps"][-1]["params"] == {"option": "refund"}
        assert doc["finished_at"] is not None and doc["outcome"]
        assert doc["score"] == states[-1]["score"] == doc["steps"][-1]["score_after"]
        assert doc["max_score"] == states[-1]["max_score"]


def test_push_step_is_idempotent(hclient, mongo_store):
    with hclient(mongo_store) as c:
        api = Api(c)
        sid = api.start(api.user())["session_id"]
        api.play(sid, BEST[:2])
        doc = mongo_store.get_session(sid)
        mongo_store.push_step(sid, doc["steps"][2])
        mongo_store.push_step(sid, doc["steps"][1])
        assert [s["seq"] for s in mongo_store.get_session(sid)["steps"]] == [0, 1, 2]


def test_activity_has_all_types(hclient, mongo_store):
    with hclient(mongo_store) as c:
        ids = play_everything(c, Api(c))
        r = c.get(f"/api/users/{ids['user']}/activity")
        assert r.status_code == 200
        body = r.json()
        assert body["available"] is True
        assert {i["type"] for i in body["items"]} == ALL_TYPES
        ts = [i["ts"] for i in body["items"]]
        assert ts == sorted(ts, reverse=True)
        fin = next(i for i in body["items"] if i["type"] == "session_finished")
        assert fin["session_id"] == ids["done"] and fin["payload"]["outcome"]

        # курсорная пагинация
        p1 = c.get(f"/api/users/{ids['user']}/activity", params={"limit": 3}).json()
        assert len(p1["items"]) == 3 and p1["next_before"]
        p2 = c.get(f"/api/users/{ids['user']}/activity", params={"limit": 50, "before": p1["next_before"]}).json()
        assert len(p1["items"]) + len(p2["items"]) == len(body["items"])
        assert p2["next_before"] is None
        assert all(datetime.fromisoformat(i["ts"]) < datetime.fromisoformat(p1["next_before"]) for i in p2["items"])


def test_history_endpoint_mongo_matches_postgres(hclient, mongo_store):
    with hclient(mongo_store) as c, hclient(NullHistoryStore()) as c_pg:
        api = Api(c)
        ids = play_everything(c, api)
        for sid in (ids["done"], ids["open"]):
            m = c.get(f"/api/sessions/{sid}/history")
            p = c_pg.get(f"/api/sessions/{sid}/history")
            assert m.status_code == p.status_code == 200, (m.text, p.text)
            mj, pj = m.json(), p.json()
            assert mj["source"] == "mongo" and pj["source"] == "postgres"
            mj.pop("source"), pj.pop("source")
            # Mongo хранит время с точностью до миллисекунд
            for body in (mj, pj):
                for st in body["steps"]:
                    st["ts"] = st["ts"][:19]
                body["started_at"] = body["started_at"][:19]
                body["finished_at"] = (body["finished_at"] or "")[:19]
            assert mj == pj
        done = c.get(f"/api/sessions/{ids['done']}/history").json()
        assert done["outcome"] and done["outcome_title"] and done["score"] is not None
        assert len(done["steps"]) == len(BEST) + 1
        assert done["steps"][0]["events"] and done["steps"][0]["events"][0]["type"] in {"say", "stage_changed"}
        assert any(e["type"] == "say" and e["text"] for s in done["steps"] for e in s["events"])
        uz = c.get(f"/api/sessions/{ids['done']}/history", params={"locale": "uz-Latn"}).json()
        assert uz["locale"] == "uz-Latn"
        assert c.get("/api/sessions/00000000-0000-0000-0000-000000000000/history").status_code == 404


def test_history_falls_back_when_mongo_document_is_stale(hclient, mongo_store):
    with hclient(mongo_store) as c:
        api = Api(c)
        sid = api.start(api.user())["session_id"]
        api.play(sid, BEST[:3])
        mongo_store.sessions.update_one({"_id": sid}, {"$pop": {"steps": 1}})  # потерян последний шаг
        body = c.get(f"/api/sessions/{sid}/history").json()
        assert body["source"] == "postgres" and len(body["steps"]) == 4
        mongo_store.sessions.delete_one({"_id": sid})
        assert c.get(f"/api/sessions/{sid}/history").json()["source"] == "postgres"


# --------------------------------------------------------------------------- Mongo недоступна


def test_unreachable_mongo_does_not_break_game(hclient, caplog):
    dead = MongoHistoryStore("mongodb://127.0.0.1:1", "adolat_test", timeout_ms=200)
    try:
        with hclient(dead) as c, caplog.at_level(logging.WARNING, logger="adolat.history"):
            api = Api(c)
            ids = play_everything(c, api)
            assert api.c.get(f"/api/sessions/{ids['done']}/result").status_code == 200
            assert c.get(f"/api/users/{ids['user']}").json()["stats"]["sessions_finished"] == 1

            h = c.get(f"/api/sessions/{ids['done']}/history")
            assert h.status_code == 200 and h.json()["source"] == "postgres"
            assert len(h.json()["steps"]) == len(BEST) + 1
            a = c.get(f"/api/users/{ids['user']}/activity")
            assert a.status_code == 200 and a.json() == {"items": [], "next_before": None, "available": False}
        assert any("MongoDB" in r.getMessage() for r in caplog.records)
    finally:
        dead.close()


def test_null_store_history_from_postgres(hclient):
    with hclient(NullHistoryStore()) as c:
        api = Api(c)
        uid = api.user()
        sid = api.start(uid)["session_id"]
        api.play(sid, LOSS)
        h = c.get(f"/api/sessions/{sid}/history").json()
        assert h["source"] == "postgres" and h["outcome"] and len(h["steps"]) == len(LOSS) + 1
        assert c.get(f"/api/users/{uid}/activity").json()["available"] is False


def test_inmemory_store_works_without_mongo(hclient):
    store = InMemoryHistoryStore()
    with hclient(store) as c:
        api = Api(c)
        ids = play_everything(c, api)
        assert c.get(f"/api/sessions/{ids['done']}/history").json()["source"] == "mongo"
        assert {a["type"] for a in store.activity.values()} == ALL_TYPES


# --------------------------------------------------------------------------- backfill


def _snapshot_mongo(store: MongoHistoryStore):
    return mongo_docs(store)


def test_backfill_rebuilds_mongo(hclient, mongo_store, seeded_db):
    with hclient(mongo_store) as c:
        ids = play_everything(c, Api(c))
        registry = c.app.state.scenarios
        live_sessions, live_activity = mongo_docs(mongo_store)
        assert len(live_sessions) == 2 and len(live_activity) >= 6

        mongo_store.sessions.delete_many({})
        mongo_store.activity.delete_many({})
        res = backfill(seeded_db, registry, mongo_store)
        assert res.sessions == 2 and res.sessions_skipped == 0
        b_sessions, b_activity = mongo_docs(mongo_store)
        assert b_sessions == live_sessions
        assert set(b_activity) == set(live_activity)
        assert b_activity == live_activity

        backfill(seeded_db, registry, mongo_store)  # повтор не дублирует
        again_sessions, again_activity = mongo_docs(mongo_store)
        assert again_sessions == live_sessions and again_activity == live_activity

        # --user: только этот пользователь
        mongo_store.sessions.delete_many({})
        import uuid

        res = backfill(seeded_db, registry, mongo_store, uuid.UUID(ids["user"]))
        assert res.sessions == 2
        res = backfill(seeded_db, registry, mongo_store, uuid.uuid4())
        assert res.sessions == 0 and res.activity == 0


def test_backfill_fills_gaps_next_to_live_records(hclient, mongo_store, seeded_db):
    """Backfill поверх частично записанной истории: живые записи не дублируются."""
    with hclient(mongo_store) as c:
        play_everything(c, Api(c))
        live_sessions, live_activity = mongo_docs(mongo_store)
        victim = next(iter(live_sessions))
        mongo_store.sessions.update_one({"_id": victim}, {"$pop": {"steps": 1}})
        mongo_store.activity.delete_one({"_id": next(iter(live_activity))})
        backfill(seeded_db, c.app.state.scenarios, mongo_store)
        sessions, activity = mongo_docs(mongo_store)
        assert sessions == live_sessions and activity == live_activity


def test_backfill_inmemory(hclient, seeded_db):
    store = InMemoryHistoryStore()
    with hclient(store) as c:
        play_everything(c, Api(c))
        live_s, live_a = dict(store.sessions), dict(store.activity)
        store.sessions.clear()
        store.activity.clear()
        backfill(seeded_db, c.app.state.scenarios, store)
        assert store.sessions == live_s and store.activity == live_a
