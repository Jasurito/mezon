"""Legal corpus lookup: citation → article → edition valid on a date.

Contract used by the game API (scenario intro, results, startup checks) and later by RAG.
Signatures are fixed; implementations live here.
"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.legal.messages import fallback_language_note, unconfirmed_note
from app.models.legal import Article, ArticlePart, Citation, DocumentVersion, LegalDocument
from app.schemas.legal import (
    ArticlePartView,
    CitationView,
    EditionView,
    LegalActView,
    Locale,
)

_NOT_FOUND = "Статья не найдена"


def _title(doc: LegalDocument, locale: str) -> str:
    titles = doc.title or {}
    for key in (locale, "ru"):
        if titles.get(key):
            return titles[key]
    for value in titles.values():
        if value:
            return value
    return doc.document_key


def _is_valid_on(v: DocumentVersion, on_date: date) -> bool:
    if v.effective_from is None or v.effective_from > on_date:
        return False
    return v.effective_to is None or on_date < v.effective_to


def _pick(versions: list[DocumentVersion], locale: str) -> tuple[DocumentVersion, bool] | None:
    """Prefer the locale; else the official text. Returns (version, is_fallback)."""
    ordered = sorted(versions, key=lambda v: (v.effective_from or date.min, v.id), reverse=True)
    for v in ordered:
        if v.language == locale:
            return v, False
    for v in ordered:
        if v.is_official_text:
            return v, True
    return None


def _build(
    db: Session,
    citation_id: str | None,
    doc: LegalDocument,
    version: DocumentVersion,
    article: Article,
    part: int | None,
    locale: str,
    edition: EditionView,
    is_official: bool | None,
    note: str | None,
) -> CitationView:
    parts = list(
        db.scalars(
            select(ArticlePart)
            .where(ArticlePart.article_id == article.id)
            .order_by(ArticlePart.part_number)
        )
    )
    text = article.content
    if part is not None:
        match = next((p for p in parts if p.part_number == part), None)
        if match is None:
            raise NotFoundError(
                _NOT_FOUND, details={"citation_id": citation_id, "part": part}
            )
        text = match.content
    return CitationView(
        citation_id=citation_id,
        article_id=article.id,
        document_key=doc.document_key,
        document_title=_title(doc, locale),
        document_type=doc.document_type or "",
        document_number=doc.document_number,
        article_number=article.article_number,
        article_title=article.article_title,
        chapter=article.chapter,
        part=part,
        parts=[ArticlePartView(part_number=p.part_number, kind=p.kind, text=p.content) for p in parts],
        text=text,
        language=version.language,
        is_official_text=is_official,
        edition=edition,
        source_url=version.source_url or doc.source_url,
        last_verified_at=version.last_verified_at,
        translation_note=note,
    )


def missing_citation_ids(db: Session, citation_ids: Iterable[str]) -> set[str]:
    """Return the ids that are not in ``citations`` or whose article exists in no version."""
    ids = set(citation_ids)
    if not ids:
        return set()
    rows = db.execute(
        select(Citation.citation_id, Citation.document_id, Citation.article_number).where(
            Citation.citation_id.in_(ids)
        )
    ).all()
    missing = ids - {r.citation_id for r in rows}
    if rows:
        existing = set(
            db.execute(
                select(DocumentVersion.document_id, Article.article_number)
                .join(Article, Article.version_id == DocumentVersion.id)
                .where(
                    DocumentVersion.document_id.in_({r.document_id for r in rows}),
                    Article.article_number.in_({r.article_number for r in rows}),
                )
                .distinct()
            ).all()
        )
        for r in rows:
            if (r.document_id, r.article_number) not in existing:
                missing.add(r.citation_id)
    return missing


def get_citation_view(db: Session, citation_id: str, on_date: date, locale: Locale) -> CitationView:
    """Resolve one citation for ``on_date`` in ``locale``. Raises NotFoundError."""
    details = {"citation_id": citation_id}
    citation = db.get(Citation, citation_id)
    if citation is None:
        raise NotFoundError(_NOT_FOUND, details=details)
    doc = db.get(LegalDocument, citation.document_id)
    if doc is None:
        raise NotFoundError(_NOT_FOUND, details=details)

    active = list(
        db.scalars(
            select(DocumentVersion).where(
                DocumentVersion.document_id == doc.id,
                DocumentVersion.review_status == "active",
            )
        )
    )

    picked = _pick([v for v in active if _is_valid_on(v, on_date)], locale)
    unconfirmed = False
    if picked is None:
        # Nothing confirmed for the date; show the in-force edition, flagged as unconfirmed.
        picked = _pick([v for v in active if v.effective_to is None], locale)
        if picked is None:
            raise NotFoundError(_NOT_FOUND, details=details)
        unconfirmed = True
    version, is_fallback = picked

    article = db.scalar(
        select(Article).where(
            Article.version_id == version.id, Article.article_number == citation.article_number
        )
    )
    if article is None:
        raise NotFoundError(_NOT_FOUND, details=details)

    if unconfirmed:
        edition = EditionView(effective_from=None, effective_to=None, status="unconfirmed")
        note = unconfirmed_note(locale, on_date)
        is_official = None
    else:
        edition = EditionView(
            effective_from=version.effective_from,
            effective_to=version.effective_to,
            status="current" if version.effective_to is None else "historical",
        )
        note = fallback_language_note(locale, version.language) if is_fallback else None
        is_official = version.is_official_text
    return _build(
        db, citation_id, doc, version, article, citation.part, locale, edition, is_official, note
    )


def get_citation_views(
    db: Session, citation_ids: Iterable[str], on_date: date, locale: Locale
) -> list[CitationView]:
    """Resolve several citations, keeping input order and dropping duplicates. Raises NotFoundError."""
    return [
        get_citation_view(db, cid, on_date, locale)
        for cid in dict.fromkeys(citation_ids)
    ]


def get_article_view(db: Session, article_id: int, locale: Locale) -> CitationView:
    """Article by its primary key (edition of that article's own version). Raises NotFoundError."""
    details = {"article_id": article_id}
    article = db.get(Article, article_id)
    if article is None:
        raise NotFoundError(_NOT_FOUND, details=details)
    version = db.get(DocumentVersion, article.version_id)
    doc = db.get(LegalDocument, version.document_id) if version else None
    if version is None or doc is None:
        raise NotFoundError(_NOT_FOUND, details=details)
    citation_id = db.scalar(
        select(Citation.citation_id)
        .where(Citation.document_id == doc.id, Citation.article_number == article.article_number)
        .order_by(Citation.part.is_not(None), Citation.citation_id)
        .limit(1)
    )
    edition = EditionView(
        effective_from=version.effective_from,
        effective_to=version.effective_to,
        status="current" if version.effective_to is None else "historical",
    )
    return _build(
        db, citation_id, doc, version, article, None, locale, edition, version.is_official_text, None
    )


def get_legal_acts(db: Session, document_keys: Iterable[str], locale: Locale) -> list[LegalActView]:
    """Titles and source URLs of documents, in input order; unknown keys are skipped."""
    keys = list(dict.fromkeys(document_keys))
    if not keys:
        return []
    docs = {
        d.document_key: d
        for d in db.scalars(select(LegalDocument).where(LegalDocument.document_key.in_(keys)))
    }
    return [
        LegalActView(document_key=k, title=_title(docs[k], locale), source_url=docs[k].source_url)
        for k in keys
        if k in docs
    ]
