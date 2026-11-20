"""Определение языка запроса по алфавиту и стоп-словам (модель не нужна)."""

from __future__ import annotations

import re

from app.schemas.legal import Locale
from app.rag.stopwords import UZ_CYRL_MARKERS

_CYR = re.compile(r"[Ѐ-ӿ]")
_LAT = re.compile(r"[A-Za-zÀ-ɏ]")
_UZ_CYRL_LETTERS = re.compile(r"[ўқғҳЎҚҒҲ]")
_CYR_WORD = re.compile(r"[Ѐ-ӿ]+")


def detect_language(text: str, default: Locale = "ru") -> Locale:
    cyr = len(_CYR.findall(text))
    lat = len(_LAT.findall(text))
    if cyr == 0 and lat == 0:
        return default
    if lat > cyr:
        return "uz-Latn"
    if _UZ_CYRL_LETTERS.search(text):
        return "uz-Cyrl"
    if any(w.lower() in UZ_CYRL_MARKERS for w in _CYR_WORD.findall(text)):
        return "uz-Cyrl"
    return "ru"
