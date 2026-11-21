"""Перевод text_key через texts.<locale>.json сценария с запасными языками."""

from __future__ import annotations

from app.i18n.translit import lat_to_cyr_display
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
    """Текст по ключу; если нигде нет, возвращается сам ключ.

    Для uz-Cyrl без кириллического текста берётся uz-Latn и транслитерируется.
    """
    for loc in fallback_chain(locale):
        value = loaded.texts.get(loc, {}).get(key)
        if value:
            if locale == "uz-Cyrl" and loc == "uz-Latn":
                return lat_to_cyr_display(value)
            return value
    return key
