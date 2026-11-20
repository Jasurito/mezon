import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.errors import AppError
from app.legal import service
from app.rag.deps import embedder_dep
from app.rag.embedder import Embedder
from app.rag.search import search_legal
from app.schemas.legal import CitationView, Locale
from app.schemas.rag import SearchResponse

router = APIRouter(prefix="/legal", tags=["legal"])


@router.get("/citations/{citation_id}", response_model=CitationView)
def get_citation(
    citation_id: str,
    date: dt.date | None = None,
    locale: Locale = "ru",
    db: Session = Depends(get_db),
) -> CitationView:
    return service.get_citation_view(db, citation_id, date or dt.date.today(), locale)


@router.get("/articles/{article_id}", response_model=CitationView)
def get_article(
    article_id: int, locale: Locale = "ru", db: Session = Depends(get_db)
) -> CitationView:
    return service.get_article_view(db, article_id, locale)


@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(min_length=1, max_length=500),
    locale: Locale | None = None,
    date: dt.date | None = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    embedder: Embedder = Depends(embedder_dep),
) -> SearchResponse:
    """Гибридный поиск (FTS + триграммы + dense, слияние RRF) без LLM."""
    if not q.strip():
        raise AppError("Пустой поисковый запрос", code="VALIDATION_ERROR", http_status=422)
    return search_legal(
        db,
        query=q.strip(),
        locale=locale,
        on_date=date or dt.date.today(),
        limit=limit,
        settings=settings,
        embedder=embedder,
    )
