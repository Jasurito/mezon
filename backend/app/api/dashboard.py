import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.dashboard import build_dashboard
from app.db import get_db
from app.scenarios.registry import Registry, get_registry
from app.schemas.analytics import DashboardOut
from app.schemas.legal import Locale

router = APIRouter(tags=["dashboard"])


@router.get("/users/{user_id}/dashboard", response_model=DashboardOut)
def get_dashboard(
    user_id: uuid.UUID,
    locale: Locale = "ru",
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
):
    """Итоги игр, прирост знаний, уровень, ошибки и рекомендации пользователя."""
    return build_dashboard(db, registry, user_id, locale)
