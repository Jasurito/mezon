"""Text preparation for synthesis: the models skip digits and each one reads only one script.

``prepare(text, lang, voice)``: numbers -> words, then the script the voice can read
(Uzbek Latin -> Cyrillic for uzb_0, 2026 / typographic Latin -> plain old-style Latin for dilnavoz).
"""

from __future__ import annotations

import re

from app.i18n.translit import lat_to_cyr_display
from app.tts.voices import Lang, Voice

# --------------------------------------------------------------------------- Russian numbers

_RU_UNITS = ["ноль", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
_RU_UNITS_F = ["ноль", "одна", "две"] + _RU_UNITS[3:]
_RU_TEENS = ["десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать", "пятнадцать", "шестнадцать",
             "семнадцать", "восемнадцать", "девятнадцать"]
_RU_TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят", "шестьдесят", "семьдесят", "восемьдесят",
            "девяносто"]
_RU_HUNDREDS = ["", "сто", "двести", "триста", "четыреста", "пятьсот", "шестьсот", "семьсот", "восемьсот",
                "девятьсот"]
_RU_SCALES = [
    (10**9, ("миллиард", "миллиарда", "миллиардов"), False),
    (10**6, ("миллион", "миллиона", "миллионов"), False),
    (10**3, ("тысяча", "тысячи", "тысяч"), True),
]


def _ru_form(n: int, forms: tuple[str, str, str]) -> str:
    if 11 <= n % 100 <= 14:
        return forms[2]
    return forms[0] if n % 10 == 1 else forms[1] if 2 <= n % 10 <= 4 else forms[2]


def _ru_below_1000(n: int, feminine: bool = False) -> list[str]:
    words = [_RU_HUNDREDS[n // 100]] if n >= 100 else []
    rest = n % 100
    if 10 <= rest < 20:
        words.append(_RU_TEENS[rest - 10])
    else:
        if rest >= 20:
            words.append(_RU_TENS[rest // 10])
        if rest % 10:
            words.append((_RU_UNITS_F if feminine else _RU_UNITS)[rest % 10])
    return [w for w in words if w]


# day of the month in the genitive: "с 8 августа" -> "с восьмого августа"
_RU_DAY_GEN = ["", "первого", "второго", "третьего", "четвёртого", "пятого", "шестого", "седьмого", "восьмого",
               "девятого", "десятого", "одиннадцатого", "двенадцатого", "тринадцатого", "четырнадцатого",
               "пятнадцатого", "шестнадцатого", "семнадцатого", "восемнадцатого", "девятнадцатого", "двадцатого"]
_RU_MONTHS_GEN = r"(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)"


def ru_day_genitive(n: int) -> str:
    if n <= 20:
        return _RU_DAY_GEN[n]
    tens = "тридцатого" if n == 30 else "двадцать" if n < 30 else "тридцать"
    return tens if n % 10 == 0 else f"{tens} {_RU_DAY_GEN[n % 10]}"


def ru_number(n: int) -> str:
    if n == 0:
        return "ноль"
    words: list[str] = []
    for scale, forms, feminine in _RU_SCALES:
        q, n = divmod(n, scale)
        if q:
            words += _ru_below_1000(q, feminine) + [_ru_form(q, forms)]
    return " ".join(words + _ru_below_1000(n))


# --------------------------------------------------------------------------- Uzbek numbers (Latin)

_UZ_UNITS = ["nol", "bir", "ikki", "uch", "toʻrt", "besh", "olti", "yetti", "sakkiz", "toʻqqiz"]
_UZ_TENS = ["", "oʻn", "yigirma", "oʻttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "toʻqson"]


def uz_number(n: int) -> str:
    if n == 0:
        return "nol"
    words: list[str] = []
    for scale, word in ((10**9, "milliard"), (10**6, "million"), (10**3, "ming")):
        q, n = divmod(n, scale)
        if q:
            words += ([word] if q == 1 and scale == 1000 else [uz_number(q), word])
    if n >= 100:
        words += (["yuz"] if n // 100 == 1 else [_UZ_UNITS[n // 100], "yuz"])
        n %= 100
    if n >= 10:
        words.append(_UZ_TENS[n // 10])
        n %= 10
    if n:
        words.append(_UZ_UNITS[n])
    return " ".join(words)


def uz_ordinal(n: int) -> str:
    """15 -> "oʻn beshinchi", 2 -> "ikkinchi", 20 -> "yigirmanchi"."""
    words = uz_number(n)
    return words + ("nchi" if words[-1] in "aeiou" else "inchi")


# --------------------------------------------------------------------------- numbers in text

_SPACED = r"\d{1,3}(?:[   ]\d{3})+(?!\d)"  # "1 500 000"
_RU_ORD_SUFFIX = r"-(?:ый|ий|ой|ая|ое|ые|го|ого|ему|ому|ым|им|ом|ую|й|я|е|х|м)\b"


def _int(s: str) -> int:
    return int(re.sub(r"\D", "", s))


def numbers_to_words(text: str, lang: Lang) -> str:
    spell = ru_number if lang == "ru" else uz_number
    if lang == "uz":
        # "15-moddasiga" -> "oʻn beshinchi moddasiga", "2026-yil" -> "... oltinchi yil"
        text = re.sub(r"(\d+)-(?=[^\W\d_])", lambda m: uz_ordinal(int(m.group(1))) + " ", text)
    else:
        text = re.sub(r"(\d+)" + _RU_ORD_SUFFIX, lambda m: m.group(1), text)  # "15-го" is read as a cardinal
        text = re.sub(r"\b([1-9]|[12]\d|3[01])(?=\s+" + _RU_MONTHS_GEN + r")",
                      lambda m: ru_day_genitive(int(m.group(1))), text)
        text = re.sub(r"(\d+)\s?%", lambda m: f"{m.group(1)} " + _ru_form(int(m.group(1)),
                      ("процент", "процента", "процентов")), text)
    text = re.sub(r"(\d+),(\d+)", lambda m: f"{spell(int(m.group(1)))} {'запятая' if lang == 'ru' else 'vergul'} "
                                            f"{spell(int(m.group(2)))}", text)
    text = re.sub(r"(?<=\d)\.(?=\d)", " ", text)  # dates 21.10.2026: each part on its own
    text = text.replace("%", " процентов" if lang == "ru" else " foiz").replace("№", "номер" if lang == "ru" else "raqam")
    text = re.sub(_SPACED, lambda m: spell(_int(m.group())), text)
    return re.sub(r"\d+", lambda m: spell(int(m.group())), text)


# --------------------------------------------------------------------------- Uzbek scripts

# typographic apostrophes and the 2026 letters (ö ğ ş ç) -> the plain Latin the models were trained on
_APOSTROPHES = "ʻ‘’`ʼ"
_NEW_TO_OLD = {"ö": "o'", "Ö": "O'", "ğ": "g'", "Ğ": "G'", "ş": "sh", "Ş": "Sh", "ç": "ch", "Ç": "Ch"}


def to_plain_latin(text: str) -> str:
    text = "".join(_NEW_TO_OLD.get(c, c) for c in text)
    return re.sub(f"[{_APOSTROPHES}]", "'", text)


def latn_to_cyrl(text: str) -> str:
    """For uzb_0: the same transliteration the UI uses for uz-Cyrl (app/i18n/translit.py)."""
    return lat_to_cyr_display(text)


# --------------------------------------------------------------------------- entry point


def prepare(text: str, lang: Lang, voice: Voice) -> str:
    text = numbers_to_words(text, lang)
    if lang == "uz":
        text = latn_to_cyrl(text) if voice.script == "cyrl" else to_plain_latin(text)
    return re.sub(r"\s+", " ", text).strip()
