"""Классификация вопроса быстрой моделью. Любая неудача = "concept": поиск идёт как обычно."""

from __future__ import annotations

import logging

from app.ai.llm import LLM
from app.ai.prompts import CLASSIFY_SYSTEM, sanitize_text
from app.config import Settings
from app.schemas.rag import QueryClassification

log = logging.getLogger("adolat.ai")

DEFAULT_CATEGORY = "concept"


def classify_question(llm: LLM | None, settings: Settings, question: str) -> str:
    if llm is None:
        return DEFAULT_CATEGORY
    try:
        result = llm.structured(
            model=settings.LLM_MODEL_FAST,
            system=CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": f"<question>\n{sanitize_text(question)}\n</question>"}],
            output_model=QueryClassification,
            max_tokens=256,
            timeout=settings.fast_timeout,
            effort="low",
            thinking_disabled=True,
        )
    except Exception:  # noqa: BLE001 - классификация не должна ронять ответ
        log.exception("классификация вопроса упала")
        return DEFAULT_CATEGORY
    return result.category if result is not None else DEFAULT_CATEGORY
