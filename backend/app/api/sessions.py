import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.deps import Viewer, get_viewer, require_path_session
from app.db import get_db
from app.history import get_history
from app.history.store import HistoryStore
from app.scenarios.registry import Registry, get_registry
from app.schemas.api import (
    ActionRequest,
    CreateSession,
    EvidenceDocument,
    GameState,
    PatchSession,
    SessionResult,
)
from app.schemas.legal import Locale
from app.services import game
from app.services.clock import get_now

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=GameState, status_code=201)
def create_session(
    body: CreateSession,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
    viewer: Viewer = Depends(get_viewer),
):
    """Начать игру: создаёт сессию и возвращает начальное состояние со вступительными репликами."""
    viewer.require_user(body.user_id)
    return game.start_session(db, registry, body.user_id, body.scenario_id, body.locale, now, history)


@router.get("/sessions/{session_id}", response_model=GameState, dependencies=[Depends(require_path_session)])
def get_session(
    session_id: uuid.UUID,
    locale: Locale | None = None,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
):
    """Состояние после replay; events — события последнего действия."""
    return game.get_state(db, registry, session_id, locale)


@router.get(
    "/sessions/{session_id}/evidence/{evidence_id}",
    response_model=EvidenceDocument,
    dependencies=[Depends(require_path_session)],
)
def get_evidence_document(
    session_id: uuid.UUID,
    evidence_id: str,
    locale: Locale | None = None,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
):
    """Текст документа из материалов дела. Только улики, уже доступные в этой сессии (как в GameState.evidence):
    заключение эксперта не прочитать до того, как его приобщили."""
    return game.get_evidence_document(db, registry, session_id, evidence_id, locale)


@router.patch("/sessions/{session_id}", response_model=GameState, dependencies=[Depends(require_path_session)])
def patch_session(
    session_id: uuid.UUID,
    body: PatchSession,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    history: HistoryStore = Depends(get_history),
):
    """Сменить язык сессии; состояние игры не меняется."""
    return game.set_locale(db, registry, session_id, body.locale, history)


@router.post("/sessions/{session_id}/actions", response_model=GameState, dependencies=[Depends(require_path_session)])
def post_action(
    session_id: uuid.UUID,
    body: ActionRequest,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
):
    """Выполнить действие; ответ на языке сессии."""
    params = body.params.model_dump(exclude_none=True) if body.params else None
    return game.perform_action(db, registry, session_id, body.action_id, params or None, now, history)


@router.get("/sessions/{session_id}/result", response_model=SessionResult, dependencies=[Depends(require_path_session)])
def get_result(
    session_id: uuid.UUID,
    locale: Locale | None = None,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
):
    """Итог игры; до завершения — 409 SESSION_NOT_FINISHED."""
    return game.get_result(db, registry, session_id, locale)
