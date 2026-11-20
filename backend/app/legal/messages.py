"""Localized service notes of the legal corpus. Law text itself is never translated."""

from __future__ import annotations

from datetime import date

LANGUAGE_NAMES: dict[str, dict[str, str]] = {
    "ru": {"ru": "русском языке", "uz-Latn": "узбекском языке (латиница)", "uz-Cyrl": "узбекском языке (кириллица)"},
    "uz-Latn": {"ru": "rus tilida", "uz-Latn": "oʻzbek tilida (lotin)", "uz-Cyrl": "oʻzbek tilida (kirill)"},
    "uz-Cyrl": {"ru": "рус тилида", "uz-Latn": "ўзбек тилида (лотин)", "uz-Cyrl": "ўзбек тилида (кирилл)"},
}

_FALLBACK_LANGUAGE = {
    "ru": "Текст на выбранном языке отсутствует. Показан официальный текст на {language}.",
    "uz-Latn": "Tanlangan tilda matn mavjud emas. Rasmiy matn {language} koʻrsatilgan.",
    "uz-Cyrl": "Танланган тилда матн мавжуд эмас. Расмий матн {language} кўрсатилган.",
}

_UNCONFIRMED = {
    "ru": "Редакция на {date} не подтверждена. Показан текст действующей редакции.",
    "uz-Latn": "{date} sanasidagi tahrir tasdiqlanmagan. Amaldagi tahrir matni koʻrsatilgan.",
    "uz-Cyrl": "{date} санасидаги таҳрир тасдиқланмаган. Амалдаги таҳрир матни кўрсатилган.",
}


def language_name(locale: str, language: str) -> str:
    return LANGUAGE_NAMES.get(locale, LANGUAGE_NAMES["ru"]).get(language, language)


def fallback_language_note(locale: str, language: str) -> str:
    tpl = _FALLBACK_LANGUAGE.get(locale, _FALLBACK_LANGUAGE["ru"])
    return tpl.format(language=language_name(locale, language))


def unconfirmed_note(locale: str, on_date: date) -> str:
    tpl = _UNCONFIRMED.get(locale, _UNCONFIRMED["ru"])
    return tpl.format(date=on_date.strftime("%d.%m.%Y"))
