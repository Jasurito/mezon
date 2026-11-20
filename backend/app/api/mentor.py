import json
import logging
import uuid
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.llm import LLM, get_llm
from app.ai.mentor import MentorPlan, prepare, stream_events
from app.config import Settings, get_settings
from app.auth.deps import Viewer, get_viewer
from app.db import SessionLocal, get_db
from app.history import get_history
from app.history.store import HistoryStore, make_activity, safely
from app.models.app_tables import Event as EventRow
from app.rag.deps import embedder_dep
from app.rag.embedder import Embedder
from app.scenarios.registry import Registry, get_registry
from app.schemas.rag import MentorAskRequest
from app.services.clock import get_now

router = APIRouter(prefix="/mentor", tags=["mentor"])
log = logging.getLogger("adolat.mentor")

DbFactory = Callable[[], AbstractContextManager[Session]]


def get_event_db_factory() -> DbFactory:
    """Короткая отдельная сессия для записи события из SSE-генератора.

    Сессия запроса (get_db) к этому моменту может быть уже закрыта. Тесты подменяют зависимость.
    """

    @contextmanager
    def open_db() -> Iterator[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return open_db


def format_sse(event: str, data: Any) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"


def _recorder(
    plan: MentorPlan, open_db: DbFactory, now: datetime, history: HistoryStore | None = None
) -> Callable[[dict[str, Any]], None]:
    def record(payload: dict[str, Any]) -> None:
        try:
            with open_db() as db:
                db.add(
                    EventRow(
                        session_id=uuid.UUID(plan.session_id) if plan.session_id else None,
                        user_id=plan.user_id,
                        type="mentor_question",
                        payload=payload,
                        ts=now,
                    )
                )
                db.commit()
            if history is not None and plan.user_id is not None:
                safely(
                    history.add_activity,
                    make_activity(plan.user_id, "mentor_question", now, plan.session_id, payload),
                )
        except Exception:  # noqa: BLE001 - аналитика не должна ломать ответ
            log.exception("не удалось записать событие mentor_question")

    return record


@router.post("/ask")
def ask(
    body: MentorAskRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    registry: Registry = Depends(get_registry),
    llm: LLM | None = Depends(get_llm),
    embedder: Embedder = Depends(embedder_dep),
    open_event_db: DbFactory = Depends(get_event_db_factory),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
    viewer: Viewer = Depends(get_viewer),
) -> StreamingResponse:
    """Ответ наставника потоком SSE: sources → block* → done (или один error)."""
    if body.session_id is not None:
        viewer.require_session(body.session_id)
    # Вся работа с БД до начала потока: зависимость с yield может закрыть сессию раньше генератора.
    plan = prepare(
        db,
        req=body,
        settings=settings,
        registry=registry,
        llm=llm,
        embedder=embedder,
        today=now.date(),
    )
    record = _recorder(plan, open_event_db, now, history)

    def gen() -> Iterator[str]:
        for name, data in stream_events(plan, llm, settings, record):
            yield format_sse(name, data)

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
