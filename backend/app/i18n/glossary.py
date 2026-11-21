"""Словарик простых определений (glossary.json): термин, определение и словоформы для подсветки."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.i18n.translit import lat_to_cyr_display
from app.schemas.legal import Locale

_FILE = Path(__file__).with_name("glossary.json")


@lru_cache(maxsize=1)
def _load() -> list[dict]:
    return json.loads(_FILE.read_text(encoding="utf-8"))["terms"]


def get_glossary(locale: Locale) -> list[dict]:
    """[{id, term, definition, aliases}]; uz-Cyrl — транслитерация из uz-Latn."""
    out: list[dict] = []
    for item in _load():
        if locale == "uz-Cyrl":
            src = item["uz-Latn"]
            entry = {
                "term": lat_to_cyr_display(src["term"]),
                "definition": lat_to_cyr_display(src["definition"]),
                "aliases": [lat_to_cyr_display(a) for a in src["aliases"]],
            }
        else:
            src = item.get(locale) or item["ru"]
            entry = {"term": src["term"], "definition": src["definition"], "aliases": list(src["aliases"])}
        out.append({"id": item["id"], **entry})
    return out
