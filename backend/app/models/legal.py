"""Правовые таблицы, схема по docs/INGESTION.md §6.

Схему держит бэкенд (одна база, одна история миграций), ingestion только наполняет данными.
"""

from datetime import date
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Computed,
    Date,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_key: Mapped[str] = mapped_column(Text, unique=True)
    document_type: Mapped[str | None] = mapped_column(Text)
    document_number: Mapped[str | None] = mapped_column(Text)
    title: Mapped[dict[str, Any] | None] = mapped_column(JSONB)  # {"ru": "...", "uz-Latn": "..."}
    adoption_date: Mapped[date | None] = mapped_column(Date)
    issuing_body: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(Text)


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    __table_args__ = (UniqueConstraint("document_id", "language", "content_hash"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("legal_documents.id"))
    language: Mapped[str] = mapped_column(Text)
    is_official_text: Mapped[bool | None] = mapped_column(Boolean)
    effective_from: Mapped[date | None] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date)
    review_status: Mapped[str | None] = mapped_column(Text)  # pending_review | active | superseded
    version_label: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    raw_file_path: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(Text)
    retrieved_at: Mapped[date | None] = mapped_column(Date)
    verified_by: Mapped[str | None] = mapped_column(Text)
    last_verified_at: Mapped[date | None] = mapped_column(Date)


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("version_id", "article_number"),
        Index(
            "ix_articles_article_title_trgm",
            "article_title",
            postgresql_using="gin",
            postgresql_ops={"article_title": "gin_trgm_ops"},
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version_id: Mapped[int] = mapped_column(ForeignKey("document_versions.id"))
    section: Mapped[str | None] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(Text)
    article_number: Mapped[str] = mapped_column(Text)
    article_title: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)  # дословно, все части
    content_normalized: Mapped[str | None] = mapped_column(Text)


class ArticlePart(Base):
    __tablename__ = "article_parts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    part_number: Mapped[int] = mapped_column(Integer)
    kind: Mapped[str] = mapped_column(Text)  # text | note
    content: Mapped[str] = mapped_column(Text)
    content_normalized: Mapped[str | None] = mapped_column(Text)


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (Index("ix_chunks_tsv", "tsv", postgresql_using="gin"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    part_from: Mapped[int | None] = mapped_column(Integer)
    part_to: Mapped[int | None] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)  # с заголовком
    text_normalized: Mapped[str] = mapped_column(Text)
    # Размерность не задана: модель эмбеддингов ещё не выбрана (см. INGESTION.md, eval).
    # После выбора модели зафиксировать размерность отдельной миграцией.
    embedding: Mapped[Any | None] = mapped_column(Vector())
    tsv: Mapped[Any] = mapped_column(
        TSVECTOR, Computed("to_tsvector('simple', text_normalized)", persisted=True)
    )
    token_count: Mapped[int | None] = mapped_column(Integer)


class Citation(Base):
    __tablename__ = "citations"

    citation_id: Mapped[str] = mapped_column(Text, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("legal_documents.id"))
    article_number: Mapped[str] = mapped_column(Text)
    part: Mapped[int | None] = mapped_column(Integer)
    topic: Mapped[str | None] = mapped_column(Text)
    verified_by: Mapped[str | None] = mapped_column(Text)
