import uuid

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.db

SID = "test_consumer"
PRE_OK = {"pre1": "b", "pre2": "a", "pre3": "b"}
POST_OK = {"post1": "a", "post2": "a", "post3": "b"}


def test_get_quiz_has_no_correct_answers(game_client):
    for kind, qid in (("pre", "pre1"), ("post", "post1")):
        r = game_client.get(f"/api/quiz/{SID}", params={"kind": kind})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["scenario_id"] == SID and body["kind"] == kind
        assert body["total"] == len(body["questions"]) == 3
        assert body["questions"][0]["question_id"] == qid
        assert body["questions"][0]["options"][0] == {"id": "a", **{"text": body["questions"][0]["options"][0]["text"]}}
        raw = r.text
        assert "correct" not in raw and "explanation" not in raw and "citation" not in raw


def test_get_quiz_locale(game_client):
    ru = game_client.get(f"/api/quiz/{SID}", params={"kind": "pre"}).json()
    uz = game_client.get(f"/api/quiz/{SID}", params={"kind": "pre", "locale": "uz-Latn"}).json()
    assert ru["questions"][0]["text"] != uz["questions"][0]["text"]


def test_get_quiz_404_and_validation(game_client):
    r = game_client.get("/api/quiz/nope", params={"kind": "pre"})
    assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"
    assert game_client.get(f"/api/quiz/{SID}", params={"kind": "mid"}).status_code == 422


def test_post_pre_scores_and_reviews(api, game_client, seeded_db):
    u = api.user()
    answers = {"pre1": "a", "pre2": "a"}  # pre1 неверно, pre2 верно, pre3 не отвечен
    r = game_client.post(f"/api/quiz/{SID}/attempts", json={"user_id": u, "kind": "pre", "answers": answers})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["score"] == 1 and body["max"] == 3
    assert body["learning_gain"] is None
    rev = body["review"]
    assert [x["question_id"] for x in rev] == ["pre1", "pre2", "pre3"]
    assert rev[0] == {
        "question_id": "pre1", "chosen_option": "a", "correct": False, "correct_option": "b",
        "explanation": "См. указанную статью.", "citation_ids": ["TEST_CPRL.art.2"],
    }
    assert rev[1]["correct"] is True
    assert rev[2]["chosen_option"] is None and rev[2]["correct"] is False

    row = seeded_db.execute(
        text("select user_id::text, scenario_id, kind, score, max_score, answers from quiz_attempts where id = :i"),
        {"i": body["attempt_id"]},
    ).one()
    assert row == (u, SID, "pre", 1, 3, answers)
    ev = seeded_db.execute(
        text("select payload from events where type = 'quiz_attempt' and user_id = :u"), {"u": u}
    ).scalar_one()
    assert ev == {"scenario_id": SID, "kind": "pre", "score": 1, "max": 3}


def test_post_after_pre_gives_learning_gain(api, game_client):
    u = api.user()
    url = f"/api/quiz/{SID}/attempts"
    game_client.post(url, json={"user_id": u, "kind": "pre", "answers": {"pre1": "b"}})
    r = game_client.post(url, json={"user_id": u, "kind": "pre", "answers": {"pre1": "b", "pre2": "a"}})
    assert r.json()["score"] == 2  # последняя pre = 2
    r = game_client.post(url, json={"user_id": u, "kind": "post", "answers": POST_OK})
    assert r.status_code == 201
    g = r.json()["learning_gain"]
    assert (g["pre"], g["post"], g["max"], g["delta"]) == (2, 3, 3, 1)
    assert g["note"] == "Предварительный показатель, не доказанный эффект обучения"


def test_post_without_pre_has_no_gain(api, game_client):
    u = api.user()
    r = game_client.post(f"/api/quiz/{SID}/attempts", json={"user_id": u, "kind": "post", "answers": POST_OK})
    assert r.status_code == 201
    assert r.json()["learning_gain"] is None and r.json()["score"] == 3


def test_unknown_question_id_is_422(api, game_client):
    u = api.user()
    r = game_client.post(
        f"/api/quiz/{SID}/attempts", json={"user_id": u, "kind": "pre", "answers": {"post1": "a"}}
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_attempt_404s(api, game_client):
    r = game_client.post(
        f"/api/quiz/{SID}/attempts", json={"user_id": str(uuid.uuid4()), "kind": "pre", "answers": {}}
    )
    assert r.status_code == 404
    r = game_client.post("/api/quiz/nope/attempts", json={"user_id": api.user(), "kind": "pre", "answers": {}})
    assert r.status_code == 404
