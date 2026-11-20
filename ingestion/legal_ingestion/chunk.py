"""Шаг 6. chunk: статьи → чанки с заголовком (docs/INGESTION.md §4 шаг 6).

Формат заголовка совпадает с backend/tests/fixtures/rag_seed.py; бэкенд вырезает его из сниппета
регуляркой ``^\\s*\\[[^\\]]*\\]\\s*`` (app.rag.search.strip_header), поэтому внутри заголовка нет «]».
"""

from __future__ import annotations

import math
from datetime import date
from typing import Any

from legal_ingestion.normalize import to_search
from legal_ingestion.patterns import PREAMBLE

MAX_TOKENS = 800
_PREAMBLE_LABEL = {"ru": "Преамбула", "uz-Latn": "Preambula", "uz-Cyrl": "Преамбула"}


def estimate_tokens(text: str) -> int:
    """Грубая оценка без токенайзера: слова × 1.3."""
    return math.ceil(len(text.split()) * 1.3)


def doc_title_for(titles: dict[str, str], language: str, document_key: str) -> str:
    return titles.get(language) or titles.get("ru") or document_key


def _clean(s: str) -> str:
    return s.replace("[", "(").replace("]", ")")


def article_label(number: str, language: str) -> str:
    if number == PREAMBLE:
        return _PREAMBLE_LABEL.get(language, "Preamble")
    if language == "ru":
        return f"Статья {number}"
    return f"{number}-modda" if language == "uz-Latn" else f"{number}-модда"


def make_header(
    doc_title: str, article: dict[str, Any], p_from: int, p_to: int, effective_from: date | str, language: str
) -> str:
    label = article_label(article["article_number"], language)
    if article["article_number"] == PREAMBLE:
        head = label
    else:
        head = f"{label}. {article['article_title'] or ''}".strip()
    parts = f" · части {p_from}" + (f"–{p_to}" if p_to != p_from else "")
    return "[" + _clean(f"{doc_title} · {head}{parts} · редакция от {effective_from} · {language}") + "]"


def build_chunks(
    articles: list[dict[str, Any]],
    *,
    doc_title: str,
    language: str,
    effective_from: date | str,
    max_tokens: int = MAX_TOKENS,
) -> list[dict[str, Any]]:
    """Одна статья = один чанк, если влезает в max_tokens; иначе группы частей. Часть не разрывается."""
    chunks: list[dict[str, Any]] = []
    for art in articles:
        parts = art["parts"]
        if not parts:
            continue
        groups: list[list[dict[str, Any]]] = []
        cur: list[dict[str, Any]] = []
        for part in parts:
            cand = [*cur, part]
            if cur and _tokens(doc_title, art, cand, effective_from, language) > max_tokens:
                groups.append(cur)
                cur = [part]
            else:
                cur = cand
        groups.append(cur)
        for g in groups:
            text = _text(doc_title, art, g, effective_from, language)
            chunks.append(
                {
                    "document_key": art["document_key"],
                    "language": language,
                    "article_number": art["article_number"],
                    "part_from": g[0]["part_number"],
                    "part_to": g[-1]["part_number"],
                    "text": text,
                    "text_normalized": to_search(text, language),
                    "token_count": estimate_tokens(text),
                }
            )
    return chunks


def _text(doc_title: str, art: dict[str, Any], group: list[dict[str, Any]], eff: date | str, language: str) -> str:
    header = make_header(doc_title, art, group[0]["part_number"], group[-1]["part_number"], eff, language)
    return header + "\n" + "\n".join(p["content"] for p in group)


def _tokens(doc_title: str, art: dict[str, Any], group: list[dict[str, Any]], eff: date | str, language: str) -> int:
    return estimate_tokens(_text(doc_title, art, group, eff, language))
