from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.legal.service import get_legal_acts
from app.scenarios.registry import Registry, get_registry
from app.schemas.api import AudioLineView, ScenarioCard, ScenarioDetail
from app.schemas.legal import Locale
from app.services import game, presenter
from app.tts.catalog import audio_for
from app.tts.lines import spoken_lines

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


@router.get("/scenarios/{scenario_id}/audio", response_model=list[AudioLineView])
def get_scenario_audio(scenario_id: str, locale: Locale = "ru", registry: Registry = Depends(get_registry)):
    """Pre-generated speech of the scenario in this locale, for preloading when the case opens (empty = text only)."""
    loaded = game.get_loaded(registry, scenario_id)
    out: list[AudioLineView] = []
    for line in spoken_lines(loaded.scenario):
        audio = audio_for(loaded, line.speaker, line.text_key, locale)
        if audio is not None:
            out.append(AudioLineView(speaker=line.speaker, text_key=line.text_key, url=audio.url,
                                     duration_ms=audio.duration_ms))
    return out
