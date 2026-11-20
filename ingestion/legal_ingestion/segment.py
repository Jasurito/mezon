"""Шаг 4. segment: блоки → преамбула, статьи, части (docs/INGESTION.md §4 шаг 4)."""

from __future__ import annotations

from typing import Any

from legal_ingestion.normalize import to_search
from legal_ingestion.patterns import (
    ARTICLE,
    CHAPTER,
    PARAGRAPH,
    PART,
    POINT,
    PREAMBLE,
    PREAMBLE_HEADING,
    REPEALED,
    SECTION,
    SUBSECTION,
    is_note,
    normalize_number,
)


class _Draft:
    """Статья в процессе сборки: части как списки строк (пункты приклеиваются к своей части)."""

    def __init__(
        self,
        number: str,
        title: str | None,
        section: str | None,
        chapter: str | None,
        first_idx: int,
        anchor: str | None = None,
    ):
        self.number = number
        self.anchor = anchor  # lex_id заголовка статьи на lex.uz: deep-link source_url#<anchor>
        self.title = title
        self.section = section
        self.chapter = chapter
        self.parts: list[dict[str, Any]] = []  # {"kind", "lines"}
        self.first_idx = first_idx
        self.last_idx = first_idx

    def add(self, block: dict[str, Any], language: str) -> None:
        text = block["text"]
        self.last_idx = block["idx"]
        if block["style"] == "note" or is_note(text, language):
            self.parts.append({"kind": "note", "lines": [text]})
        elif self.parts and POINT.match(text):
            self.parts[-1]["lines"].append(text)
        else:
            self.parts.append({"kind": "text", "lines": [text]})


def _structural(text: str, language: str) -> bool:
    return bool(
        ARTICLE[language].match(text)
        or CHAPTER[language].match(text)
        or SECTION[language].match(text)
        or PART[language].match(text)
        or SUBSECTION[language].match(text)
        or PARAGRAPH[language].match(text)
        or PREAMBLE_HEADING[language].match(text)
    )


def _finish(d: _Draft, document_key: str, language: str) -> dict[str, Any]:
    parts = [{"kind": p["kind"], "content": "\n".join(p["lines"])} for p in d.parts]
    status = "in_force"
    rep = REPEALED[language]
    if d.number != PREAMBLE:
        if (d.title and rep.match(d.title)) or (len(parts) == 1 and rep.match(parts[0]["content"])):
            status = "repealed"
        if status == "repealed" and not parts and d.title:
            parts = [{"kind": "text", "content": d.title}]  # «утратила силу» сохраняется текстом
    out_parts = [
        {
            "part_number": i,
            "kind": p["kind"],
            "content": p["content"],
            "content_normalized": to_search(p["content"], language),
        }
        for i, p in enumerate(parts, start=1)
    ]
    content = "\n".join(p["content"] for p in out_parts)
    return {
        "document_key": document_key,
        "language": language,
        "section": d.section,
        "chapter": d.chapter,
        "article_number": d.number,
        "article_title": d.title,
        "anchor": d.anchor,
        "parts": out_parts,
        "status": status,
        "content": content,
        "content_normalized": to_search(content, language),
        "source_blocks": [d.first_idx, d.last_idx],
    }


def segment(
    blocks: list[dict[str, Any]], language: str, document_key: str
) -> tuple[list[dict[str, Any]], list[str]]:
    """Вернуть (статьи в порядке документа, ошибки сегментации). Ошибка = редакцию загружать нельзя."""
    section: str | None = None
    chapter: str | None = None
    preamble = _Draft(PREAMBLE, None, None, None, blocks[0]["idx"] if blocks else 0)
    drafts: list[_Draft] = []
    current: _Draft | None = None
    issues: list[str] = []
    # Разметка lex.uz (style=clause): структура берётся только из заголовков, а не из любых абзацев
    lex = any(b["style"] == "clause" for b in blocks)
    i = 0
    while i < len(blocks):
        b = blocks[i]
        text = b["text"]
        style = b["style"]
        i += 1
        if style == "meta":  # форма и название акта
            continue
        if style == "footer":  # подпись, место, дата, номер акта: не часть последней статьи
            current = None
            continue
        head = style in ("heading", "clause") or not lex
        m_art = ARTICLE[language].match(text) if head else None
        m_sec = SECTION[language].match(text) if head else None
        m_chap = CHAPTER[language].match(text) if head else None
        if lex and style == "heading" and not drafts and PREAMBLE_HEADING[language].match(text):
            current = preamble
            preamble.first_idx = preamble.last_idx = b["idx"]
            preamble.anchor = b.get("lex_id")
        elif m_art:
            current = _Draft(m_art.group(1), m_art.group(2).strip() or None, section, chapter, b["idx"], b.get("lex_id"))
            drafts.append(current)
        elif m_sec or m_chap:
            m = m_sec or m_chap
            number = normalize_number(m.group(1), language)
            if m_sec:
                section, chapter = number, None
            else:
                chapter = number
            current = None  # текст между заголовком главы и следующей статьёй не принадлежит предыдущей статье
            # название главы/раздела на следующей строке
            nxt = blocks[i] if i < len(blocks) else None
            if not m.group(2).strip() and nxt and nxt["style"] == "heading" and not _structural(nxt["text"], language):
                i += 1
        elif head and (
            PART[language].match(text) or SUBSECTION[language].match(text) or PARAGRAPH[language].match(text)
        ):
            current = None  # часть кодекса, подраздел, параграф: ни section, ни chapter
        elif lex and style in ("heading", "clause"):
            current = None
            issues.append(f"блок {b['idx']}: неопознанный заголовок {text[:60]!r} (проверьте регулярки в patterns.py)")
        elif current is not None:
            current.add(b, language)
        elif lex:
            issues.append(f"блок {b['idx']}: текст вне статьи {text[:60]!r}")
        elif not drafts:
            preamble.add(b, language)

    articles: list[dict[str, Any]] = []
    if preamble.parts:
        articles.append(_finish(preamble, document_key, language))
    articles.extend(_finish(d, document_key, language) for d in drafts)

    seen: set[str] = set()
    for a in articles:
        n = a["article_number"]
        if n in seen:
            issues.append(f"повторяющийся номер статьи {n}")
        seen.add(n)
    if not drafts:
        issues.append("не найдено ни одной статьи (проверьте регулярки в patterns.py)")
    return articles, issues
