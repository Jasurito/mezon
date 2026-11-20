from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics import quiz as quiz_service
from app.db import get_db
from app.history import get_history
from app.history.store import HistoryStore
from app.scenarios.registry import Registry, get_registry
from app.schemas.analytics import QuizAttemptIn, QuizAttemptOut, QuizKind, QuizOut
from app.schemas.legal import Locale
from app.services.clock import get_now

router = APIRouter(tags=["quiz"])


@router.get("/quiz/{scenario_id}", response_model=QuizOut)
def get_quiz(
    scenario_id: str,
    kind: QuizKind,
    locale: Locale = "ru",
    registry: Registry = Depends(get_registry),
):
    """Вопросы теста без правильных ответов."""
    return quiz_service.get_quiz(registry, scenario_id, kind, locale)


@router.post("/quiz/{scenario_id}/attempts", response_model=QuizAttemptOut, status_code=201)
def post_attempt(
    scenario_id: str,
    body: QuizAttemptIn,
    locale: Locale = "ru",
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
):
    """Проверить ответы, сохранить попытку; для post считается прирост знаний."""
    return quiz_service.submit_attempt(db, registry, scenario_id, body, locale, now, history)
