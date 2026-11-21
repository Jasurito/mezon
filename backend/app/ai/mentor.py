"""AI-наставник: подготовка контекста (вся работа с БД) и поток событий (docs/BACKEND.md §5.8).

``prepare`` ходит в БД и быстрый LLM и возвращает ``MentorPlan``. ``stream_events`` БД не трогает:
он вызывает наставника, проверяет блоки и отдаёт события. Так SSE-генератор не зависит от
жизни сессии БД запроса.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.classify import classify_question
from app.ai.context import SessionContext, load_session_context
from app.ai.llm import LLM
from app.ai.messages import msg
from app.ai.prompts import build_mentor_system, build_mentor_user
from app.ai.prompts.mentor import SourceForPrompt
from app.config import Settings
from app.errors import AppError
from app.legal.service import get_article_view
from app.models.legal import Chunk
from app.rag.embedder import Embedder
from app.rag.language import detect_language
from app.rag.pipeline import Candidate, hybrid_search
from app.rag.rerank import NullReranker, RerankItem, get_reranker
from app.rag.search import strip_header
from app.rag.validate import validate_blocks
from app.scenarios.registry import Registry
from app.schemas.legal import Locale
from app.schemas.rag import MentorAnswer, MentorAskRequest

log = logging.getLogger("adolat.ai")

HISTORY_LIMIT = 6
HISTORY_TEXT_LIMIT = 1000
MENTOR_MAX_TOKENS = 4096  # только страховка от зависания: длину задаёт промпт, ответ не обрезается
OLLAMA_MENTOR_MAX_TOKENS = 2048  # страховка; обычный ответ ~300–600 токенов
HEAD_SOURCES = 5

Kind = Literal["error", "out_of_scope", "insufficient", "answer"]
Event = tuple[str, Any]


@dataclass
class MentorPlan:
    kind: Kind
    language: Locale
    category: str
    question: str
    sources_payload: list[dict] = field(default_factory=list)
    source_articles: dict[str, str] = field(default_factory=dict)  # source_id -> article_number
    system: str = ""
    user_message: str = ""
    session_id: str | None = None
    user_id: Any = None
    reranked: bool = False
    error: tuple[str, str] | None = None


def _article_label(language: Locale, number: str) -> str:
    if language == "uz-Latn":
        return f"{number}-modda"
    if language == "uz-Cyrl":
        return f"{number}-модда"
    return f"ст. {number}"


def select_candidates(candidates: Sequence[Candidate], limit: int) -> list[Candidate]:
    """Лучшие по баллу, но статьи сценария не вытесняются из выборки органической выдачей."""
    head = list(candidates[: min(HEAD_SOURCES, limit)])
    rest = list(candidates[len(head):])
    scenario = [c for c in rest if c.scenario]
    others = [c for c in rest if not c.scenario]
    return (head + scenario + others)[:limit]


def _history(req: MentorAskRequest) -> list[tuple[str, str]]:
    return [(h.role, h.text[:HISTORY_TEXT_LIMIT]) for h in req.history[-HISTORY_LIMIT:]]


def prepare(
    db: Session,
    *,
    req: MentorAskRequest,
    settings: Settings,
    registry: Registry,
    llm: LLM | None,
    embedder: Embedder | None,
    today: date,
) -> MentorPlan:
    language = detect_language(req.question, default=req.locale)
    question = req.question.strip()
    plan = MentorPlan(kind="answer", language=language, category="concept", question=question)

    # Сессия: неизвестная сессия — единственное событие error.
    ctx: SessionContext | None = None
    if req.session_id is not None:
        try:
            ctx = load_session_context(db, registry, req.session_id, language)
        except AppError as exc:
            plan.kind = "error"
            plan.error = (exc.code, exc.message)
            return plan
        plan.session_id = str(ctx.session_id)
        plan.user_id = ctx.user_id

    plan.category = classify_question(llm, settings, question, has_session=req.session_id is not None)
    if plan.category == "out_of_scope":
        plan.kind = "out_of_scope"
        return plan

    outcome = hybrid_search(
        db,
        query=question,
        locale=language,
        on_date=ctx.legal_date if ctx else today,
        settings=settings,
        embedder=embedder,
        document_keys=ctx.document_keys if ctx else None,
        scenario_citation_ids=ctx.citation_ids if ctx else (),
    )
    if not outcome.sufficient:
        plan.kind = "insufficient"
        return plan

    limit = settings.MENTOR_MAX_SOURCES
    reranker = get_reranker(settings, llm)
    use_rerank = (
        llm is not None
        and not isinstance(reranker, NullReranker)
        and len(outcome.candidates) > limit
    )
    pool = select_candidates(outcome.candidates, max(settings.RERANK_CANDIDATES, limit)) if use_rerank else None
    chosen = pool if pool is not None else select_candidates(outcome.candidates, limit)
    views = {c.article_id: get_article_view(db, c.article_id, language) for c in chosen}
    chunk_texts = dict(
        db.execute(select(Chunk.id, Chunk.text).where(Chunk.id.in_([c.chunk_id for c in chosen]))).all()
    )
    if pool is not None:
        items = [
            RerankItem(
                id=f"r{i}",
                document=views[c.article_id].document_title,
                article_number=views[c.article_id].article_number,
                article_title=views[c.article_id].article_title,
                text=strip_header(chunk_texts.get(c.chunk_id) or views[c.article_id].text),
                exact=c.exact,
                scenario=c.scenario,
                ref=c,
            )
            for i, c in enumerate(pool, start=1)
        ]
        ranked = reranker.rerank(question, items)
        plan.reranked = True
        chosen = select_candidates([it.ref for it in ranked], limit)
    prompt_sources: list[SourceForPrompt] = []
    for i, cand in enumerate(chosen, start=1):
        sid = f"c{i}"
        view = views[cand.article_id]
        plan.sources_payload.append({"source_id": sid, "citation": view.model_dump(mode="json")})
        plan.source_articles[sid] = view.article_number
        prompt_sources.append(
            SourceForPrompt(
                source_id=sid,
                citation=f"{view.document_title}, {_article_label(language, view.article_number)}",
                url=view.source_url,
                text=strip_header(chunk_texts.get(cand.chunk_id) or view.text),
            )
        )
    plan.system = build_mentor_system(language)
    plan.user_message = build_mentor_user(
        question=question,
        sources=prompt_sources,
        session_context=ctx.text if ctx else None,
        history=_history(req),
    )
    return plan


def _sse_done(language: Locale, **fields: Any) -> dict[str, Any]:
    return {"disclaimer": msg("disclaimer", language), **fields}


def _call_mentor(llm: LLM, settings: Settings, plan: MentorPlan) -> MentorAnswer | None:
    try:
        return llm.structured(
            model=settings.LLM_MODEL_MENTOR,
            system=plan.system,
            messages=[{"role": "user", "content": plan.user_message}],
            output_model=MentorAnswer,
            max_tokens=OLLAMA_MENTOR_MAX_TOKENS if settings.LLM_PROVIDER == "ollama" else MENTOR_MAX_TOKENS,
            timeout=settings.mentor_timeout,
            effort=settings.LLM_MENTOR_EFFORT,
        )
    except Exception:  # noqa: BLE001 - любая ошибка модели = «AI недоступен», а не 500
        log.exception("наставник: вызов модели упал")
        return None


def stream_events(
    plan: MentorPlan,
    llm: LLM | None,
    settings: Settings,
    record: Callable[[dict[str, Any]], None],
) -> Iterator[Event]:
    """События SSE по порядку: sources → block* → done (или один error)."""
    lang = plan.language
    stats: dict[str, Any] = {
        "question": plan.question,
        "detected_language": lang,
        "category": plan.category,
        "sources_count": len(plan.sources_payload),
        "insufficient": False,
        "ai_unavailable": False,
        "blocks_kept": 0,
        "blocks_dropped": 0,
        "session_id": plan.session_id,
        "reranked": plan.reranked,
    }

    if plan.kind == "error":
        code, message = plan.error or ("INTERNAL_ERROR", "Ошибка")
        yield "error", {"code": code, "message": message}
        return

    if plan.kind == "out_of_scope":
        yield "sources", []
        record(stats)
        yield "done", _sse_done(
            lang,
            insufficient_sources=False,
            ai_unavailable=False,
            out_of_scope=True,
            message=msg("out_of_scope", lang),
        )
        return

    if plan.kind == "insufficient":
        stats["insufficient"] = True
        yield "sources", []
        record(stats)
        yield "done", _sse_done(
            lang, insufficient_sources=True, ai_unavailable=False, message=msg("insufficient", lang)
        )
        return

    yield "sources", plan.sources_payload

    answer = _call_mentor(llm, settings, plan) if llm is not None else None
    if answer is None:
        stats["ai_unavailable"] = True
        record(stats)
        yield "done", _sse_done(
            lang, insufficient_sources=False, ai_unavailable=True, message=msg("ai_unavailable", lang)
        )
        return

    result = validate_blocks(answer.answer_blocks, plan.source_articles)
    stats["blocks_kept"] = len(result.kept)
    stats["blocks_dropped"] = result.dropped
    insufficient = answer.insufficient_sources or not result.kept
    stats["insufficient"] = insufficient
    record(stats)
    for block in result.kept:
        yield "block", {"text": block.text, "source_ids": block.source_ids, "verified": block.verified}
    if insufficient:
        yield "done", _sse_done(
            lang, insufficient_sources=True, ai_unavailable=False, message=msg("insufficient", lang)
        )
    else:
        yield "done", _sse_done(lang, insufficient_sources=False, ai_unavailable=False)
