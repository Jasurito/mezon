"""Сборка документов истории из Postgres (журнал действий + replay). Нужна для /history без Mongo и для backfill."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from app.errors import SessionOutdatedError
from app.game_engine import (
    EngineState,
    Event,
    IllegalAction,
    ScenarioError,
    SessionFinished,
    apply,
    evaluate,
    initial_state,
)
from app.models.app_tables import GameSession, SessionAction
from app.scenarios.loader import LoadedScenario


def event_dicts(events: list[Event]) -> list[dict[str, Any]]:
    return [e.model_dump(mode="json") for e in events]


def step_doc(
    seq: int,
    ts: datetime,
    action_id: str | None,
    params: dict | None,
    stage_before: str | None,
    state_after: EngineState,
    events: list[Event],
) -> dict[str, Any]:
    return {
        "seq": seq,
        "ts": ts,
        "action_id": action_id,
        "params": params,
        "stage_before": stage_before,
        "stage_after": state_after.stage,
        "score_after": state_after.score,
        "events": event_dicts(events),
    }


def session_doc(
    session_id: uuid.UUID | str,
    user_id: uuid.UUID | str,
    loaded: LoadedScenario,
    locale: str,
    started_at: datetime,
    steps: list[dict[str, Any]],
    *,
    finished_at: datetime | None = None,
    outcome: str | None = None,
    score: int | None = None,
    max_score: int | None = None,
) -> dict[str, Any]:
    return {
        "_id": str(session_id),
        "user_id": str(user_id),
        "scenario_id": loaded.scenario.scenario_id,
        "scenario_version": loaded.scenario.version,
        "locale": locale,
        "started_at": started_at,
        "finished_at": finished_at,
        "outcome": outcome,
        "score": score,
        "max_score": loaded.scenario.max_score if max_score is None else max_score,
        "steps": steps,
    }


def build_session_doc(loaded: LoadedScenario, session: GameSession, log: list[SessionAction]) -> dict[str, Any]:
    """Документ session_history из журнала Postgres. SessionOutdatedError, если журнал не проигрывается."""
    sc = loaded.scenario
    state, events = initial_state(sc)
    steps = [step_doc(0, session.started_at, None, None, None, state, events)]
    try:
        for a in log:
            before = state.stage
            state, events = apply(sc, state, a.action_id, a.params)
            steps.append(step_doc(a.seq, a.ts, a.action_id, a.params, before, state, events))
    except (IllegalAction, SessionFinished, ScenarioError) as exc:
        raise SessionOutdatedError(
            details={
                "session_id": str(session.id),
                "session_version": session.scenario_version,
                "scenario_version": sc.version,
            }
        ) from exc
    max_score = sc.max_score
    if session.finished_at is not None and state.finished:
        max_score = evaluate(sc, state).max_score
    return session_doc(
        session.id,
        session.user_id,
        loaded,
        session.locale,
        session.started_at,
        steps,
        finished_at=session.finished_at,
        outcome=session.outcome,
        score=session.score,
        max_score=max_score,
    )
