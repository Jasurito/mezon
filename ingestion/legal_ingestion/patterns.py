"""Регулярки структуры документа (docs/INGESTION.md §4 шаг 4). Проверены на реальных файлах lex.uz (ru, uz-Latn)."""

from __future__ import annotations

import re

SUPERSCRIPTS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_TABLE = str.maketrans("0123456789", SUPERSCRIPTS)
_APOS = "ʻ'’‘`ʼ"

# Номер статьи/главы: «26», «25-1», «26¹», «419²⁵»
_NUM = rf"\d+(?:[-–]\d+|[{SUPERSCRIPTS}]+)?"
# Римские цифры; на lex.uz в Конституции встречаются кириллические «Х» и «І» вместо латинских
_ROMAN = r"[IVXLCХІ]+"
_TOKEN = rf"(?:{_NUM}|{_ROMAN})"

# Порядковые числительные (раздел «ПЕРВЫЙ», «BIRINCHI»); ключ в нижнем регистре, ё → е
ORDINALS: dict[str, dict[str, int]] = {
    "ru": {
        w: i
        for i, w in enumerate(
            "первый второй третий четвертый пятый шестой седьмой восьмой девятый десятый одиннадцатый "
            "двенадцатый тринадцатый четырнадцатый пятнадцатый шестнадцатый семнадцатый восемнадцатый "
            "девятнадцатый двадцатый".split(),
            start=1,
        )
    },
    "uz-Latn": {
        w: i
        for i, w in enumerate(
            "birinchi ikkinchi uchinchi toʻrtinchi beshinchi oltinchi yettinchi sakkizinchi toʻqqizinchi "
            "oninchi".split(),
            start=1,
        )
    },
    "uz-Cyrl": {
        w: i
        for i, w in enumerate(
            "биринчи иккинчи учинчи тўртинчи бешинчи олтинчи еттинчи саккизинчи тўққизинчи ўнинчи".split(), start=1
        )
    },
}


def _ord_alt(lang: str) -> str:
    words = sorted(ORDINALS[lang], key=len, reverse=True)
    return "|".join(re.escape(w).replace("ʻ", f"[{_APOS}]") for w in words)


def _ord_alt_ru() -> str:
    # допускаем «четвертый» и «четвёртый»
    return _ord_alt("ru").replace("четвертый", "четв[её]ртый")


SECTION = {
    "ru": re.compile(rf"^Раздел\s+({_TOKEN}|{_ord_alt_ru()})\b[.\s]*(.*)$", re.IGNORECASE),
    "uz-Latn": re.compile(
        rf"^({_TOKEN}|{_ord_alt('uz-Latn')})[- ]?bo[{_APOS}]lim\b[.\s]*(.*)$", re.IGNORECASE
    ),
    "uz-Cyrl": re.compile(rf"^({_TOKEN}|{_ord_alt('uz-Cyrl')})[- ]?бўлим\b[.\s]*(.*)$", re.IGNORECASE),
}
CHAPTER = {
    "ru": re.compile(rf"^Глава\s+({_TOKEN})\b[.\s]*(.*)$", re.IGNORECASE),
    "uz-Latn": re.compile(rf"^({_TOKEN})[- ]?bob\b[.\s]*(.*)$", re.IGNORECASE),
    "uz-Cyrl": re.compile(rf"^({_TOKEN})[- ]?боб\b[.\s]*(.*)$", re.IGNORECASE),
}
# Заголовки, которые не пишутся ни в section, ни в chapter, но и не являются текстом статьи:
# часть кодекса («Часть первая»), подраздел, параграф («§ 1.»).
PART = {
    "ru": re.compile(r"^Часть\s+(первая|вторая|третья|четв[её]ртая|пятая)\s*$", re.IGNORECASE),
    "uz-Latn": re.compile(rf"^({_ord_alt('uz-Latn')})\s+qism\s*$", re.IGNORECASE),
    "uz-Cyrl": re.compile(rf"^({_ord_alt('uz-Cyrl')})\s+қисм\s*$", re.IGNORECASE),
}
SUBSECTION = {
    "ru": re.compile(rf"^Подраздел\s+({_TOKEN})\b[.\s]*(.*)$", re.IGNORECASE),
    "uz-Latn": re.compile(rf"^({_TOKEN})[- ]?kichik\s+bo[{_APOS}]lim\b[.\s]*(.*)$", re.IGNORECASE),
    "uz-Cyrl": re.compile(rf"^({_TOKEN})[- ]?кичик\s+бўлим\b[.\s]*(.*)$", re.IGNORECASE),
}
PARAGRAPH = {
    "ru": re.compile(rf"^§\s*({_NUM})\b[.\s]*(.*)$"),
    "uz-Latn": re.compile(rf"^({_NUM})[- ]?§[.\s]*(.*)$"),
    "uz-Cyrl": re.compile(rf"^({_NUM})[- ]?§[.\s]*(.*)$"),
}
# «Стать» без «я» — опечатка на lex.uz (ru, ст. 419²⁵ ГПК), принимаем как статью
ARTICLE = {
    "ru": re.compile(rf"^Стать[яи]?\s+({_NUM})\.\s*(.*)$", re.IGNORECASE),
    "uz-Latn": re.compile(rf"^({_NUM})\s*-?\s*modda\.\s*(.*)$", re.IGNORECASE),  # «599- modda.» — пробел на lex.uz
    "uz-Cyrl": re.compile(rf"^({_NUM})\s*-?\s*модда\.\s*(.*)$", re.IGNORECASE),
}
# Преамбула — отдельный заголовок (TEXT_BOLD_CENTER в Конституции)
PREAMBLE_HEADING = {
    "ru": re.compile(r"^Преамбула\s*$", re.IGNORECASE),
    "uz-Latn": re.compile(r"^(?:Muqaddima|Preambula)\s*$", re.IGNORECASE),
    "uz-Cyrl": re.compile(r"^(?:Муқаддима|Преамбула)\s*$", re.IGNORECASE),
}
NOTE = {
    "ru": re.compile(r"^Примечани[ея]\b", re.IGNORECASE),
    "uz-Latn": re.compile(r"^Izoh\b", re.IGNORECASE),
    "uz-Cyrl": re.compile(r"^Изоҳ\b", re.IGNORECASE),
}
_ALL_NOTES = tuple(NOTE.values())
REPEALED = {
    "ru": re.compile(r"^\W*утрати[лв]\w*\s+силу", re.IGNORECASE),
    "uz-Latn": re.compile(rf"^\W*kuchini\s+yo[{_APOS}]qotgan", re.IGNORECASE),
    "uz-Cyrl": re.compile(r"^\W*кучини\s+йўқотган", re.IGNORECASE),
}
# Пункт/подпункт остаётся внутри своей части: «1)», «4¹)», «а)», «—», «–», «-»
POINT = re.compile(rf"^(?:\d+[{SUPERSCRIPTS}]*\)|[^\W\d_]{{1,2}}\)|[—–-](?:\s|$))")

PREAMBLE = "preamble"

_HOMOGLYPHS = str.maketrans("ХІхі", "XIXI")


def normalize_number(token: str, language: str | None = None) -> str:
    """Номер раздела/главы в единый вид: римские — латиницей в верхнем регистре, порядковое слово → римская
    цифра («ПЕРВЫЙ» → «I»), арабские (в т.ч. «23¹», «25-1») как в тексте."""
    t = token.strip()
    key = t.lower().replace("ё", "е")
    for lang in (language, "ru", "uz-Latn", "uz-Cyrl"):
        if lang in ORDINALS:
            for w, n in ORDINALS[lang].items():
                if key == w or (lang == "uz-Latn" and key.translate(_APOS_FOLD) == w.translate(_APOS_FOLD)):
                    return to_roman(n)
    if re.fullmatch(_ROMAN, t, re.IGNORECASE):
        return t.translate(_HOMOGLYPHS).upper()
    return t


_APOS_FOLD = {ord(c): "ʻ" for c in _APOS}


def to_roman(n: int) -> str:
    out = ""
    for v, s in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= v:
            out += s
            n -= v
    return out


def is_note(text: str, language: str | None = None) -> bool:
    pats = (NOTE[language],) if language in NOTE else _ALL_NOTES
    return any(p.match(text) for p in pats)
