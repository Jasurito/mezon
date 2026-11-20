"""Поиск для GET /api/legal/search: пайплайн + данные для выдачи (без LLM)."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.legal import Article, Chunk, Citation, DocumentVersion, LegalDocument
from app.rag.embedder import Embedder
from app.rag.language import detect_language
from app.rag.normalize import APOS_TABLE, base_normalize, tokenize
from app.rag.pipeline import Candidate, SearchOutcome, hybrid_search
from app.schemas.legal import Locale
from app.schemas.rag import SearchMatch, SearchResponse, SearchResultItem

SNIPPET_MAX = 300
_HEADER = re.compile(r"^\s*\[[^\]]*\]\s*")


def doc_title(doc: LegalDocument, locale: str) -> str:
    titles = doc.title or {}
    for key in (locale, "ru"):
        if titles.get(key):
            return titles[key]
    for value in titles.values():
        if value:
            return value
    return doc.document_key


def strip_header(chunk_text: str) -> str:
    """Заголовок чанка «[Документ · Статья N · …]» в выдачу не попадает."""
    return _HEADER.sub("", chunk_text, count=1)


def make_snippet(chunk_text: str, tokens: Sequence[str], limit: int = SNIPPET_MAX) -> str:
    """Дословный фрагмент вокруг первого совпавшего слова, не длиннее ``limit`` символов."""
    body = " ".join(strip_header(chunk_text).split())
    if len(body) <= limit:
        return body
    # Нормализация побуквенная (1:1), поэтому позиции в lowered совпадают с body.
    lowered = body.translate(APOS_TABLE).lower()
    pos = -1
    for t in tokens:
        i = lowered.find(t)
        if i != -1 and (pos == -1 or i < pos):
            pos = i
    start = 0 if pos == -1 else max(0, pos - limit // 3)
    if start > 0:
        space = body.find(" ", start)
        start = space + 1 if 0 <= space < start + 30 else start
    prefix = "…" if start > 0 else ""
    room = limit - len(prefix) - 1
    end = start + room
    if end >= len(body):
        return prefix + body[start:]
    cut = body.rfind(" ", start, end)
    if cut > start + room // 2:
        end = cut
    return prefix + body[start:end].rstrip() + "…"


def _parts_label(part_from: int | None, part_to: int | None) -> str | None:
    if part_from is None:
        return None
    if part_to is None or part_to == part_from:
        return str(part_from)
    return f"{part_from}–{part_to}"


def load_items(
    db: Session, candidates: Sequence[Candidate], query: str, locale: str
) -> list[SearchResultItem]:
    if not candidates:
        return []
    ids = [c.chunk_id for c in candidates]
    rows = db.execute(
        select(Chunk, Article, DocumentVersion, LegalDocument)
        .join(Article, Article.id == Chunk.article_id)
        .join(DocumentVersion, DocumentVersion.id == Article.version_id)
        .join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
        .where(Chunk.id.in_(ids))
    ).all()
    by_id = {r[0].id: r for r in rows}
    doc_ids = {r[3].id for r in rows}
    cit = {}
    for c in db.scalars(
        select(Citation)
        .where(Citation.document_id.in_(doc_ids))
        .order_by(Citation.part.is_not(None), Citation.citation_id)
    ):
        cit.setdefault((c.document_id, c.article_number), c.citation_id)  # без части приоритетнее

    tokens = tokenize(base_normalize(query))
    out: list[SearchResultItem] = []
    for cand in candidates:
        row = by_id.get(cand.chunk_id)
        if row is None:
            continue
        chunk, article, version, doc = row
        out.append(
            SearchResultItem(
                chunk_id=chunk.id,
                article_id=article.id,
                citation_id=cit.get((doc.id, article.article_number)),
                document_title=doc_title(doc, locale),
                article_number=article.article_number,
                article_title=article.article_title,
                parts=_parts_label(chunk.part_from, chunk.part_to),
                snippet=make_snippet(chunk.text, tokens),
                edition_status="current" if version.effective_to is None else "historical",
                source_url=version.source_url or doc.source_url,
                score=round(cand.score, 6),
                match=SearchMatch(
                    exact_article=cand.exact, dense_rank=cand.dense_rank, sparse_rank=cand.sparse_rank
                ),
            )
        )
    return out


def search_legal(
    db: Session,
    *,
    query: str,
    locale: Locale | None,
    on_date: date,
    limit: int,
    settings: Settings,
    embedder: Embedder | None,
) -> SearchResponse:
    detected = detect_language(query)
    use_locale = locale or detected
    outcome: SearchOutcome = hybrid_search(
        db, query=query, locale=use_locale, on_date=on_date, settings=settings, embedder=embedder
    )
    items: list[SearchResultItem] = []
    if outcome.sufficient:
        items = load_items(db, outcome.candidates[:limit], query, use_locale)
    return SearchResponse(query=query, detected_language=detected, date=on_date, results=items)
