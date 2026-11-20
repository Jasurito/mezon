import json
import shutil
import uuid

import pytest

from tests.game.conftest import BEST, LOSS, PARTIAL, SCENARIOS_FIXTURES

pytestmark = pytest.mark.db

SID = "test_consumer"


def dash(client, user, **params):
    r = client.get(f"/api/users/{user}/dashboard", params=params)
    assert r.status_code == 200, r.text
    return r.json()


def quiz(client, user, kind, answers):
    r = client.post(f"/api/quiz/{SID}/attempts", json={"user_id": user, "kind": kind, "answers": answers})
    assert r.status_code == 201, r.text


def test_new_user_dashboard(api, game_client):
    u = api.user()
    d = dash(game_client, u)
    assert d["user"] == {"user_id": u, "display_name": "Азиз"}
    assert d["knowledge_level"] == {"score": None, "label": "Нет данных"}
    assert d["completed"] == [] and d["learning_gain"] == []
    assert d["mistake_categories"] == [] and d["focus_topics"] == []
    assert [(r["scenario_id"], r["reason"]) for r in d["recommended"]] == [(SID, "Новое дело")]
    card = d["recommended"][0]
    assert card["available"] is True and card["title"] == "Неисправный смартфон (тест)" and card["topics"]


def test_dashboard_after_three_games(api, game_client):
    u = api.user()
    api.play(api.start(u)["session_id"], BEST)
    api.play(api.start(u)["session_id"], PARTIAL)
    api.play(api.start(u)["session_id"], LOSS)
    quiz(game_client, u, "pre", {"pre1": "b"})
    quiz(game_client, u, "post", {"post1": "a", "post2": "a", "post3": "b"})

    d = dash(game_client, u)
    # новые сверху
    assert [(c["outcome"], c["score"]) for c in d["completed"]] == [
        ("claim_denied", 4), ("claim_partially_granted", 40), ("claim_granted", 100),
    ]
    assert [c["outcome_title"] for c in d["completed"]] == [
        "В иске отказано", "Иск удовлетворён частично", "Иск удовлетворён",
    ]
    assert d["completed"][0]["max_score"] == 100 and d["completed"][0]["title"].startswith("Неисправный")
    assert d["learning_gain"] == [
        {"scenario_id": SID, "pre": 1, "post": 3, "max": 3,
         "note": "Предварительный показатель, не доказанный эффект обучения"}
    ]
    # (4 + 40 + 100 + 100) / 4 = 61
    assert d["knowledge_level"] == {"score": 61, "label": "Уверенный"}
    assert d["mistake_categories"] == [
        {"category": "procedure", "title": "Процедура", "count": 3},
        {"category": "evidence", "title": "Доказательства", "count": 1},
        {"category": "substantive", "title": "substantive", "count": 1},  # неизвестная категория: сам id
    ]
    assert d["recommended"] == []  # единственный сценарий завершён
    assert [f["category"] for f in d["focus_topics"]] == ["procedure", "evidence", "substantive"]
    assert d["focus_topics"][0]["topic"] == "Ходатайства и экспертиза в гражданском процессе"
    assert d["focus_topics"][0]["citation_ids"] == ["TEST_CPC.art.2"]


@pytest.mark.parametrize(
    "path,expected,label",
    [(LOSS, 4, "Начальный"), (BEST, 100, "Продвинутый")],
)
def test_knowledge_level_labels(api, game_client, path, expected, label):
    u = api.user()
    api.play(api.start(u)["session_id"], path)
    assert dash(game_client, u)["knowledge_level"] == {"score": expected, "label": label}


def test_dashboard_uz_latn(api, game_client):
    u = api.user()
    api.play(api.start(u)["session_id"], LOSS)
    d = dash(game_client, u, locale="uz-Latn")
    assert d["knowledge_level"]["label"] == "Boshlang'ich"
    assert d["mistake_categories"][0]["title"] == "Protsedura"
    assert d["completed"][0]["outcome_title"] != "В иске отказано"
    d2 = dash(game_client, api.user(), locale="uz-Latn")
    assert d2["knowledge_level"]["label"] == "Ma'lumot yo'q"
    assert d2["recommended"][0]["reason"] == "Yangi ish"


def test_recommended_reasons(api, make_client, tmp_path):
    for sid, available in (("test_consumer", True), ("soon", False), ("other", True)):
        dst = tmp_path / sid
        shutil.copytree(SCENARIOS_FIXTURES / "test_consumer", dst)
        for name in ("scenario.json", "quiz.json"):
            data = json.loads((dst / name).read_text(encoding="utf-8"))
            data["scenario_id"] = sid
            if name == "scenario.json":
                data["card"]["available"] = available
            (dst / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    with make_client(scenarios_dir=tmp_path) as c:
        u = c.post("/api/users", json={}).json()["user_id"]
        c.post("/api/sessions", json={"user_id": u, "scenario_id": "other", "locale": "ru"})
        d = dash(c, u)
        assert {r["scenario_id"]: r["reason"] for r in d["recommended"]} == {
            "test_consumer": "Новое дело", "soon": "Скоро", "other": "Не завершено",
        }
        assert next(r for r in d["recommended"] if r["scenario_id"] == "soon")["available"] is False


def test_dashboard_404(game_client):
    r = game_client.get(f"/api/users/{uuid.uuid4()}/dashboard")
    assert r.status_code == 404 and r.json()["error"]["code"] == "NOT_FOUND"
