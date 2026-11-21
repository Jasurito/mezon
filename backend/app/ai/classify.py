"""Классификация вопроса быстрой моделью. Любая неудача = "concept": поиск идёт как обычно."""

from __future__ import annotations

import logging
import re

from app.ai.llm import LLM
from app.ai.prompts import CLASSIFY_SYSTEM, sanitize_text
from app.config import Settings
from app.rag.normalize import base_normalize
from app.rag.refs import extract_article_numbers
from app.schemas.rag import QueryClassification

log = logging.getLogger("adolat.ai")

DEFAULT_CATEGORY = "concept"


# Слова о своём деле (ru/uz), в нормализованном виде (нижний регистр, ё→е).
_CASE_RE = re.compile(
    r"(?<!\w)(?:я|мой|моя|мое|мои|моего|моему|моем|мною|мне|меня|проиграл\w*|выиграл\w*|"
    r"почему\s+суд|men|mening|menga|meni|yutqazdim|yutdim|nega\s+sud)(?!\w)",
    re.IGNORECASE,
)


def classify_by_rules(question: str, has_session: bool) -> str:
    """Без LLM: ссылка на статью → article_lookup; вопрос о своём деле при сессии → case_specific;
    иначе concept. out_of_scope отсекает порог поиска (insufficient_sources)."""
    if extract_article_numbers(question):
        return "article_lookup"
    if has_session and _CASE_RE.search(base_normalize(question)) is not None:
        return "case_specific"
    return DEFAULT_CATEGORY


def classify_question(
    llm: LLM | None, settings: Settings, question: str, has_session: bool = False
) -> str:
    if settings.MENTOR_CLASSIFIER == "rules":
        return classify_by_rules(question, has_session)
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
