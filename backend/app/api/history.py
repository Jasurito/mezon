import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import TypeAdapter
from sqlalchemy.orm import Session

from app.db import get_db
from app.errors import NotFoundError
from app.game_engine import Event as EngineEvent
from app.game_engine import evaluate
from app.history import builder, get_history
from app.history.store import HistoryStore
from app.i18n import translate
from app.models.app_tables import GameSession, User
from app.scenarios.registry import Registry, get_registry
from app.schemas.history import ActivityItem, ActivityOut, HistoryStepOut, SessionHistoryOut
from app.schemas.legal import Locale
from app.services import game, presenter

router = APIRouter(tags=["history"])

_event_adapter = TypeAdapter(EngineEvent)


def _usable(doc: dict | None, session: GameSession, n_actions: int) -> bool:
    """Документ Mongo пригоден, только если он полон (не отстал от журнала Postgres)."""
    if doc is None:
        return False
    steps = doc.get("steps") or []
    if len(steps) != n_actions + 1:
        return False
    return (doc.get("finished_at") is not None) == (session.finished_at is not None)


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryOut)
def session_history(
    session_id: uuid.UUID,
    locale: Locale | None = None,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    history: HistoryStore = Depends(get_history),
) -> SessionHistoryOut:
    """Хроника дела: шаги с переведёнными событиями и итог. Mongo, при её отсутствии пересборка из Postgres."""
    session = game._get_session(db, session_id)
    loaded = game.get_loaded(registry, session.scenario_id)
    loc: Locale = locale or session.locale  # type: ignore[assignment]
    log = game._log(db, session_id)

    doc = history.get_session(str(session_id)) if history.available else None
    source = "mongo"
    if not _usable(doc, session, len(log)):
        doc = builder.build_session_doc(loaded, session, log)
        source = "postgres"
    assert doc is not None

    steps = [
        HistoryStepOut(
            seq=s["seq"],
            ts=s["ts"],
            action_id=s.get("action_id"),
            params=s.get("params"),
            stage_before=s.get("stage_before"),
            stage_after=s["stage_after"],
            score_after=s["score_after"],
            events=presenter.present_events(
                loaded, [_event_adapter.validate_python(e) for e in s.get("events", [])], loc
            ),
        )
        for s in sorted(doc["steps"], key=lambda s: s["seq"])
    ]

    outcome_title = None
    if doc.get("outcome"):
        # название исхода берётся из правила оценки по финальному состоянию
        r = game.load_replayed(db, registry, session_id)
        if r.state.finished:
            outcome_title = translate(loaded, evaluate(loaded.scenario, r.state).title_key, loc)

    return SessionHistoryOut(
        session_id=session.id,
        user_id=session.user_id,
        scenario_id=doc["scenario_id"],
        scenario_version=doc["scenario_version"],
        locale=loc,
        started_at=doc["started_at"],
        finished_at=doc.get("finished_at"),
        outcome=doc.get("outcome"),
        outcome_title=outcome_title,
        score=doc.get("score"),
        max_score=doc.get("max_score"),
        steps=steps,
        source=source,  # type: ignore[arg-type]
    )


@router.get("/users/{user_id}/activity", response_model=ActivityOut)
def user_activity(
    user_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    before: datetime | None = None,
    db: Session = Depends(get_db),
    history: HistoryStore = Depends(get_history),
) -> ActivityOut:
    """Лента активности, новые сверху; курсор before = ts последней записи страницы. Без Mongo available=false."""
    if db.get(User, user_id) is None:
        raise NotFoundError("Пользователь не найден", details={"user_id": str(user_id)})
    rows = history.list_activity(str(user_id), limit, before) if history.available else None
    if rows is None:
        return ActivityOut(items=[], next_before=None, available=False)
    items = [
        ActivityItem(type=r["type"], ts=r["ts"], session_id=r.get("session_id"), payload=r.get("payload") or {})
        for r in rows
    ]
    return ActivityOut(items=items, next_before=items[-1].ts if len(items) == limit else None, available=True)
