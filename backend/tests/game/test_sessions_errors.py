import uuid

import pytest

from tests.game.conftest import BEST, SCENARIO_ID

pytestmark = pytest.mark.db


def _err(r, status, code):
    assert r.status_code == status, r.text
    body = r.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]
    return body["error"]["details"]


@pytest.fixture
def session(api):
    uid = api.user()
    return uid, api.start(uid)["session_id"]


def test_illegal_action(api, session):
    _, sid = session
    d = _err(api.act(sid, "final_claim", {"option": "refund"}), 409, "ILLEGAL_ACTION")
    assert d == {"action_id": "final_claim", "stage": "INTRO"}
    d = _err(api.act(sid, "no_such_action"), 409, "ILLEGAL_ACTION")
    assert d["action_id"] == "no_such_action"
    # состояние не изменилось и действие не записано
    assert api.c.get(f"/api/sessions/{sid}").json()["stage"] == "INTRO"
    assert api.act(sid, "enter_courtroom").status_code == 200


def test_decision_without_valid_option_is_illegal(api, session):
    _, sid = session
    api.play(sid, BEST[:-1])
    _err(api.act(sid, "final_claim"), 409, "ILLEGAL_ACTION")
    _err(api.act(sid, "final_claim", {"option": "bogus"}), 409, "ILLEGAL_ACTION")
    assert api.act(sid, "final_claim", {"option": "refund"}).status_code == 200


def test_session_finished_and_not_finished(api, session):
    _, sid = session
    d = _err(api.c.get(f"/api/sessions/{sid}/result"), 409, "SESSION_NOT_FINISHED")
    assert d["session_id"] == sid
    api.play(sid, BEST)
    assert api.c.get(f"/api/sessions/{sid}/result").status_code == 200
    _err(api.act(sid, "enter_courtroom"), 409, "SESSION_FINISHED")


def test_not_found(api, session):
    uid, _ = session
    ghost = str(uuid.uuid4())
    for r in (
        api.c.get(f"/api/sessions/{ghost}"),
        api.c.get(f"/api/sessions/{ghost}/result"),
        api.c.patch(f"/api/sessions/{ghost}", json={"locale": "ru"}),
        api.act(ghost, "enter_courtroom"),
    ):
        assert _err(r, 404, "NOT_FOUND") == {"session_id": ghost}
    r = api.c.post("/api/sessions", json={"user_id": uid, "scenario_id": "nope"})
    assert _err(r, 404, "NOT_FOUND") == {"scenario_id": "nope"}
    r = api.c.post("/api/sessions", json={"user_id": ghost, "scenario_id": SCENARIO_ID})
    assert _err(r, 404, "NOT_FOUND") == {"user_id": ghost}
    _err(api.c.get("/api/scenarios/nope"), 404, "NOT_FOUND")


def test_validation_errors(api, session):
    uid, sid = session
    _err(api.c.patch(f"/api/sessions/{sid}", json={"locale": "de"}), 422, "VALIDATION_ERROR")
    _err(api.c.get(f"/api/sessions/{sid}", params={"locale": "de"}), 422, "VALIDATION_ERROR")
    _err(api.c.post("/api/sessions", json={"scenario_id": SCENARIO_ID}), 422, "VALIDATION_ERROR")
    _err(api.c.post("/api/sessions", json={"user_id": uid, "scenario_id": SCENARIO_ID, "locale": "xx"}), 422, "VALIDATION_ERROR")
    _err(api.c.post(f"/api/sessions/{sid}/actions", json={}), 422, "VALIDATION_ERROR")


def test_patch_locale_keeps_game_state(api, session):
    _, sid = session
    api.play(sid, BEST[:8])
    before = api.c.get(f"/api/sessions/{sid}").json()
    r = api.c.patch(f"/api/sessions/{sid}", json={"locale": "uz-Latn"})
    assert r.status_code == 200
    after = r.json()
    assert after["locale"] == "uz-Latn" and before["locale"] == "ru"
    for k in ("stage", "stage_index", "score", "finished"):
        assert after[k] == before[k]
    assert [a["action_id"] for a in after["available_actions"]] == [a["action_id"] for a in before["available_actions"]]
    assert after["stage_title"] != before["stage_title"]
    assert [a["label"] for a in after["available_actions"]] != [a["label"] for a in before["available_actions"]]
    # язык сессии сохранён: GET и следующее действие приходят на uz-Latn
    assert api.c.get(f"/api/sessions/{sid}").json()["locale"] == "uz-Latn"
    nxt = after["available_actions"][0]["action_id"]
    assert api.act(sid, nxt).json()["locale"] == "uz-Latn"
    # locale в запросе меняет только язык ответа
    assert api.c.get(f"/api/sessions/{sid}", params={"locale": "ru"}).json()["locale"] == "ru"
    assert api.c.get(f"/api/sessions/{sid}").json()["locale"] == "uz-Latn"


def test_reload_returns_same_state_and_last_step_events(api, session):
    _, sid = session
    states = api.play(sid, BEST[:12])
    got = api.c.get(f"/api/sessions/{sid}").json()
    assert got == states[-1]
    assert got["events"]
    # перезагрузка сразу после старта: вступительные реплики
    uid = api.user()
    fresh = api.start(uid)
    assert api.c.get(f"/api/sessions/{fresh['session_id']}").json() == fresh


def test_outdated_session_after_scenario_change(api, session, seeded_db):
    """Лог, который больше не проигрывается на текущем сценарии, даёт 409 SESSION_OUTDATED, а не 500."""
    from sqlalchemy import update

    from app.models.app_tables import SessionAction

    _, sid = session
    assert api.act(sid, "enter_courtroom").status_code == 200
    # имитируем правку сценария: действия из лога больше нет
    seeded_db.execute(
        update(SessionAction)
        .where(SessionAction.session_id == uuid.UUID(sid))
        .values(action_id="removed_in_new_version")
    )
    seeded_db.flush()

    d = _err(api.c.get(f"/api/sessions/{sid}"), 409, "SESSION_OUTDATED")
    assert d["session_id"] == sid
    _err(api.act(sid, "anything"), 409, "SESSION_OUTDATED")
    _err(api.c.get(f"/api/sessions/{sid}/result"), 409, "SESSION_OUTDATED")
