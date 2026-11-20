"""Шаг 9. link: citations.yaml → таблица citations (docs/INGESTION.md §3.3, §4 шаг 9)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.legal import Article, ArticlePart, Citation, DocumentVersion, LegalDocument
from legal_ingestion.errors import IngestionError
from legal_ingestion.load import SessionFactory


def _to_str(v: Any) -> Any:
    return str(v) if isinstance(v, int) and not isinstance(v, bool) else v


class CitationEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str = Field(min_length=1)
    document_key: str = Field(min_length=1)
    article_number: Annotated[str, BeforeValidator(_to_str)] = Field(min_length=1)
    part: int | None = None
    topic: str | None = None
    verified_by: str | None = None


class LinkError(IngestionError):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("link: ссылки не загружены:\n  " + "\n  ".join(errors))


def load_citations(path: Path) -> tuple[list[CitationEntry], list[str]]:
    if not path.is_file():
        return [], [f"{path}: файл не найден"]
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [], [f"{path}: некорректный YAML: {exc}"]
    if raw is None:
        return [], []
    if not isinstance(raw, list):
        return [], [f"{path}: ожидается список записей"]
    entries: list[CitationEntry] = []
    errors: list[str] = []
    seen: set[str] = set()
    for i, item in enumerate(raw):
        try:
            e = CitationEntry.model_validate(item)
        except ValidationError as exc:
            for err in exc.errors():
                loc = ".".join(str(p) for p in err["loc"])
                errors.append(f"citations[{i}].{loc}: {err['msg']}")
            continue
        if e.citation_id in seen:
            errors.append(f"citations[{i}]: повторяющийся citation_id {e.citation_id}")
        seen.add(e.citation_id)
        entries.append(e)
    return entries, errors


def _article_exists(session: Session, doc_id: int, number: str, part: int | None) -> str | None:
    """None = всё найдено, иначе текст ошибки. Статья ищется в любой редакции документа."""
    arts = list(
        session.scalars(
            select(Article)
            .join(DocumentVersion, DocumentVersion.id == Article.version_id)
            .where(DocumentVersion.document_id == doc_id, Article.article_number == number)
        )
    )
    if not arts:
        return f"статья {number} не найдена ни в одной редакции документа"
    if part is not None:
        found = session.scalar(
            select(ArticlePart.id).where(
                ArticlePart.article_id.in_([a.id for a in arts]), ArticlePart.part_number == part
            ).limit(1)
        )
        if found is None:
            return f"в статье {number} нет части {part}"
    return None


def link_citations(session_factory: SessionFactory, entries: list[CitationEntry]) -> int:
    """Upsert всех ссылок одной транзакцией; хоть одна ненайденная статья = LinkError, ничего не записано."""
    session = session_factory()
    try:
        with session.begin():
            errors: list[str] = []
            docs: dict[str, LegalDocument | None] = {}
            for e in entries:
                if e.document_key not in docs:
                    docs[e.document_key] = session.scalar(
                        select(LegalDocument).where(LegalDocument.document_key == e.document_key)
                    )
                doc = docs[e.document_key]
                if doc is None:
                    errors.append(f"{e.citation_id}: документ {e.document_key} не загружен")
                    continue
                msg = _article_exists(session, doc.id, e.article_number, e.part)
                if msg:
                    errors.append(f"{e.citation_id}: {msg}")
            if errors:
                raise LinkError(errors)
            for e in entries:
                doc = docs[e.document_key]
                assert doc is not None
                row = session.get(Citation, e.citation_id)
                values = dict(
                    document_id=doc.id,
                    article_number=e.article_number,
                    part=e.part,
                    topic=e.topic,
                    verified_by=e.verified_by,
                )
                if row is None:
                    session.add(Citation(citation_id=e.citation_id, **values))
                else:
                    for k, v in values.items():
                        if getattr(row, k) != v:
                            setattr(row, k, v)
        return len(entries)
    finally:
        session.close()
