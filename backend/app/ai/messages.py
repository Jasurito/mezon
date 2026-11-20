"""Тексты наставника на трёх языках (язык = язык вопроса)."""

from __future__ import annotations

from app.schemas.legal import Locale

_MESSAGES: dict[str, dict[Locale, str]] = {
    "disclaimer": {
        "ru": "Образовательное объяснение, не юридическая консультация",
        "uz-Latn": "Ta’limiy tushuntirish, yuridik maslahat emas",
        "uz-Cyrl": "Таълимий тушунтириш, юридик маслаҳат эмас",
    },
    "out_of_scope": {
        "ru": "Я помогаю разбираться в правовых вопросах по загруженной правовой базе и в ваших делах из игры. "
        "Этот вопрос выходит за эти рамки, попробуйте спросить о нормах закона или о вашем деле.",
        "uz-Latn": "Men yuklangan huquqiy baza va o‘yindagi ishlaringiz bo‘yicha huquqiy savollarga yordam beraman. "
        "Bu savol shu doiradan tashqarida; qonun normalari yoki o‘z ishingiz haqida so‘rab ko‘ring.",
        "uz-Cyrl": "Мен юкланган ҳуқуқий база ва ўйиндаги ишларингиз бўйича ҳуқуқий саволларга ёрдам бераман. "
        "Бу савол шу доирадан ташқарида; қонун нормалари ёки ўз ишингиз ҳақида сўраб кўринг.",
    },
    "insufficient": {
        "ru": "В загруженной правовой базе недостаточно источников, чтобы ответить на этот вопрос.",
        "uz-Latn": "Yuklangan huquqiy bazada bu savolga javob berish uchun manbalar yetarli emas.",
        "uz-Cyrl": "Юкланган ҳуқуқий базада бу саволга жавоб бериш учун манбалар етарли эмас.",
    },
    "ai_unavailable": {
        "ru": "AI-объяснение сейчас недоступно. Вот нормы, которые относятся к вашему вопросу.",
        "uz-Latn": "AI tushuntirishi hozir mavjud emas. Savolingizga tegishli normalar quyida.",
        "uz-Cyrl": "AI тушунтириши ҳозир мавжуд эмас. Саволингизга тегишли нормалар қуйида.",
    },
}


def msg(key: str, locale: Locale) -> str:
    variants = _MESSAGES[key]
    return variants.get(locale) or variants["ru"]


LANGUAGE_NAMES: dict[Locale, str] = {
    "ru": "Russian",
    "uz-Latn": "Uzbek (Latin script)",
    "uz-Cyrl": "Uzbek (Cyrillic script)",
}
