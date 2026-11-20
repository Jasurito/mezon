"""Модели поиска по правовой базе и AI-наставника (docs/BACKEND.md §5.7, §5.8)."""

from __future__ import annotations

import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.legal import EditionStatus, Locale

# --------------------------------------------------------------------------- search


class SearchMatch(BaseModel):
    exact_article: bool
    dense_rank: int | None
    sparse_rank: int | None


class SearchResultItem(BaseModel):
    chunk_id: int
    article_id: int
    citation_id: str | None
    document_title: str
    article_number: str
    article_title: str | None
    parts: str | None  # "1–2"
    snippet: str  # дословный фрагмент текста, ≤300 символов
    edition_status: EditionStatus
    source_url: str | None
    score: float
    match: SearchMatch


class SearchResponse(BaseModel):
    query: str
    detected_language: Locale
    date: dt.date
    results: list[SearchResultItem]


# --------------------------------------------------------------------------- mentor request


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class MentorAskRequest(BaseModel):
    session_id: uuid.UUID | None = None
    question: str = Field(min_length=1, max_length=2000)
    locale: Locale = "ru"
    history: list[HistoryItem] = []


# --------------------------------------------------------------------------- LLM output contracts
# Без ограничений длины и значений по умолчанию: схема уходит в structured output.


class MentorBlock(BaseModel):
    text: str
    source_ids: list[str]


class MentorAnswer(BaseModel):
    answer_blocks: list[MentorBlock]
    insufficient_sources: bool


QueryCategory = Literal["article_lookup", "concept", "case_specific", "out_of_scope"]


class QueryClassification(BaseModel):
    category: QueryCategory
