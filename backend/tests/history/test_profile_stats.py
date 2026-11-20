"""Профиль, user_stats и список игр пользователя (Postgres)."""

import uuid

import pytest

from tests.history.conftest import BEST, LOSS, PARTIAL, Api, post_quiz

pytestmark = pytest.mark.db


def stats(c, uid):
    r = c.get(f"/api/users/{uid}")
    assert r.status_code == 200, r.text
    return r.json()["stats"]


# --------------------------------------------------------------------------- профиль


def test_profile_get_patch(hclient):
    with hclient() as c:
        api = Api(c)
        uid = api.user()
        r = c.get(f"/api/users/{uid}")
        assert r.status_code == 200
        body = r.json()
        assert body["user_id"] == uid and body["display_name"] == "Азиз"
        assert body["preferred_locale"] is None and body["created_at"]
        assert body["stats"] == {
            "sessions_started": 0, "sessions_finished": 0, "total_score": 0, "best_score": 0,
            "total_time_sec": 0, "quizzes_taken": 0, "last_active_at": None, "active_days": 0, "streak_days": 0,
        }

        r = c.patch(f"/api/users/{uid}", json={"preferred_locale": "uz-Latn"})
        assert r.status_code == 200 and r.json()["preferred_locale"] == "uz-Latn"
        assert r.json()["display_name"] == "Азиз"
        r = c.patch(f"/api/users/{uid}", json={"display_name": "Зарина"})
        assert r.json()["display_name"] == "Зарина" and r.json()["preferred_locale"] == "uz-Latn"
        r = c.patch(f"/api/users/{uid}", json={"preferred_locale": None, "display_name": None})
        assert r.json()["preferred_locale"] is None and r.json()["display_name"] is None
        assert c.get(f"/api/users/{uid}").json()["preferred_locale"] is None


def test_profile_404_and_validation(hclient):
    with hclient() as c:
        ghost = uuid.uuid4()
        for url in (f"/api/users/{ghost}", f"/api/users/{ghost}/sessions", f"/api/users/{ghost}/activity"):
            r = c.get(url)
            assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND", url
        assert c.patch(f"/api/users/{ghost}", json={"display_name": "x"}).status_code == 404
        uid = Api(c).user()
        assert c.patch(f"/api/users/{uid}", json={"preferred_locale": "en"}).status_code == 422
        assert c.get(f"/api/users/{uid}/sessions", params={"locale": "en"}).status_code == 422
        assert c.get(f"/api/users/{uid}/sessions", params={"status": "weird"}).status_code == 422


# --------------------------------------------------------------------------- user_stats


def test_stats_after_three_playthroughs_and_quiz(hclient):
    with hclient() as c:
        api = Api(c)
        uid = api.user()
        scores, secs = [], 0
        for path in (BEST, PARTIAL, LOSS):
            sid = api.start(uid)["session_id"]
            last = api.play(sid, path)[-1]
            assert last["finished"]
            scores.append(last["score"])
            secs += 5 * len(path)
        post_quiz(c, uid, "pre")
        post_quiz(c, uid, "post", {"post1": "a", "post2": "a", "post3": "b"})

        s = stats(c, uid)
        assert s["sessions_started"] == 3 and s["sessions_finished"] == 3
        assert s["total_score"] == sum(scores) and s["best_score"] == max(scores)
        assert len(set(scores)) == 3 and scores[0] == max(scores)
        assert s["total_time_sec"] == secs
        assert s["quizzes_taken"] == 2
        assert s["active_days"] == 1 and s["streak_days"] == 1 and s["last_active_at"]


def test_stats_unfinished_session_counts_only_started(hclient):
    with hclient() as c:
        api = Api(c)
        uid = api.user()
        sid = api.start(uid)["session_id"]
        api.play(sid, BEST[:3])
        s = stats(c, uid)
        assert s["sessions_started"] == 1 and s["sessions_finished"] == 0
        assert s["total_score"] == 0 and s["total_time_sec"] == 0


def test_streak_by_utc_days(hclient, settable_clock):
    with hclient(now=settable_clock) as c:
        api = Api(c)
        uid = api.user()

        def touch(clock_):
            settable_clock.t = clock_
            api.start(uid)
            return stats(c, uid)

        from datetime import UTC, datetime

        s = touch(datetime(2026, 11, 20, 12, 0, tzinfo=UTC))
        assert (s["active_days"], s["streak_days"]) == (1, 1)
        s = touch(datetime(2026, 11, 20, 23, 59, tzinfo=UTC))  # тот же день
        assert (s["active_days"], s["streak_days"]) == (1, 1)
        s = touch(datetime(2026, 11, 21, 0, 1, tzinfo=UTC))  # вчера -> +1 (граница полуночи UTC)
        assert (s["active_days"], s["streak_days"]) == (2, 2)
        s = touch(datetime(2026, 11, 21, 18, 0, tzinfo=UTC))  # сегодня: без изменений
        assert (s["active_days"], s["streak_days"]) == (2, 2)
        s = touch(datetime(2026, 11, 22, 8, 0, tzinfo=UTC))
        assert (s["active_days"], s["streak_days"]) == (3, 3)
        s = touch(datetime(2026, 11, 25, 8, 0, tzinfo=UTC))  # разрыв -> 1
        assert (s["active_days"], s["streak_days"]) == (4, 1)
        assert s["sessions_started"] == 6


# --------------------------------------------------------------------------- /users/{id}/sessions


def test_user_sessions_list(hclient):
    with hclient() as c:
        api = Api(c)
        uid = api.user()
        other = api.user()
        sids = []
        for path in (BEST, PARTIAL, LOSS[:4]):  # третья не завершена
            sid = api.start(uid)["session_id"]
            api.play(sid, path)
            sids.append(sid)
        api.start(other)

        r = c.get(f"/api/users/{uid}/sessions")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["total"] == 3 and body["limit"] == 20 and body["offset"] == 0
        assert [i["session_id"] for i in body["items"]] == sids[::-1]  # новые сверху
        active, partial, best = body["items"]
        assert active["finished_at"] is None and active["outcome"] is None and active["score"] is None
        assert active["outcome_title"] is None and active["steps"] == 4
        assert best["steps"] == len(BEST) and best["outcome"] and best["outcome_title"]
        assert best["score"] is not None and best["max_score"] and best["title"]
        assert best["scenario_id"] == "test_consumer" and partial["score"] < best["score"]

        fin = c.get(f"/api/users/{uid}/sessions", params={"status": "finished"}).json()
        assert fin["total"] == 2 and [i["session_id"] for i in fin["items"]] == [sids[1], sids[0]]
        act = c.get(f"/api/users/{uid}/sessions", params={"status": "active"}).json()
        assert act["total"] == 1 and act["items"][0]["session_id"] == sids[2]

        p1 = c.get(f"/api/users/{uid}/sessions", params={"limit": 2}).json()
        p2 = c.get(f"/api/users/{uid}/sessions", params={"limit": 2, "offset": 2}).json()
        assert p1["total"] == p2["total"] == 3
        assert [i["session_id"] for i in p1["items"] + p2["items"]] == sids[::-1]
        assert len(p2["items"]) == 1

        uz = c.get(f"/api/users/{uid}/sessions", params={"locale": "uz-Latn"}).json()["items"][-1]
        assert uz["title"] != best["title"]
