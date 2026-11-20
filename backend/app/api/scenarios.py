from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.legal.service import get_legal_acts
from app.scenarios.registry import Registry, get_registry
from app.schemas.api import ScenarioCard, ScenarioDetail
from app.schemas.legal import Locale
from app.services import game, presenter

router = APIRouter(tags=["scenarios"])


@router.get("/scenarios", response_model=list[ScenarioCard])
def list_scenarios(locale: Locale = "ru", registry: Registry = Depends(get_registry)):
    """Карточки сценариев из реестра в памяти."""
    return [presenter.build_scenario_card(s, locale) for s in registry.values()]


@router.get("/scenarios/{scenario_id}", response_model=ScenarioDetail)
def get_scenario(
    scenario_id: str,
    locale: Locale = "ru",
    registry: Registry = Depends(get_registry),
    db: Session = Depends(get_db),
):
    """Введение в дело: история, участники, требования, документы, применимые акты."""
    loaded = game.get_loaded(registry, scenario_id)
    acts = get_legal_acts(db, loaded.scenario.intro.legal_acts, locale)
    return presenter.build_scenario_detail(loaded, acts, locale)
