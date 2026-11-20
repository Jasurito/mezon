"""Нормализация текста и транслитерация узбекского.

Правила обязаны совпадать с docs/INGESTION.md §4 шаг 3 (поле content_normalized):
поиск идёт по chunks.text_normalized, который строит ingestion. Если ingestion
меняет правила, менять надо и здесь.
"""

from __future__ import annotations

import re

# Канонический апостроф: ʻ (U+02BB), как в таблице транслитерации INGESTION.md (ў→oʻ, ғ→gʻ).
APOSTROPHE = "ʻ"
_APOSTROPHES = "ʻʼ’‘ʹˈ`´'"
APOS_TABLE = {ord(c): APOSTROPHE for c in _APOSTROPHES}  # побуквенная замена, длина строки не меняется
# Разные пробелы (в том числе неразрывные) → обычный; мягкий перенос и невидимые символы убираем.
_SPACES = (
    "             "
    "  　\t\r\n  "
)
_SPACE_TABLE = {ord(c): " " for c in _SPACES}
_REMOVE_TABLE = {ord(c): None for c in "­​‌‍⁠﻿"}
_WS = re.compile(r" {2,}")

# --- Cyrillic (uz) -> Latin ------------------------------------------------------------
_CYR_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo", "ж": "j", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
    "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "x", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ъ": APOSTROPHE, "ь": "", "ы": "i", "э": "e", "ю": "yu", "я": "ya",
    "ў": "o" + APOSTROPHE, "қ": "q", "ғ": "g" + APOSTROPHE, "ҳ": "h",
}
_CYR_VOWELS = set("аеёиоуэюяыўъь")


def base_normalize(text: str) -> str:
    """Регистр, пробелы (в том числе NBSP), апострофы, ё→е. Без транслитерации."""
    s = text.translate(_REMOVE_TABLE).translate(_SPACE_TABLE).translate(APOS_TABLE)
    s = s.lower().replace("ё", "е")
    return _WS.sub(" ", s).strip()


def cyr_to_lat(text: str) -> str:
    """uz-Cyrl → uz-Latn (только для поиска; юридический текст не транслитерируется)."""
    s = text.lower()  # «ё» нужна транслитерации как «yo», поэтому до base_normalize
    out: list[str] = []
    prev = " "
    for ch in s:
        if ch == "е":
            lat = "ye" if (not prev.isalpha() or prev in _CYR_VOWELS) else "e"
        else:
            lat = _CYR_LAT.get(ch, ch)
        out.append(lat)
        prev = ch
    return "".join(out)


_LAT_CYR_MULTI = (
    ("o" + APOSTROPHE, "ў"), ("g" + APOSTROPHE, "ғ"), ("shch", "щ"), ("sh", "ш"), ("ch", "ч"),
    ("yo", "ё"), ("yu", "ю"), ("ya", "я"), ("ye", "е"),  # «ts» не склеиваем: чаще это «тс» (sifatsiz)
)
_LAT_CYR = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и", "j": "ж",
    "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ", "r": "р", "s": "с",
    "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з", APOSTROPHE: "ъ",
}


def lat_to_cyr(text: str) -> str:
    """uz-Latn → uz-Cyrl (детерминированная таблица; «e» в начале слова → «э»)."""
    s = base_normalize(text)
    out: list[str] = []
    i = 0
    while i < len(s):
        for lat, cyr in _LAT_CYR_MULTI:
            if s.startswith(lat, i):
                out.append(cyr)
                i += len(lat)
                break
        else:
            ch = s[i]
            if ch == "e" and (i == 0 or not s[i - 1].isalpha()):
                out.append("э")
            else:
                out.append(_LAT_CYR.get(ch, ch))
            i += 1
    return "".join(out)


def normalize(text: str, language: str | None = None) -> str:
    """Нормализованная форма для поиска; для uz-Cyrl дополнительно транслитерация в латиницу."""
    if language == "uz-Cyrl":
        return base_normalize(cyr_to_lat(text))
    return base_normalize(text)


# Слово: буквы/цифры, внутри допустим апостроф (oʻzbek); дефис слова не склеивает.
_TOKEN = re.compile(rf"[^\W_]+(?:{APOSTROPHE}[^\W_]+)*", re.UNICODE)


def tokenize(normalized: str) -> list[str]:
    return _TOKEN.findall(normalized)
