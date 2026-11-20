"""Защита от выдуманных статей: проверка блоков ответа наставника (ARCHITECTURE.md §5.5).

Правила для каждого блока:
1. каждый source_id должен быть среди выданных источников, иначе блок удаляется;
2. каждое упоминание статьи («ст. N», «статья N», «N-modda», «N-модда») должно совпадать
   с номером статьи одного из источников этого блока, иначе блок удаляется;
3. блок без source_ids, но с упоминанием статьи, удаляется (следствие правила 2);
4. блок без упоминаний статей и без source_ids допустим (общее пояснение).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from app.rag.refs import canonical_number, extract_article_numbers
from app.schemas.rag import MentorBlock

# Модели дублируют ссылки в тексте («… [c2]»); фронт рисует их сам по source_ids.
_INLINE_SOURCE_MARK = re.compile(r"\s*\[c\d+(?:\s*,\s*c\d+)*\]")


def strip_source_marks(text: str) -> str:
    return _INLINE_SOURCE_MARK.sub("", text).strip()


@dataclass(frozen=True)
class ValidatedBlock:
    text: str
    source_ids: list[str]
    verified: bool = True


@dataclass(frozen=True)
class ValidationResult:
    kept: list[ValidatedBlock]
    dropped: int


def validate_blocks(
    blocks: Sequence[MentorBlock], source_articles: Mapping[str, str]
) -> ValidationResult:
    """``source_articles``: source_id -> article_number выданных источников."""
    allowed = {sid: canonical_number(n) for sid, n in source_articles.items()}
    kept: list[ValidatedBlock] = []
    dropped = 0
    for block in blocks:
        text = strip_source_marks(block.text or "")
        ids = list(dict.fromkeys(block.source_ids or []))
        if not text or any(sid not in allowed for sid in ids):
            dropped += 1
            continue
        block_numbers = {allowed[sid] for sid in ids}
        if any(canonical_number(n) not in block_numbers for n in extract_article_numbers(text)):
            dropped += 1
            continue
        kept.append(ValidatedBlock(text=text, source_ids=ids, verified=True))
    return ValidationResult(kept, dropped)
