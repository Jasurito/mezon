"""NPC со свободными вопросами. Движок хранит факты (источник истины), LLM только подбирает
вопрос и перефразирует факты голосом персонажа. Любая неудача ведёт к заготовленному ответу."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from pydantic import create_model

from app.ai.llm import LLM
from app.ai.messages import LANGUAGE_NAMES, msg
from app.ai.prompts.npc import (
    NPC_CLASSIFY_SYSTEM,
    build_classify_user,
    build_rephrase_system,
    build_rephrase_user,
)
from app.config import Settings
from app.game_engine.engine import RESULTS
from app.i18n import translate
from app.rag.normalize import normalize, tokenize
from app.rag.retrieve import prefix_stem
from app.rag.stopwords import content_tokens
from app.scenarios.loader import LoadedScenario
from app.schemas.legal import Locale
from app.schemas.npc import NpcClassification, NpcReply
from app.schemas.scenario import NpcQuestion

log = logging.getLogger("adolat.ai")

UNKNOWN = "unknown"
MAX_ANSWER_CHARS = 400
_NUMBER = re.compile(r"\d+")


@dataclass
class NpcResult:
    text: str
    question_id: str
    fact_ids: list[str]
    ai_generated: bool


def allowed_questions(loaded: LoadedScenario, character_id: str, stage: str) -> list[NpcQuestion]:
    """Вопросы персонажа, доступные на этапе (пустой ``stages`` = любой этап, кроме RESULTS)."""
    if stage == RESULTS:
        return []
    return [
        q
        for q in loaded.scenario.npc_questions
        if q.character_id == character_id and (not q.stages or stage in q.stages)
    ]


# --------------------------------------------------------------------------- без AI: лексика


def _tokens(text: str, locale: Locale) -> list[str]:
    return content_tokens(tokenize(normalize(text, locale)), locale)


def _same_word(a: str, b: str) -> bool:
    if a == b:
        return True
    sa, sb = prefix_stem(a), prefix_stem(b)
    if sa == sb:
        return True
    return (len(sa) >= 3 and b.startswith(sa)) or (len(sb) >= 3 and a.startswith(sb))


def classify_lexical(
    loaded: LoadedScenario, questions: list[NpcQuestion], text: str, locale: Locale
) -> str:
    """Вопрос с наибольшим числом совпавших токенов (≥ 2, либо ≥ 1 при одном значимом слове) или unknown."""
    query = _tokens(text, locale)
    if not query:
        return UNKNOWN
    need = 1 if len(query) == 1 else 2
    best_id, best_score = UNKNOWN, 0
    for q in questions:
        source = translate(loaded, q.label_key, locale)
        if q.keywords_key:
            source += ", " + translate(loaded, q.keywords_key, locale)
        words = _tokens(source, locale)
        score = sum(1 for t in query if any(_same_word(t, w) for w in words))
        if score > best_score:
            best_id, best_score = q.question_id, score
    return best_id if best_score >= need else UNKNOWN


# --------------------------------------------------------------------------- с AI


@lru_cache(maxsize=256)
def _choice_model(ids: tuple[str, ...]):
    """Модель вывода, где question_id ограничен enum из допустимых id и "unknown"."""
    literal = Literal[(*ids, UNKNOWN)]  # type: ignore[valid-type]
    return create_model("NpcClassificationChoice", __base__=NpcClassification, question_id=(literal, ...))


def classify_llm(
    llm: LLM,
    settings: Settings,
    loaded: LoadedScenario,
    questions: list[NpcQuestion],
    text: str,
    locale: Locale,
) -> str | None:
    """question_id, "unknown" либо None, если модель недоступна."""
    model = _choice_model(tuple(q.question_id for q in questions))
    labels = [(q.question_id, translate(loaded, q.label_key, locale)) for q in questions]
    try:
        result = llm.structured(
            model=settings.LLM_MODEL_FAST,
            system=NPC_CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": build_classify_user(text, labels)}],
            output_model=model,
            max_tokens=128,
            timeout=settings.fast_timeout,
            effort="low",
            thinking_disabled=True,
        )
    except Exception:  # noqa: BLE001 - сбой модели не должен ронять ответ
        log.exception("NPC: классификация упала")
        return None
    if result is None:
        return None
    qid = getattr(result, "question_id", None)
    return qid if qid in {q.question_id for q in questions} else UNKNOWN


def _numbers(text: str) -> set[str]:
    return set(_NUMBER.findall(text))


def valid_reply(text: str, fact_texts: list[str]) -> bool:
    """Не пусто, не длиннее лимита, все числа ответа есть в текстах фактов."""
    if not text or len(text) > MAX_ANSWER_CHARS:
        return False
    allowed: set[str] = set()
    for f in fact_texts:
        allowed |= _numbers(f)
    return _numbers(text) <= allowed


def rephrase(
    llm: LLM,
    settings: Settings,
    *,
    name: str,
    role: str,
    text: str,
    fact_texts: list[str],
    locale: Locale,
) -> str | None:
    """Ответ персонажа своими словами или None (сбой модели либо ответ не прошёл проверку)."""
    try:
        result = llm.structured(
            model=settings.LLM_MODEL_FAST,
            system=build_rephrase_system(LANGUAGE_NAMES[locale]),
            messages=[
                {
                    "role": "user",
                    "content": build_rephrase_user(name=name, role=role, text=text, facts=fact_texts),
                }
            ],
            output_model=NpcReply,
            max_tokens=300,
            timeout=settings.fast_timeout,
            effort="low",
            thinking_disabled=True,
        )
    except Exception:  # noqa: BLE001
        log.exception("NPC: перефраз упал")
        return None
    if result is None:
        return None
    reply = " ".join(result.text.split())
    if not valid_reply(reply, fact_texts):
        log.warning("NPC: ответ модели не прошёл проверку")
        return None
    return reply


# --------------------------------------------------------------------------- вход


def answer_question(
    loaded: LoadedScenario,
    *,
    character_id: str,
    stage: str,
    text: str,
    locale: Locale,
    llm: LLM | None,
    settings: Settings,
) -> NpcResult:
    questions = allowed_questions(loaded, character_id, stage)
    unknown = NpcResult(msg("npc_unknown", locale), UNKNOWN, [], False)
    if not questions:
        return unknown

    qid: str | None = None
    if llm is not None:
        qid = classify_llm(llm, settings, loaded, questions, text, locale)
    if qid is None:
        qid = classify_lexical(loaded, questions, text, locale)
    question = next((q for q in questions if q.question_id == qid), None)
    if question is None:
        return unknown

    fact_by_id = {f.id: f for f in loaded.scenario.facts}
    fact_texts = [translate(loaded, fact_by_id[f].text_key, locale) for f in question.fact_ids]
    scripted = NpcResult(translate(loaded, question.answer_key, locale), qid, list(question.fact_ids), False)
    if llm is None:
        return scripted
    character = next(c for c in loaded.scenario.characters if c.id == character_id)
    reply = rephrase(
        llm,
        settings,
        name=translate(loaded, character.name_key, locale),
        role=translate(loaded, character.role_key, locale),
        text=text,
        fact_texts=fact_texts,
        locale=locale,
    )
    if reply is None:
        return scripted
    return NpcResult(reply, qid, list(question.fact_ids), True)
