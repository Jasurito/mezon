"""Служебные строки, которых нет в сценарии."""

from __future__ import annotations

from app.schemas.legal import Locale

MESSAGES: dict[str, dict[str, str]] = {
    "result.disclaimer": {
        "ru": (
            "Это учебный результат. Реальный суд оценивает все обстоятельства "
            "конкретного дела, и его решение может отличаться."
        ),
        "uz-Latn": (
            "Bu o'quv natijasi. Haqiqiy sud muayyan ishning barcha holatlarini baholaydi "
            "va uning qarori boshqacha bo'lishi mumkin."
        ),
        "uz-Cyrl": (
            "Бу ўқув натижаси. Ҳақиқий суд муайян ишнинг барча ҳолатларини баҳолайди "
            "ва унинг қарори бошқача бўлиши мумкин."
        ),
    },
    "result.no_choice": {
        "ru": "Решение не принято",
        "uz-Latn": "Qaror qabul qilinmadi",
        "uz-Cyrl": "Қарор қабул қилинмади",
    },
    "result.kind.win": {"ru": "Победа", "uz-Latn": "G'alaba", "uz-Cyrl": "Ғалаба"},
    "result.kind.partial": {"ru": "Частичная победа", "uz-Latn": "Qisman g'alaba", "uz-Cyrl": "Қисман ғалаба"},
    "result.kind.loss": {"ru": "Поражение", "uz-Latn": "Mag'lubiyat", "uz-Cyrl": "Мағлубият"},
    "result.kind.settlement": {"ru": "Мировое соглашение", "uz-Latn": "Kelishuv bitimi", "uz-Cyrl": "Келишув битими"},
    "result.kind.procedural_loss": {
        "ru": "Иск оставлен без рассмотрения",
        "uz-Latn": "Da'vo ko'rilmasdan qoldirildi",
        "uz-Cyrl": "Даъво кўрилмасдан қолдирилди",
    },
    "quiz.learning_gain_note": {
        "ru": "Предварительный показатель, не доказанный эффект обучения",
        "uz-Latn": "Dastlabki ko'rsatkich, o'qitish samarasining isboti emas",
        "uz-Cyrl": "Дастлабки кўрсаткич, ўқитиш самарасининг исботи эмас",
    },
    "analytics.summary_note": {
        "ru": "Предварительные данные, малая выборка",
        "uz-Latn": "Dastlabki ma'lumotlar, tanlanma kichik",
        "uz-Cyrl": "Дастлабки маълумотлар, танланма кичик",
    },
    "dashboard.level.beginner": {"ru": "Начальный", "uz-Latn": "Boshlang'ich", "uz-Cyrl": "Бошланғич"},
    "dashboard.level.confident": {"ru": "Уверенный", "uz-Latn": "Ishonchli", "uz-Cyrl": "Ишончли"},
    "dashboard.level.advanced": {"ru": "Продвинутый", "uz-Latn": "Ilg'or", "uz-Cyrl": "Илғор"},
    "dashboard.level.none": {"ru": "Нет данных", "uz-Latn": "Ma'lumot yo'q", "uz-Cyrl": "Маълумот йўқ"},
    "dashboard.reason.soon": {"ru": "Скоро", "uz-Latn": "Tez orada", "uz-Cyrl": "Тез орада"},
    "dashboard.reason.unfinished": {
        "ru": "Не завершено", "uz-Latn": "Tugallanmagan", "uz-Cyrl": "Тугалланмаган",
    },
    "dashboard.reason.new": {"ru": "Новое дело", "uz-Latn": "Yangi ish", "uz-Cyrl": "Янги иш"},
    "mistake_category.evidence": {"ru": "Доказательства", "uz-Latn": "Dalillar", "uz-Cyrl": "Далиллар"},
    "mistake_category.procedure": {"ru": "Процедура", "uz-Latn": "Protsedura", "uz-Cyrl": "Процедура"},
    "mistake_category.substantive_law": {
        "ru": "Материальное право", "uz-Latn": "Moddiy huquq", "uz-Cyrl": "Моддий ҳуқуқ",
    },
    "mistake_category.remedy_choice": {
        "ru": "Выбор требования", "uz-Latn": "Talabni tanlash", "uz-Cyrl": "Талабни танлаш",
    },
    "score.forecast_correct": {
        "ru": "верный прогноз решения суда",
        "uz-Latn": "sud qarorini to'g'ri bashorat qildingiz",
        "uz-Cyrl": "суд қарорини тўғри башорат қилдингиз",
    },
    "skill.procedure": {"ru": "Процедура", "uz-Latn": "Protsedura", "uz-Cyrl": "Процедура"},
    "skill.evidence": {"ru": "Доказательства", "uz-Latn": "Dalillar", "uz-Cyrl": "Далиллар"},
    "skill.substantive_law": {"ru": "Нормы права", "uz-Latn": "Huquq normalari", "uz-Cyrl": "Ҳуқуқ нормалари"},
    "skill.remedy_choice": {"ru": "Выбор требования", "uz-Latn": "Talabni tanlash", "uz-Cyrl": "Талабни танлаш"},
    "skill.procedure.desc": {
        "ru": "Делать шаги в суде в нужном порядке и вовремя.",
        "uz-Latn": "Sudda qadamlarni to'g'ri tartibda va o'z vaqtida qo'yish.",
        "uz-Cyrl": "Судда қадамларни тўғри тартибда ва ўз вақтида қўйиш.",
    },
    "skill.evidence.desc": {
        "ru": "Собрать нужные доказательства и показать их суду.",
        "uz-Latn": "Kerakli dalillarni to'plash va sudga ko'rsatish.",
        "uz-Cyrl": "Керакли далилларни тўплаш ва судга кўрсатиш.",
    },
    "skill.substantive_law.desc": {
        "ru": "Опираться на правильные нормы закона в своих доводах.",
        "uz-Latn": "Dalillarda qonunning to'g'ri normalariga tayanish.",
        "uz-Cyrl": "Далилларда қонуннинг тўғри нормаларига таяниш.",
    },
    "skill.remedy_choice.desc": {
        "ru": "Выбрать требование, которое суд действительно может удовлетворить.",
        "uz-Latn": "Sud haqiqatan ham qanoatlantira oladigan talabni tanlash.",
        "uz-Cyrl": "Суд ҳақиқатан ҳам қаноатлантира оладиган талабни танлаш.",
    },
}


def message(key: str, locale: Locale) -> str:
    entry = MESSAGES.get(key)
    if entry is None:
        return key
    return entry.get(locale) or entry.get("uz-Latn" if locale == "uz-Cyrl" else "ru") or entry["ru"]
