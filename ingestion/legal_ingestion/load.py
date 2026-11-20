"""Шаг 8. load: upsert в Postgres, одна транзакция на редакцию (docs/INGESTION.md §4 шаг 8)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.legal import Article, ArticlePart, Chunk, DocumentVersion, LegalDocument
from legal_ingestion import version as ver
from legal_ingestion.errors import IngestionError
from legal_ingestion.sources import SourceDocument, SourceVersion

SessionFactory = Callable[[], Session]


@dataclass
class Edition:
    """Всё, что нужно для загрузки одной редакции."""

    doc: SourceDocument
    version: SourceVersion
    stem: str
    articles: list[dict[str, Any]]
    content_hash: str
    chunks: list[dict[str, Any]] = field(default_factory=list)  # с ключом "embedding" после embed


@dataclass
class LoadResult:
    action: str  # loaded | unchanged | updated
    version_id: int
    review_status: str | None
    articles: int
    chunks: int


def _set_if_changed(obj: Any, **values: Any) -> bool:
    changed = False
    for k, v in values.items():
        if getattr(obj, k) != v:
            setattr(obj, k, v)
            changed = True
    return changed


def upsert_document(session: Session, doc: SourceDocument) -> LegalDocument:
    row = session.scalar(select(LegalDocument).where(LegalDocument.document_key == doc.document_key))
    values = dict(
        document_type=doc.document_type,
        document_number=doc.document_number,
        title=dict(doc.title),
        adoption_date=doc.adoption_date,
        issuing_body=doc.issuing_body,
        source_url=doc.source_url,
        status=doc.status,
    )
    if row is None:
        row = LegalDocument(document_key=doc.document_key, **values)
        session.add(row)
    else:
        _set_if_changed(row, **values)
    session.flush()
    return row


def lookup_existing(session: Session, document_key: str, language: str, chash: str) -> tuple[int, int] | None:
    """(version_id, число чанков без вектора), если редакция с таким хэшем уже загружена."""
    doc = session.scalar(select(LegalDocument).where(LegalDocument.document_key == document_key))
    if doc is None:
        return None
    existing = ver.find_existing(session, doc.id, language, chash)
    if existing is None:
        return None
    nulls = session.scalar(
        select(func.count())
        .select_from(Chunk)
        .join(Article, Article.id == Chunk.article_id)
        .where(Article.version_id == existing.id, Chunk.embedding.is_(None))
    )
    return existing.id, int(nulls or 0)


def _version_meta(ed: Edition) -> dict[str, Any]:
    v = ed.version
    return dict(
        is_official_text=v.is_official_text,
        source_url=v.source_url,
        raw_file_path=v.file,
        retrieved_at=v.retrieved_at,
        version_label=v.version_label or v.effective_from.isoformat(),
    )


DEMO_DB_SUFFIX = "_demo"


def assert_demo_database(session_factory: SessionFactory) -> None:
    """--draft-activate разрешён только для базы, имя которой оканчивается на _demo."""
    session = session_factory()
    try:
        name = session.get_bind().url.database or ""
    finally:
        session.close()
    if not name.endswith(DEMO_DB_SUFFIX):
        raise IngestionError(
            f"--draft-activate разрешён только для демо-базы (имя оканчивается на {DEMO_DB_SUFFIX}), "
            f"а подключение идёт к базе '{name}'. Черновики без verified_by в основную базу не попадают: "
            "подтвердите редакцию (verified_by в sources.yaml или команда activate)."
        )


def load_edition(
    session_factory: SessionFactory, ed: Edition, *, reembed: bool = False, draft_activate: bool = False
) -> LoadResult:
    """Загрузить редакцию одной транзакцией. Ошибка в любой точке откатывает всё.

    draft_activate: редакция без verified_by тоже становится active (только демо-база, проверяет вызывающий).
    """
    session = session_factory()
    try:
        with session.begin():
            return _load(session, ed, reembed, draft_activate)
    finally:
        session.close()


def _load(session: Session, ed: Edition, reembed: bool, draft_activate: bool = False) -> LoadResult:
    doc_row = upsert_document(session, ed.doc)
    existing = ver.find_existing(session, doc_row.id, ed.version.language, ed.content_hash)
    if existing is not None:
        return _update_existing(session, existing, ed, reembed, draft_activate)

    v = ed.version
    status = "active" if draft_activate else ver.initial_status(v.verified_by)
    row = DocumentVersion(
        document_id=doc_row.id,
        language=v.language,
        effective_from=v.effective_from,
        effective_to=v.effective_to,
        review_status=status,
        content_hash=ed.content_hash,
        verified_by=v.verified_by,
        last_verified_at=date.today() if status == "active" else None,
        **_version_meta(ed),
    )
    session.add(row)
    session.flush()

    article_rows: dict[str, Article] = {}
    for a in ed.articles:
        art = Article(
            version_id=row.id,
            section=a["section"],
            chapter=a["chapter"],
            article_number=a["article_number"],
            article_title=a["article_title"],
            status=a["status"],
            content=a["content"],
            content_normalized=a["content_normalized"],
        )
        article_rows[a["article_number"]] = art
    session.add_all(article_rows.values())
    session.flush()

    session.add_all(
        ArticlePart(
            article_id=article_rows[a["article_number"]].id,
            part_number=p["part_number"],
            kind=p["kind"],
            content=p["content"],
            content_normalized=p["content_normalized"],
        )
        for a in ed.articles
        for p in a["parts"]
    )
    session.add_all(
        Chunk(
            article_id=article_rows[c["article_number"]].id,
            part_from=c["part_from"],
            part_to=c["part_to"],
            text=c["text"],
            text_normalized=c["text_normalized"],
            embedding=c.get("embedding"),
            token_count=c["token_count"],
        )
        for c in ed.chunks
    )
    session.flush()
    if status == "active":
        ver.link_neighbors(session, row)
        session.flush()
    return LoadResult("loaded", row.id, row.review_status, len(ed.articles), len(ed.chunks))


def _update_existing(
    session: Session, row: DocumentVersion, ed: Edition, reembed: bool, draft_activate: bool = False
) -> LoadResult:
    """Тот же хэш: текст не трогаем; обновляем метаданные и досчитываем недостающие векторы."""
    changed = _set_if_changed(row, **_version_meta(ed))
    if draft_activate and row.review_status == "pending_review":
        row.review_status = "active"
        row.last_verified_at = date.today()
        session.flush()
        ver.link_neighbors(session, row)
        changed = True
    n_articles = session.scalar(select(func.count()).select_from(Article).where(Article.version_id == row.id))
    vectors = {
        (c["article_number"], c["part_from"], c["part_to"]): c["embedding"]
        for c in ed.chunks
        if c.get("embedding") is not None
    }
    n_chunks = 0
    if vectors:
        rows = session.execute(
            select(Chunk, Article.article_number)
            .join(Article, Article.id == Chunk.article_id)
            .where(Article.version_id == row.id)
        ).all()
        n_chunks = len(rows)
        for chunk, number in rows:
            new = vectors.get((number, chunk.part_from, chunk.part_to))
            if new is not None and (reembed or chunk.embedding is None):
                chunk.embedding = new
                changed = True
    else:
        n_chunks = session.scalar(
            select(func.count()).select_from(Chunk).join(Article, Article.id == Chunk.article_id).where(Article.version_id == row.id)
        )
    return LoadResult("updated" if changed else "unchanged", row.id, row.review_status, int(n_articles or 0), int(n_chunks or 0))
