import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.llm import LLM, get_llm
from app.ai.npc import answer_question
from app.config import Settings, get_settings
from app.auth.deps import require_path_session
from app.db import get_db
from app.history import get_history
from app.history.store import HistoryStore, make_activity, safely
from app.errors import NotFoundError, SessionFinishedError
from app.game_engine import available_actions
from app.models.app_tables import Event as EventRow
from app.scenarios.registry import Registry, get_registry
from app.schemas.npc import NpcAnswer, NpcAskRequest
from app.services import game
from app.services.clock import get_now
from app.tts.catalog import audio_for

router = APIRouter(tags=["npc"])


@router.post(
    "/sessions/{session_id}/npc/{character_id}/ask",
    response_model=NpcAnswer,
    dependencies=[Depends(require_path_session)],
)
def ask_npc(
    session_id: uuid.UUID,
    character_id: str,
    body: NpcAskRequest,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
    settings: Settings = Depends(get_settings),
    llm: LLM | None = Depends(get_llm),
    now: datetime = Depends(get_now),
    history: HistoryStore = Depends(get_history),
):
    """Свободный вопрос персонажу: ответ строится только из фактов сценария, состояние игры не меняется."""
    r = game.load_replayed(db, registry, session_id)
    if r.session.finished_at is not None or r.state.finished:
        raise SessionFinishedError()
    sc = r.loaded.scenario
    if character_id not in {c.id for c in sc.characters}:
        raise NotFoundError("Персонаж не найден", details={"character_id": character_id})
    locale = r.session.locale
    res = answer_question(
        r.loaded,
        character_id=character_id,
        stage=r.state.stage,
        text=body.text,
        locale=locale,  # type: ignore[arg-type]
        llm=llm,
        settings=settings,
    )
    suggested = f"ask_{res.question_id}"
    available = {a.id for a in available_actions(sc, r.state)}
    npc_payload = {
        "character_id": character_id,
        "question_id": res.question_id,
        "ai_generated": res.ai_generated,
        "stage": r.state.stage,
    }
    db.add(
        EventRow(
            session_id=r.session.id,
            user_id=r.session.user_id,
            type="npc_question",
            payload=npc_payload,
            ts=now,
        )
    )
    db.commit()
    safely(
        history.add_activity,
        make_activity(r.session.user_id, "npc_question", now, r.session.id, npc_payload),
    )
    question = next((q for q in sc.npc_questions if q.question_id == res.question_id), None)
    audio = (
        audio_for(r.loaded, character_id, question.answer_key, locale)
        if question is not None and not res.ai_generated
        else None
    )
    return NpcAnswer(
        speaker=character_id,
        text=res.text,
        question_id=res.question_id,
        fact_ids=res.fact_ids,
        ai_generated=res.ai_generated,
        suggested_action_id=suggested if suggested in available else None,
        audio_url=audio.url if audio else None,
        audio_duration_ms=audio.duration_ms if audio else None,
    )
