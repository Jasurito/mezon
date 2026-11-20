import pytest

from tests.game.conftest import BEST, PARTIAL

pytestmark = pytest.mark.db

SID = "test_consumer"
MISTAKES = {"procedure": 1}  # BEST: одна ошибка процедуры; PARTIAL без ошибок
MISTAKES = {"procedure": 1}  # BEST: одна ошибка процедуры; PARTIAL без ошибок
URL = f"/api/analytics/scenarios/{SID}/summary"


def test_empty_scenario_gives_zeros(game_client):
    r = game_client.get(URL)
    assert r.status_code == 200, r.text
    assert r.json() == {
        "sessions_started": 0, "completion_rate": None, "avg_score": None, "correct_decision_rate": None,
        "avg_time_sec": None, "avg_learning_gain": None, "mistakes_by_category": {},
        "note": "Предварительные данные, малая выборка",
    }


def test_summary_after_sessions(api, game_client):
    u = api.user()
    api.play(api.start(u)["session_id"], BEST)
    api.play(api.start(u)["session_id"], PARTIAL)
    api.start(u)  # не завершена

    body = game_client.get(URL).json()
    assert body["sessions_started"] == 3
    assert body["completion_rate"] == 0.67
    assert body["avg_score"] == 70  # (100 + 40) / 2
    assert body["correct_decision_rate"] == 0.67  # (1.0 + 1/3) / 2
    assert isinstance(body["avg_time_sec"], int) and body["avg_time_sec"] > 0
    assert body["avg_learning_gain"] is None
    assert body["mistakes_by_category"] == MISTAKES


def test_summary_learning_gain_and_locale(api, game_client):
    u = api.user()
    q = f"/api/quiz/{SID}/attempts"
    game_client.post(q, json={"user_id": u, "kind": "pre", "answers": {"pre1": "b"}})
    game_client.post(q, json={"user_id": u, "kind": "post", "answers": {"post1": "a", "post2": "a", "post3": "b"}})
    body = game_client.get(URL, params={"locale": "uz-Latn"}).json()
    assert body["avg_learning_gain"] == 2.0
    assert body["note"] == "Dastlabki ma'lumotlar, tanlanma kichik"


def test_summary_404(game_client):
    r = game_client.get("/api/analytics/scenarios/nope/summary")
    assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"

