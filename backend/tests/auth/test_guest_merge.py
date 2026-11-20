import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import select

from app.history import get_history
from app.history.store import InMemoryHistoryStore, make_activity
from app.models.app_tables import Event, GameSession, QuizAttempt, User, UserStats
from tests.auth.conftest import add_session, login, signup

pytestmark = pytest.mark.db

T = datetime(2026, 11, 1, tzinfo=UTC)


def seed_guest(db, guest_id):
    uid = uuid.UUID(guest_id)
    sid = add_session(db, uid, finished=True, score=7)
    db.add(QuizAttempt(user_id=uid, scenario_id="x", kind="pre", answers={}, score=1, max_score=3, ts=T))
    db.add(Event(user_id=uid, session_id=sid, type="screen_view", payload={}, ts=T))
    db.add(UserStats(user_id=uid, sessions_started=2, sessions_finished=1, total_score=7, best_score=7,
                     total_time_sec=60, quizzes_taken=1, active_days=2, streak_days=2, last_active_at=T))
    db.commit()
    return sid


def test_signup_moves_guest_progress(client, db_session, make_guest):
    guest = make_guest()
    sid = seed_guest(db_session, guest)
    r = signup(client, guest=guest)
    acc = uuid.UUID(r.json()["id"])

    s = db_session.get(GameSession, sid)
    db_session.refresh(s)
    assert s.user_id == acc
    assert db_session.execute(select(QuizAttempt.user_id)).scalar_one() == acc
    assert db_session.execute(select(Event.user_id)).scalar_one() == acc
    assert db_session.get(UserStats, uuid.UUID(guest)) is None
    st = db_session.get(UserStats, acc)
    assert (st.sessions_started, st.sessions_finished, st.total_score, st.best_score, st.quizzes_taken) == (2, 1, 7, 7, 1)
    g = db_session.get(User, uuid.UUID(guest))
    db_session.refresh(g)
    assert g.merged_into == acc

    # данные доступны аккаунту через прежний API
    prof = client.get(f"/api/users/{acc}").json()
    assert prof["stats"]["sessions_finished"] == 1
    assert client.get(f"/api/users/{acc}/sessions").json()["total"] == 1


def test_stats_are_added_to_existing_account_stats(client, db_session, make_guest, make_account):
    acc, _ = make_account("a@example.com")
    db_session.add(UserStats(user_id=uuid.UUID(acc), sessions_started=1, sessions_finished=1, total_score=3,
                             best_score=9, total_time_sec=10, quizzes_taken=0, active_days=1, streak_days=5))
    db_session.commit()
    guest = make_guest()
    seed_guest(db_session, guest)
    assert login(client, guest=guest).status_code == 200
    st = db_session.get(UserStats, uuid.UUID(acc))
    db_session.refresh(st)
    assert (st.sessions_started, st.total_score, st.best_score, st.total_time_sec, st.active_days, st.streak_days) == (
        3, 10, 9, 70, 3, 5)


def test_login_merges_guest(client, db_session, make_guest, make_account):
    acc, _ = make_account("a@example.com")
    guest = make_guest()
    sid = seed_guest(db_session, guest)
    assert login(client, guest=guest).status_code == 200
    s = db_session.get(GameSession, sid)
    db_session.refresh(s)
    assert str(s.user_id) == acc


def test_cannot_merge_another_account(client, db_session, make_account):
    a, _ = make_account("a@example.com")
    sid = add_session(db_session, a, finished=True, score=5)
    make_account("b@example.com")
    assert login(client, email="b@example.com", guest=a).status_code == 200
    s = db_session.get(GameSession, sid)
    db_session.refresh(s)
    assert str(s.user_id) == a
    assert db_session.get(User, uuid.UUID(a)).merged_into is None


def test_merged_guest_cannot_be_merged_twice(client, db_session, make_guest, make_account):
    guest = make_guest()
    seed_guest(db_session, guest)
    a, _ = make_account("a@example.com", guest=guest)
    b, _ = make_account("b@example.com", guest=guest)
    assert db_session.get(User, uuid.UUID(guest)).merged_into == uuid.UUID(a)
    assert db_session.execute(select(GameSession.user_id)).scalar_one() == uuid.UUID(a)


@pytest.mark.parametrize("bad", ["not-a-uuid", "00000000-0000-0000-0000-000000000000", None])
def test_bad_guest_id_is_ignored(client, bad):
    assert signup(client, guest=bad).status_code == 201


def test_own_id_is_ignored(client, make_account):
    acc, _ = make_account("a@example.com")
    assert login(client, guest=acc).status_code == 200


def test_mongo_history_is_reassigned(app, client, db_session, make_guest):
    store = InMemoryHistoryStore()
    app.dependency_overrides[get_history] = lambda: store
    guest = make_guest()
    seed_guest(db_session, guest)
    store.sessions["s1"] = {"_id": "s1", "user_id": guest, "steps": []}
    store.add_activity(make_activity(guest, "session_started", T, None, {}))
    acc = signup(client, guest=guest).json()["id"]
    assert store.sessions["s1"]["user_id"] == acc
    assert all(a["user_id"] == acc for a in store.activity.values())
