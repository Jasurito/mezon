from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics import events as events_service
from app.analytics import summary as summary_service
from app.db import get_db
from app.scenarios.registry import Registry, get_registry
from app.schemas.analytics import EventsIn, EventsOut, ScenarioSummary
from app.schemas.legal import Locale
from app.services.clock import get_now

router = APIRouter(tags=["analytics"])


@router.post("/events", response_model=EventsOut, status_code=202)
def post_events(
    body: EventsIn,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
):
    """Клиентские события пачкой; неизвестные типы считаются в rejected."""
    return events_service.ingest(db, body, now)


@router.get("/analytics/scenarios/{scenario_id}/summary", response_model=ScenarioSummary)
def get_summary(
    scenario_id: str,
    locale: Locale = "ru",
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
):
    """Агрегаты по сценарию из SQL-представлений."""
    return summary_service.scenario_summary(db, registry, scenario_id, locale)
