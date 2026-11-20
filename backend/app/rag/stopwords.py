"""Короткие списки стоп-слов. FTS с конфигом 'simple' их не убирает, а без этого любой
вопрос совпадёт с любым текстом по «в», «как», «и»."""

from __future__ import annotations

from app.rag.normalize import APOSTROPHE as _A

RU = frozenset(
    """
    а без более бы был была были было быть в вам вас весь во вот все всё всего вы где да даже для до
    его ее её ей ему если есть еще ещё ж же за здесь и из или им их к как какая какие какой какую когда
    кто ли либо мне может можно мной мы на над надо наш не него нее нет ни них но ну о об однако
    он она они оно от очень по под после при про с со так также такой там те тем то тогда того той только
    том тот ту у уж уже хотя чего чем что чтобы эта эти это этого этой этом этот я
    почему зачем нужно должен должна ль
    """.split()
)

# Узбекская латиница; слова с апострофом записаны через "'" и приводятся к каноническому ʻ.
_UZ_LATIN = (
    "va bilan uchun yoki ham hamda bu shu u ular biz siz men sen nima nega qanday qanaqa qaysi kim "
    "qachon qayerda qayerga bor yoq emas edi ekan mumkin kerak lekin biroq ammo agar balki haqida "
    "boyicha kabi bir ikki hozir endi deb degan qilish qilib "
    "yo'q bo'yicha bo'lsa bo'lgan bo'ladi o'z"
).split()

UZ = frozenset({w.replace("'", _A) for w in _UZ_LATIN} | {w.replace("'", "") for w in _UZ_LATIN})

# Узбекские слова кириллицей, которых нет в русском: признак uz-Cyrl при определении языка.
UZ_CYRL_MARKERS = frozenset(
    (
        "ва билан учун ёки ҳам ҳамда бу шу улар биз сиз мен нима нега қандай қайси ким қачон бор йўқ "
        "эмас эди экан мумкин керак лекин аммо агар ҳақида бўйича каби бир икки ҳозир энди бўлса "
        "бўлган бўлади қилиш қилиб деб деган"
    ).split()
)

_BY_LANG = {"ru": RU, "uz-Latn": UZ, "uz-Cyrl": UZ}


def stopwords_for(language: str) -> frozenset[str]:
    return _BY_LANG.get(language, RU)


def content_tokens(tokens: list[str], language: str) -> list[str]:
    """Токены без стоп-слов и одиночных букв; дубликаты убираются, порядок сохраняется."""
    stop = stopwords_for(language)
    out: list[str] = []
    for t in tokens:
        if t in stop or (len(t) < 2 and not t.isdigit()):
            continue
        if t not in out:
            out.append(t)
    return out
