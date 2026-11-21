"""uz-Latn → uz-Cyrl для показа и запасной перевод uz-Cyrl."""

from types import SimpleNamespace

import pytest

from app.i18n.translate import translate
from app.i18n.translit import lat_to_cyr_display as t


@pytest.mark.parametrize(
    "src, expected",
    [
        ("Telefon 10 kundan keyin buzildi", "Телефон 10 кундан кейин бузилди"),
        ("Oʻquv vaziyati. Ismlar va doʻkon toʻqima.", "Ўқув вазияти. Исмлар ва дўкон тўқима."),
        ("Isteʼmolchilar huquqlarini himoya qilish toʻgʻrisida", "Истеъмолчилар ҳуқуқларини ҳимоя қилиш тўғрисида"),
        ("«Nur Elektroniks» doʻkoni", "«Нур Электроникс» дўкони"),
        ("Yer, yosh, yuz, ming, choy, Shahar, gʻoya, SHAXS", "Ер, ёш, юз, минг, чой, Шаҳар, ғоя, ШАХС"),
        ("Kirill: уже кириллица", "Кирилл: уже кириллица"),
    ],
)
def test_lat_to_cyr_display(src, expected):
    assert t(src) == expected


def test_translate_uz_cyrl_falls_back_to_transliterated_latin():
    loaded = SimpleNamespace(texts={"ru": {"k": "Телефон"}, "uz-Latn": {"k": "Telefon buzildi"}, "uz-Cyrl": {}})
    assert translate(loaded, "k", "uz-Cyrl") == "Телефон бузилди"
    assert translate(loaded, "k", "uz-Latn") == "Telefon buzildi"


def test_translate_uz_cyrl_prefers_own_text_then_ru():
    loaded = SimpleNamespace(texts={"ru": {"a": "Рус"}, "uz-Latn": {}, "uz-Cyrl": {"b": "Ўз матн"}})
    assert translate(loaded, "b", "uz-Cyrl") == "Ўз матн"
    assert translate(loaded, "a", "uz-Cyrl") == "Рус"
