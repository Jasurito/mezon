"""Приём клиентских событий пачкой."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app.history.store import HistoryStore, make_activity, safely
from app.models.app_tables import Event
from app.schemas.analytics import EventsIn, EventsOut

ALLOWED_TYPES = frozenset({"legal_panel_opened", "evidence_opened", "mentor_opened", "screen_view"})


def ingest(db: Session, body: EventsIn, now: datetime, history: HistoryStore | None = None) -> EventsOut:
    rows = [
        {
            "session_id": body.session_id,
            "user_id": body.user_id,
            "type": e.type,
            "payload": e.payload,
            "ts": e.ts or now,
        }
        for e in body.events
        if e.type in ALLOWED_TYPES
    ]
    if rows:
        db.execute(insert(Event).values(rows))
        db.commit()
        if history is not None:
            for r in rows:
                if r["user_id"] is not None:
                    safely(
                        history.add_activity,
                        make_activity(r["user_id"], r["type"], r["ts"], r["session_id"], r["payload"]),
                    )
    return EventsOut(accepted=len(rows), rejected=len(body.events) - len(rows))
