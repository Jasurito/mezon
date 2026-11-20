"""Reranker: пересортировка кандидатов гибридного поиска по релевантности вопросу.

Шаг идёт после RRF и до отбора источников для наставника (ARCHITECTURE.md §5.1).
Сейчас есть две реализации: ``NullReranker`` (порядок RRF) и ``LLMReranker`` (одна
структурированная просьба к быстрой модели). Любой сбой = исходный порядок.

Точка расширения: cross-encoder (например bge-reranker-v2-m3 локально или hosted rerank API)
реализуйте как класс с методом ``rerank`` и добавьте фабрику в ``RERANKERS`` под значением
переменной RERANKER (расширив Literal в Settings). Реализации cross-encoder здесь нет.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Protocol

from pydantic import BaseModel

from app.ai.llm import LLM
from app.ai.prompts.rerank import RERANK_SYSTEM, CandidateForPrompt, build_rerank_user
from app.config import Settings

log = logging.getLogger("adolat.rag")

SNIPPET_LIMIT = 400
MAX_SCORE = 3


@dataclass
class RerankItem:
    """Кандидат для reranker'а: данные для оценки плюс ссылка на исходный объект пайплайна."""

    id: str
    document: str
    article_number: str
    article_title: str | None
    text: str
    exact: bool = False  # явная ссылка на статью: всегда первым
    scenario: bool = False  # кандидат сценария: не опускается ниже исходной позиции
    ref: Any = None


class Reranker(Protocol):
    def rerank(self, question: str, candidates: Sequence[RerankItem]) -> list[RerankItem]:
        """Те же кандидаты в новом порядке. Ничего не теряет и не добавляет."""
        ...


class NullReranker:
    """Порядок без изменений (порядок RRF)."""

    def rerank(self, question: str, candidates: Sequence[RerankItem]) -> list[RerankItem]:
        return list(candidates)


class RerankScore(BaseModel):
    id: str
    score: int


class RerankScores(BaseModel):
    # Без ограничений в схеме: она уходит в structured output; значения нормализуются в коде.
    scores: list[RerankScore]


def order_by_scores(candidates: Sequence[RerankItem], scores: dict[str, float]) -> list[RerankItem]:
    """Порядок по оценке (убыв.), при равенстве исходный. Точные ссылки первыми; кандидаты
    сценария не оказываются ниже своей исходной позиции."""
    pos = {c.id: i for i, c in enumerate(candidates)}
    exact = [c for c in candidates if c.exact]
    rest = sorted((c for c in candidates if not c.exact), key=lambda c: (-scores[c.id], pos[c.id]))
    result = exact + rest
    for c in candidates:  # в исходном порядке: ранее поднятые не сдвигаются
        if c.exact or not c.scenario:
            continue
        cur = result.index(c)
        if cur > pos[c.id]:
            result.insert(pos[c.id], result.pop(cur))
    return result


class LLMReranker:
    def __init__(self, llm: LLM, settings: Settings) -> None:
        self._llm = llm
        self._settings = settings

    def rerank(self, question: str, candidates: Sequence[RerankItem]) -> list[RerankItem]:
        items = list(candidates)
        if len(items) < 2:
            return items
        try:
            scores = self._scores(question, items)
        except Exception:  # noqa: BLE001 - reranker не должен ронять ответ
            log.exception("reranker: вызов модели упал, порядок RRF")
            return items
        if scores is None:
            return items
        return order_by_scores(items, scores)

    def _scores(self, question: str, items: list[RerankItem]) -> dict[str, float] | None:
        prompt = [
            CandidateForPrompt(
                id=c.id,
                document=c.document,
                article_number=c.article_number,
                article_title=c.article_title,
                snippet=c.text[:SNIPPET_LIMIT],
            )
            for c in items
        ]
        timeout = self._settings.RERANK_TIMEOUT
        resp = self._llm.structured(
            model=self._settings.LLM_MODEL_FAST,
            system=RERANK_SYSTEM,
            messages=[{"role": "user", "content": build_rerank_user(question, prompt)}],
            output_model=RerankScores,
            max_tokens=128 + 24 * len(items),
            timeout=timeout if timeout is not None else self._settings.fast_timeout,
            effort="low",
            thinking_disabled=True,
        )
        if resp is None:
            log.warning("reranker: модель недоступна, порядок RRF")
            return None
        known = {c.id for c in items}
        given: dict[str, float] = {}
        for s in resp.scores:
            if s.id in known and s.id not in given:
                given[s.id] = float(min(max(s.score, 0), MAX_SCORE))
        if not given:
            log.warning("reranker: в ответе нет известных id, порядок RRF")
            return None
        # Недостающие id наследуют оценку ближайшего предыдущего (иначе следующего) оценённого
        # кандидата: их место определяется исходным порядком.
        result: dict[str, float] = {}
        last: float | None = None
        for c in items:
            if c.id in given:
                last = given[c.id]
                result[c.id] = last
            elif last is not None:
                result[c.id] = last
        first_known = next(given[c.id] for c in items if c.id in given)
        for c in items:
            result.setdefault(c.id, first_known)
        return result


RERANKERS: dict[str, Callable[[Settings, LLM | None], Reranker]] = {}


def _llm_factory(settings: Settings, llm: LLM | None) -> Reranker:
    if llm is None:
        return NullReranker()
    return LLMReranker(llm, settings)


RERANKERS["llm"] = _llm_factory


def get_reranker(settings: Settings, llm: LLM | None) -> Reranker:
    factory = RERANKERS.get(settings.RERANKER)
    if factory is None:  # "none" и незарегистрированные значения
        return NullReranker()
    return factory(settings, llm)
