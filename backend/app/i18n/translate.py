"""Перевод text_key через texts.<locale>.json сценария с запасными языками."""

from __future__ import annotations

from app.scenarios.loader import LoadedScenario
from app.schemas.legal import Locale

_CHAINS: dict[str, tuple[str, ...]] = {
    "ru": ("ru",),
    "uz-Latn": ("uz-Latn", "ru"),
    "uz-Cyrl": ("uz-Cyrl", "uz-Latn", "ru"),
}


def fallback_chain(locale: Locale) -> tuple[str, ...]:
    """Порядок языков: запрошенный, (uz-Cyrl → uz-Latn), ru."""
    return _CHAINS.get(locale, ("ru",))


def translate(loaded: LoadedScenario, key: str, locale: Locale) -> str:
    """Текст по ключу; если нигде нет, возвращается сам ключ."""
    for loc in fallback_chain(locale):
        value = loaded.texts.get(loc, {}).get(key)
        if value:
            return value
    return key
