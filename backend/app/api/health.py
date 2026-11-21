from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.tts.catalog import audio_lines

router = APIRouter(tags=["service"])


class HealthResponse(BaseModel):
    status: str
    db: bool
    articles: int | None
    chunks: int | None
    scenarios: int
    llm_configured: bool
    embedder: str | None
    audio_lines: int = 0  # pre-generated speech lines loaded from storage (0 = text only)


@router.get("/health", response_model=HealthResponse)
def health(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    db_ok = True
    articles: int | None = None
    chunks: int | None = None
    try:
        db.execute(text("SELECT 1"))
        articles = db.execute(text("SELECT count(*) FROM articles")).scalar_one()
        chunks = db.execute(text("SELECT count(*) FROM chunks")).scalar_one()
    except Exception:
        db_ok = False
        articles = chunks = None
        try:
            db.rollback()
        except Exception:
            pass
    if not db_ok:
        response.status_code = 503
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        db=db_ok,
        articles=articles,
        chunks=chunks,
        scenarios=len(getattr(request.app.state, "scenarios", {})),
        llm_configured=settings.llm_configured,
        embedder=settings.EMBEDDER,
        audio_lines=sum(audio_lines(s) for s in getattr(request.app.state, "scenarios", {}).values()),
    )
