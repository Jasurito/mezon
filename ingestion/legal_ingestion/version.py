"""Шаг 5. version: хэш редакции, статусы, смена действующей редакции (docs/INGESTION.md §4 шаг 5)."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.legal import DocumentVersion
from legal_ingestion.errors import IngestionError
from legal_ingestion.normalize import to_search


def content_hash(articles: list[dict[str, Any]], language: str) -> str:
    """SHA-256 нормализованного текста всей редакции (номера, названия и тексты статей по порядку)."""
    h = hashlib.sha256()
    for a in articles:
        title = to_search(a["article_title"] or "", language)
        h.update(f"{a['article_number']}\x1f{title}\x1f{a['content_normalized']}\x1e".encode())
    return h.hexdigest()


def initial_status(verified_by: str | None) -> str:
    """Новая редакция: без подтверждения юриста = pending_review, иначе active."""
    return "active" if verified_by and verified_by.strip() else "pending_review"


def find_existing(session: Session, document_id: int, language: str, chash: str) -> DocumentVersion | None:
    return session.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == document_id,
            DocumentVersion.language == language,
            DocumentVersion.content_hash == chash,
        )
    )


def link_neighbors(session: Session, new: DocumentVersion) -> list[DocumentVersion]:
    """Активная редакция встала в цепочку: предыдущая active закрывается (superseded, effective_to).

    Если новая старше уже действующей (загрузка исторической редакции), закрывается сама новая.
    Старые редакции не удаляются.
    """
    if new.effective_from is None:
        return []
    others = list(
        session.scalars(
            select(DocumentVersion).where(
                DocumentVersion.document_id == new.document_id,
                DocumentVersion.language == new.language,
                DocumentVersion.review_status.in_(("active", "superseded")),
                DocumentVersion.id != new.id,
            )
        )
    )
    changed: list[DocumentVersion] = []
    for prev in others:
        if prev.effective_from is None:
            continue
        if prev.review_status == "active" and prev.effective_from < new.effective_from:
            if prev.effective_to is None or prev.effective_to > new.effective_from:
                prev.effective_to = new.effective_from
            prev.review_status = "superseded"
            changed.append(prev)
    later = [p.effective_from for p in others if p.effective_from and p.effective_from > new.effective_from]
    if later and new.effective_to is None:
        new.effective_to = min(later)
        changed.append(new)
    return changed


def activate_version(session: Session, version: DocumentVersion, by: str, today: date | None = None) -> list[DocumentVersion]:
    """Подтвердить редакцию: verified_by, active, закрыть предыдущую active того же документа и языка."""
    if not by or not by.strip():
        raise IngestionError("activate: укажите инициалы проверяющего (--by)")
    if version.review_status == "superseded":
        raise IngestionError(f"редакция id={version.id} уже заменена более новой (superseded), активировать нельзя")
    version.verified_by = by.strip()
    version.last_verified_at = today or date.today()
    version.review_status = "active"
    session.flush()
    return [version, *link_neighbors(session, version)]
