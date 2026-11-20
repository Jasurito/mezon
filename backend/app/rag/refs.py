"""Явные ссылки на статьи в тексте («ст. 15», «статья 15 ГК», «15-modda», «15-модда»).

Используется и поиском (точная ветка), и валидатором ответа наставника.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.rag.normalize import base_normalize

# Номер статьи: 15, 15-1 (вставленная), 15¹.
_NUM = r"\d+(?:[-–]\d+|[¹²³⁴⁵⁶⁷⁸⁹]+)?"
_NUM_LIST = rf"{_NUM}(?:\s*(?:,|;|и|или|и\s+также)\s*{_NUM})*"

# «ст. 15», «ст.15», «ст.ст. 15, 16», «статья 15», «статьи 15», «статье 15», «статью 15», «статьей 15».
_RU = re.compile(
    rf"(?<!\w)(?:ст(?:\.\s*ст)?\.?|стать(?:я|и|е|ю|ей|ям|ями|ях))\s*№?\s*(?P<nums>{_NUM_LIST})",
    re.IGNORECASE,
)
# «15-modda», «15 modda», «15-moddaga», «15-модда», «15-моддага».
_UZ = re.compile(
    rf"(?<![\d\w])(?P<nums>{_NUM})\s*[-–]?\s*(?:modda|модда)\w*",
    re.IGNORECASE,
)
_NUM_RE = re.compile(_NUM)


@dataclass(frozen=True)
class DocHint:
    name: str
    aliases: frozenset[str]  # варианты document_key (регистр не важен, допускается префикс «TEST_»)
    title_needles: tuple[str, ...]  # подстроки нормализованного названия документа


DOC_HINTS: tuple[tuple[DocHint, re.Pattern[str]], ...] = (
    (
        DocHint("civil_procedure", frozenset({"GPK", "CPC", "FPK"}),
                ("гражданский процессуальный", "fuqarolik protsessual")),
        re.compile(r"(?<!\w)(?:гпк|гражданск\w*\s+процессуальн\w*|fpk|fuqarolik\s+protsessual\w*)(?!\w)", re.I),
    ),
    (
        DocHint("civil", frozenset({"GK", "CC", "FK", "CIVIL"}),
                ("гражданский кодекс", "fuqarolik kodeksi")),
        re.compile(r"(?<!\w)(?:гк|гражданск\w*\s+кодекс\w*|fk|fuqarolik\s+kodeks\w*)(?!\w)", re.I),
    ),
    (
        DocHint("consumer", frozenset({"CPRL", "ZPP"}),
                ("защите прав потребителей", "istemolchilar", "isteʻmolchilar")),
        re.compile(
            r"(?<!\w)(?:о\s+защите\s+прав\s+потребител\w*|закон\w*\s+о\s+защите\s+прав|зозпп|"
            r"iste['ʻ’]?molchilar\w*|истеъмолчилар\w*)",
            re.I,
        ),
    ),
    (
        DocHint("constitution", frozenset({"CONST", "CONSTITUTION"}),
                ("конституция", "konstitutsiya")),
        re.compile(r"(?<!\w)(?:конституци\w*|konstitutsiya\w*|конституция\w*)", re.I),
    ),
)


@dataclass(frozen=True)
class ArticleRef:
    hint: str | None  # имя подсказки документа (DocHint.name) или None
    number: str


def canonical_number(n: str) -> str:
    """15–1 → 15-1; надстрочные цифры сохраняются как есть."""
    return n.strip().replace("–", "-").replace("‑", "-")


def _numbers(group: str) -> list[str]:
    return [canonical_number(m) for m in _NUM_RE.findall(group)]


def _hint_in(window: str) -> str | None:
    best: tuple[int, str] | None = None
    for hint, pattern in DOC_HINTS:
        m = pattern.search(window)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), hint.name)
    return best[1] if best else None


def extract_article_numbers(text: str) -> list[str]:
    """Номера статей, упомянутые в тексте (без подсказок документов). Порядок сохраняется."""
    out: list[str] = []
    for rx in (_RU, _UZ):
        for m in rx.finditer(text):
            out.extend(_numbers(m.group("nums")))
    return list(dict.fromkeys(out))


def extract_refs(text: str) -> list[ArticleRef]:
    """Явные ссылки на статьи с необязательной подсказкой документа («ст. 15 ГК»)."""
    matches = sorted(
        (m for rx in (_RU, _UZ) for m in rx.finditer(text)), key=lambda m: m.start()
    )
    refs: list[ArticleRef] = []
    for i, m in enumerate(matches):
        nxt = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        prev_end = matches[i - 1].end() if i else 0
        after = text[m.end(): min(nxt, m.end() + 40)]
        # Подсказка документа сразу после номера («ст. 15 ГК», «15-modda FK»), иначе перед ним
        # («в ГПК ст. 15»).
        hint = _hint_in(after) or _hint_in(text[max(prev_end, m.start() - 25): m.start()])
        for n in _numbers(m.group("nums")):
            refs.append(ArticleRef(hint, n))
    return list(dict.fromkeys(refs))


def matches_document(hint_name: str, document_key: str, titles: list[str]) -> bool:
    """Подходит ли документ под подсказку: по ключу (ГК/CC…) или по названию."""
    hint = next((h for h, _ in DOC_HINTS if h.name == hint_name), None)
    if hint is None:
        return False
    key = document_key.upper()
    if any(key == a or key.endswith("_" + a) for a in hint.aliases):
        return True
    normalized = [base_normalize(t) for t in titles]
    needles = [base_normalize(n) for n in hint.title_needles]
    return any(n in t for n in needles for t in normalized)
