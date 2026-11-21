"""Игровой сервис: сессии, журнал действий, результат. Движок вызывается как чистая функция."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import (
    IllegalActionError,
    NotFoundError,
    SessionFinishedError,
    SessionNotFinishedError,
    SessionOutdatedError,
)
from app.game_engine import (
    EngineState,
    Event,
    IllegalAction,
    LoggedAction,
    ScenarioError,
    SessionFinished,
    apply,
    evaluate,
    initial_state,
    replay,
)
from app.legal.service import get_citation_views
from app.models.app_tables import Event as EventRow
from app.models.app_tables import GameSession, SessionAction, User
from app.history import builder
from app.history.store import HistoryStore, make_activity, safely
from app.scenarios.loader import LoadedScenario
from app.scenarios.registry import Registry
from app.schemas import api
from app.schemas.legal import Locale
from app.services import presenter, stats


@dataclass
class Replayed:
    session: GameSession
    loaded: LoadedScenario
    state: EngineState
    events: list[Event]  # события последнего шага


def create_user(db: Session, display_name: str | None, now: datetime) -> User:
    user = User(id=uuid.uuid4(), display_name=display_name, created_at=now)
    db.add(user)
    db.commit()
    return user


def _scenario(registry: Registry, scenario_id: str) -> LoadedScenario:
    loaded = registry.get(scenario_id)
    if loaded is None:
        raise NotFoundError("Сценарий не найден", details={"scenario_id": scenario_id})
    return loaded


def get_loaded(registry: Registry, scenario_id: str) -> LoadedScenario:
    return _scenario(registry, scenario_id)


def _get_session(db: Session, session_id: uuid.UUID, *, lock: bool = False) -> GameSession:
    stmt = select(GameSession).where(GameSession.id == session_id)
    if lock:
        stmt = stmt.with_for_update()
    row = db.execute(stmt).scalar_one_or_none()
    if row is None:
        raise NotFoundError("Сессия не найдена", details={"session_id": str(session_id)})
    return row


def _log(db: Session, session_id: uuid.UUID) -> list[SessionAction]:
    return list(
        db.execute(
            select(SessionAction).where(SessionAction.session_id == session_id).order_by(SessionAction.seq)
        ).scalars()
    )


def _replay_log(loaded: LoadedScenario, session: GameSession, log: list[SessionAction]):
    """Replay the stored log; a log that no longer fits the scenario means the content changed."""
    actions = [LoggedAction(action_id=a.action_id, params=a.params) for a in log]
    try:
        return replay(loaded.scenario, actions)
    except (IllegalAction, SessionFinished, ScenarioError) as exc:
        raise SessionOutdatedError(
            details={
                "session_id": str(session.id),
                "session_version": session.scenario_version,
                "scenario_version": loaded.scenario.version,
            }
        ) from exc


def _replay(db: Session, registry: Registry, session: GameSession) -> Replayed:
    loaded = _scenario(registry, session.scenario_id)
    state, events = _replay_log(loaded, session, _log(db, session.id))
    return Replayed(session, loaded, state, events)


def load_replayed(db: Session, registry: Registry, session_id: uuid.UUID) -> Replayed:
    """Session row + replayed engine state (public entry point for the mentor and other readers)."""
    return _replay(db, registry, _get_session(db, session_id))


def start_session(
    db: Session,
    registry: Registry,
    user_id: uuid.UUID,
    scenario_id: str,
    locale: Locale,
    now: datetime,
    history: HistoryStore | None = None,
) -> api.GameState:
    if db.get(User, user_id) is None:
        raise NotFoundError("Пользователь не найден", details={"user_id": str(user_id)})
    loaded = _scenario(registry, scenario_id)
    state, events = initial_state(loaded.scenario)
    session = GameSession(
        id=uuid.uuid4(),
        user_id=user_id,
        scenario_id=scenario_id,
        scenario_version=loaded.scenario.version,
        locale=locale,
        started_at=now,
    )
    db.add(session)
    db.flush()
    started_payload = {"scenario_id": scenario_id, "scenario_version": loaded.scenario.version, "locale": locale}
    db.add(EventRow(session_id=session.id, user_id=user_id, type="session_started", payload=started_payload, ts=now))
    stats.on_session_started(db, user_id, now)
    db.commit()
    if history is not None:
        step0 = builder.step_doc(0, now, None, None, None, state, events)
        safely(history.start_session, builder.session_doc(session.id, user_id, loaded, locale, now, [step0]))
        safely(history.add_activity, make_activity(user_id, "session_started", now, session.id, started_payload))
    return presenter.build_game_state(loaded, state, events, session.id, locale)


def get_state(
    db: Session, registry: Registry, session_id: uuid.UUID, locale: Locale | None
) -> api.GameState:
    session = _get_session(db, session_id)
    r = _replay(db, registry, session)
    return presenter.build_game_state(r.loaded, r.state, r.events, session.id, locale or session.locale)  # type: ignore[arg-type]


def get_evidence_document(
    db: Session, registry: Registry, session_id: uuid.UUID, evidence_id: str, locale: Locale | None
) -> api.EvidenceDocument:
    session = _get_session(db, session_id)
    r = _replay(db, registry, session)
    doc = presenter.build_evidence_document(r.loaded, r.state, evidence_id, locale or session.locale)  # type: ignore[arg-type]
    if doc is None:
        raise NotFoundError("Документ не найден или ещё не доступен", details={"evidence_id": evidence_id})
    return doc


def set_locale(
    db: Session, registry: Registry, session_id: uuid.UUID, locale: Locale, history: HistoryStore | None = None
) -> api.GameState:
    session = _get_session(db, session_id, lock=True)
    session.locale = locale
    r = _replay(db, registry, session)
    db.commit()
    if history is not None:
        safely(history.finish_session, str(session.id), {"locale": locale})
    return presenter.build_game_state(r.loaded, r.state, r.events, session.id, locale)


def perform_action(
    db: Session,
    registry: Registry,
    session_id: uuid.UUID,
    action_id: str,
    params: dict | None,
    now: datetime,
    history: HistoryStore | None = None,
) -> api.GameState:
    """Одно действие в одной транзакции; строка сессии заблокирована до коммита."""
    session = _get_session(db, session_id, lock=True)
    if session.finished_at is not None:
        raise SessionFinishedError()
    log = _log(db, session.id)
    loaded = _scenario(registry, session.scenario_id)
    sc = loaded.scenario
    state, _ = _replay_log(loaded, session, log)
    try:
        new_state, events = apply(sc, state, action_id, params)
    except IllegalAction as exc:
        raise IllegalActionError(details={"action_id": exc.action_id, "stage": exc.stage}) from exc
    except SessionFinished as exc:
        raise SessionFinishedError() from exc

    seq = len(log) + 1
    db.add(SessionAction(session_id=session.id, seq=seq, action_id=action_id, params=params, ts=now))
    db.add(
        EventRow(
            session_id=session.id,
            user_id=session.user_id,
            type="action",
            payload={"action_id": action_id, "params": params, "stage": state.stage, "step": new_state.step},
            ts=now,
        )
    )
    finish_fields: dict | None = None
    finished_payload: dict | None = None
    if new_state.finished:
        outcome = evaluate(sc, new_state)
        session.finished_at = now
        session.outcome = outcome.outcome
        session.score = new_state.score
        finished_payload = {
            "outcome": outcome.outcome,
            "score": new_state.score,
            "max_score": outcome.max_score,
            "correct_decision_rate": outcome.correct_decision_rate,
        }
        finish_fields = {
            "finished_at": now,
            "outcome": outcome.outcome,
            "score": new_state.score,
            "max_score": outcome.max_score,
        }
        db.add(
            EventRow(
                session_id=session.id,
                user_id=session.user_id,
                type="session_finished",
                payload=finished_payload,
                ts=now,
            )
        )
        stats.on_session_finished(db, session.user_id, new_state.score, session.started_at, now)
        for m in outcome.mistakes:
            db.add(
                EventRow(
                    session_id=session.id,
                    user_id=session.user_id,
                    type="mistake",
                    payload={"category": m.category, "title_key": m.title_key},
                    ts=now,
                )
            )
    db.commit()
    if history is not None:
        step = builder.step_doc(seq, now, action_id, params, state.stage, new_state, events)
        safely(history.push_step, str(session.id), step)
        if finish_fields is not None and finished_payload is not None:
            safely(history.finish_session, str(session.id), finish_fields)
            safely(
                history.add_activity,
                make_activity(session.user_id, "session_finished", now, session.id, finished_payload),
            )
    return presenter.build_game_state(loaded, new_state, events, session.id, session.locale)  # type: ignore[arg-type]


def get_result(
    db: Session, registry: Registry, session_id: uuid.UUID, locale: Locale | None
) -> api.SessionResult:
    session = _get_session(db, session_id)
    r = _replay(db, registry, session)
    if not r.state.finished:
        raise SessionNotFinishedError(details={"session_id": str(session_id)})
    loc: Locale = locale or session.locale  # type: ignore[assignment]
    outcome = evaluate(r.loaded.scenario, r.state)
    citations = get_citation_views(db, outcome.citation_ids, r.loaded.scenario.legal_date, loc)
    finished_at = session.finished_at or session.started_at
    spent = max(0, int((finished_at - session.started_at).total_seconds()))
    return presenter.build_result(r.loaded, outcome, session.id, loc, citations, spent)
