"""uz-Latn → uz-Cyrl для показа: сохраняет регистр, цифры и знаки.

Используется как запасной вариант, когда у текста нет кириллической версии
(тексты дел, названия документов). Тексты статей закона не транслитерируются.
"""

from __future__ import annotations

# варианты апострофа после o/g (oʻ, gʻ) и знак тутуқ (ʼ → ъ)
_TURNED = "ʻ‘'`ʹ"
_TUTUQ = "ʼ’"
_VOWELS = set("aeiouAEIOUоаеиуэОАЕИУЭ")

_DIGRAPHS = {"sh": "ш", "ch": "ч", "ya": "я", "yo": "ё", "yu": "ю", "ye": "е"}
_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ", "i": "и",
    "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о", "p": "п", "q": "қ",
    "r": "р", "s": "с", "t": "т", "u": "у", "v": "в", "x": "х", "y": "й", "z": "з", "c": "с", "w": "в",
}


def _case(src: str, out: str) -> str:
    return out.upper() if src[:1].isupper() else out


def lat_to_cyr_display(text: str) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        low = ch.lower()
        nxt = text[i + 1] if i + 1 < n else ""
        word_start = i == 0 or not text[i - 1].isalpha()
        if low in "og" and nxt in _TURNED:
            out.append(_case(ch, "ў" if low == "o" else "ғ"))
            i += 2
            continue
        pair = (ch + nxt).lower()
        if pair in _DIGRAPHS:
            out.append(_case(ch, _DIGRAPHS[pair]))
            i += 2
            continue
        if ch in _TUTUQ or (ch in _TURNED and i > 0 and text[i - 1].isalpha()):
            out.append("ъ")
            i += 1
            continue
        if low == "e" and (word_start or (i > 0 and text[i - 1] in _VOWELS)):
            out.append(_case(ch, "э"))
            i += 1
            continue
        if low in _SINGLE:
            out.append(_case(ch, _SINGLE[low]))
        else:
            out.append(ch)
        i += 1
    return "".join(out)
