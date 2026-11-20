"""Пересборка истории в MongoDB из Postgres (идемпотентно).

    python -m app.history.backfill [--user <id>]
"""

from __future__ import annotations

import argparse
import logging
import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AppError
from app.history import build_store
from app.history.builder import build_session_doc
from app.history.store import HistoryStore, make_activity
from app.models.app_tables import Event, GameSession, SessionAction
from app.scenarios.registry import Registry

log = logging.getLogger("adolat.history")

# события таблицы events, которые попадают в ленту активности (action и mistake — нет)
ACTIVITY_TYPES = frozenset(
    {
        "session_started",
        "session_finished",
        "quiz_attempt",
        "mentor_question",
        "npc_question",
        "legal_panel_opened",
        "evidence_opened",
        "mentor_opened",
        "screen_view",
    }
)


@dataclass
class BackfillResult:
    sessions: int = 0
    sessions_skipped: int = 0
    activity: int = 0


def backfill(db: Session, registry: Registry, store: HistoryStore, user_id: uuid.UUID | None = None) -> BackfillResult:
    res = BackfillResult()
    q = select(GameSession).order_by(GameSession.started_at)
    if user_id is not None:
        q = q.where(GameSession.user_id == user_id)
    for session in db.execute(q).scalars():
        loaded = registry.get(session.scenario_id)
        if loaded is None:
            log.warning("сессия %s: сценарий %s не найден, пропуск", session.id, session.scenario_id)
            res.sessions_skipped += 1
            continue
        actions = list(
            db.execute(
                select(SessionAction).where(SessionAction.session_id == session.id).order_by(SessionAction.seq)
            ).scalars()
        )
        try:
            doc = build_session_doc(loaded, session, actions)
        except AppError as exc:
            log.warning("сессия %s: журнал не проигрывается (%s), пропуск", session.id, exc.code)
            res.sessions_skipped += 1
            continue
        store.upsert_session(doc)
        res.sessions += 1

    eq = select(Event).where(Event.type.in_(ACTIVITY_TYPES), Event.user_id.is_not(None)).order_by(Event.id)
    if user_id is not None:
        eq = eq.where(Event.user_id == user_id)
    for e in db.execute(eq).scalars():
        store.add_activity(make_activity(e.user_id, e.type, e.ts, e.session_id, e.payload))
        res.activity += 1
    return res


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Восстановить историю MongoDB из Postgres")
    parser.add_argument("--user", type=uuid.UUID, default=None, help="только этот пользователь")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)

    from app.config import get_settings
    from app.db import SessionLocal
    from app.scenarios.registry import load_registry

    settings = get_settings()
    if not settings.MONGO_URL:
        print("MONGO_URL не задан: история выключена, делать нечего")
        return 1
    store = build_store(settings)
    client = getattr(store, "_client", None)
    if client is not None:
        try:
            client.admin.command("ping")
        except Exception as exc:  # noqa: BLE001
            print(f"MongoDB недоступна: {exc.__class__.__name__}")
            return 2
    store.ensure_indexes()
    with SessionLocal() as db:
        registry = load_registry(settings, lambda: _ctx(db))
        res = backfill(db, registry, store, args.user)
    store.close()
    print(f"сессий: {res.sessions} (пропущено {res.sessions_skipped}), записей активности: {res.activity}")
    return 0


def _ctx(db: Session):
    from contextlib import nullcontext

    return nullcontext(db)


if __name__ == "__main__":
    raise SystemExit(main())
