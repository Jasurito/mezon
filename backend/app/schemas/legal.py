"""API views of the legal corpus (contract between app/legal and the rest of the API).

Field names follow docs/BACKEND.md §4 (CitationView) and §5.7. Fields may be added,
never renamed or removed, without updating the frontend.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel

Locale = Literal["ru", "uz-Latn", "uz-Cyrl"]
EditionStatus = Literal["current", "historical", "unconfirmed"]


class EditionView(BaseModel):
    effective_from: date | None
    effective_to: date | None
    status: EditionStatus


class ArticlePartView(BaseModel):
    part_number: int
    kind: str  # text | note
    text: str


class CitationView(BaseModel):
    """Everything the frontend shows about one article (or one part of it).

    Used by GET /api/legal/citations/{id}, GET /api/legal/articles/{id},
    session results and mentor sources. ``citation_id`` is null for an article
    that no scenario references.
    """

    citation_id: str | None
    article_id: int
    document_key: str
    document_title: str
    document_type: str
    document_number: str | None
    article_number: str
    article_title: str | None
    chapter: str | None
    part: int | None  # set when the citation points to one part
    parts: list[ArticlePartView]
    text: str  # verbatim: the cited part if ``part`` is set, else the whole article
    language: str
    is_official_text: bool | None
    edition: EditionView
    source_url: str | None
    last_verified_at: date | None
    translation_note: str | None


class LegalActView(BaseModel):
    """Applicable act shown on the case intro screen."""

    document_key: str
    title: str
    source_url: str | None
