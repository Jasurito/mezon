"""Реестр сценариев в памяти: загрузка и проверка при старте сервера."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path

from fastapi import Request
from sqlalchemy.orm import Session

from app.config import Settings
from app.game_engine import collect_citation_ids
from app.legal.service import missing_citation_ids
from app.scenarios.loader import LoadedScenario, ScenarioValidationError, load_all

log = logging.getLogger("adolat.scenarios")

Registry = dict[str, LoadedScenario]


class CitationCheckError(Exception):
    """В базе нет ссылок, на которые указывает сценарий."""

    def __init__(self, missing: dict[str, list[str]]) -> None:
        self.missing = missing
        lines = [f"{sid}: {', '.join(ids)}" for sid, ids in missing.items()]
        super().__init__("citations not found in the legal database:\n" + "\n".join(lines))


def find_missing_citations(registry: Registry, db: Session) -> dict[str, list[str]]:
    """scenario_id -> отсутствующие в базе citation_id (только непустые)."""
    result: dict[str, list[str]] = {}
    for sid, loaded in registry.items():
        ids = collect_citation_ids(loaded.scenario)
        missing = missing_citation_ids(db, ids)
        if missing:
            result[sid] = sorted(missing)
    return result


def scenario_roots(settings: Settings) -> list[Path]:
    """SCENARIOS_DIR: один путь или несколько через os.pathsep (':' на Linux/macOS)."""
    raw = os.fspath(settings.SCENARIOS_DIR)
    return [Path(p) for p in raw.split(os.pathsep) if p.strip()]


def load_from_roots(roots: list[Path]) -> Registry:
    """Сценарии из всех каталогов; повтор scenario_id в разных каталогах = ошибка."""
    registry: Registry = {}
    origin: dict[str, Path] = {}
    errors: list[str] = []
    for root in roots:
        if not root.is_dir():
            log.warning("каталог сценариев %s не существует, пропущен", root)
            continue
        for sid, loaded in load_all(root, strict=True).items():
            if sid in registry:
                errors.append(f"duplicate scenario_id '{sid}': {origin[sid]} and {root}")
                continue
            registry[sid] = loaded
            origin[sid] = root
    if errors:
        raise ScenarioValidationError(errors)
    return registry


def load_registry(settings: Settings, open_db: Callable[[], AbstractContextManager[Session]]) -> Registry:
    """Загрузить сценарии и проверить ссылки.

    Ошибки схемы и (при STRICT_CITATIONS) отсутствующие ссылки поднимают исключение:
    сервер не должен стартовать.
    """
    roots = scenario_roots(settings)
    if not any(r.is_dir() for r in roots):
        log.warning("SCENARIOS_DIR %s не существует, реестр сценариев пуст", settings.SCENARIOS_DIR)
        return {}
    registry = load_from_roots(roots)
    for sid, loaded in registry.items():
        if loaded.warnings:
            # обычно это сотни ключей uz-Cyrl: одна строка на сценарий, полный список — в debug
            log.warning(
                "сценарий %s: %d предупреждений (первое: %s)",
                sid, len(loaded.warnings), loaded.warnings[0],
            )
            for w in loaded.warnings:
                log.debug("scenario warning: %s", w)
    if not registry:
        log.warning("в %s нет сценариев", settings.SCENARIOS_DIR)
        return registry
    try:
        with open_db() as db:
            missing = find_missing_citations(registry, db)
    except Exception as exc:
        if settings.STRICT_CITATIONS:
            raise
        log.warning("проверка ссылок пропущена (STRICT_CITATIONS=False): %s", exc)
        return registry
    if missing:
        err = CitationCheckError(missing)
        if settings.STRICT_CITATIONS:
            raise err
        log.warning("%s", err)
    log.info("загружено сценариев: %d", len(registry))
    return registry


def get_registry(request: Request) -> Registry:
    """Зависимость FastAPI: реестр сценариев из app.state."""
    return request.app.state.scenarios
