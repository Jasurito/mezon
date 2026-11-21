"""Numbers to words and the script each voice reads."""

import pytest

from app.tts.text import latn_to_cyrl, numbers_to_words, prepare, ru_number, to_plain_latin, uz_number, uz_ordinal
from app.tts.voices import VOICES


@pytest.mark.parametrize(
    "n,ru,uz",
    [
        (0, "ноль", "nol"),
        (15, "пятнадцать", "oʻn besh"),
        (21, "двадцать один", "yigirma bir"),
        (1000, "одна тысяча", "ming"),
        (2026, "две тысячи двадцать шесть", "ikki ming yigirma olti"),
        (1_500_000, "один миллион пятьсот тысяч", "bir million besh yuz ming"),
        (12_000, "двенадцать тысяч", "oʻn ikki ming"),
    ],
)
def test_cardinals(n, ru, uz):
    assert ru_number(n) == ru
    assert uz_number(n) == uz


@pytest.mark.parametrize("n,word", [(1, "birinchi"), (2, "ikkinchi"), (15, "oʻn beshinchi"), (20, "yigirmanchi")])
def test_uz_ordinals(n, word):
    assert uz_ordinal(n) == word


def test_numbers_in_text():
    assert numbers_to_words("статье 15 ГК", "ru") == "статье пятнадцать ГК"
    assert numbers_to_words("1 500 000 сум", "ru") == "один миллион пятьсот тысяч сум"
    assert numbers_to_words("15-moddasiga", "uz") == "oʻn beshinchi moddasiga"
    assert numbers_to_words("2026-yil", "uz") == "ikki ming yigirma oltinchi yil"
    assert numbers_to_words("12,5%", "ru") == "двенадцать запятая пять процентов"
    assert numbers_to_words("неустойку 1% цены", "ru") == "неустойку один процент цены"
    assert numbers_to_words("3 % в день", "ru") == "три процента в день"
    assert numbers_to_words("с 8 августа", "ru") == "с восьмого августа"
    assert numbers_to_words("20 июля и 31 декабря", "ru") == "двадцатого июля и тридцать первого декабря"
    assert numbers_to_words("Через 8 дней", "ru") == "Через восемь дней"


def test_latn_to_cyrl():
    assert latn_to_cyrl("Sud majlisi ochiq deb eʼlon qilinadi.") == "Суд мажлиси очиқ деб эълон қилинади."
    assert latn_to_cyrl("Fuqarolik kodeksi, toʻliq hajmda") == "Фуқаролик кодекси, тўлиқ ҳажмда"
    assert latn_to_cyrl("sifatsiz") == "сифатсиз"  # the frontend's ts -> ц rule gave "сифациз"
    assert latn_to_cyrl("Sudya şartnomani köz bilan koʻrdi") == "Судья шартномани кўз билан кўрди"
    assert latn_to_cyrl("yoʻq") == "йўқ"


def test_plain_latin_for_dilnavoz():
    assert to_plain_latin("Daʼvogar boʻyicha şartnoma") == "Da'vogar bo'yicha shartnoma"


def test_prepare_per_voice():
    text = "Kodeksning 15-moddasi"
    assert prepare(text, "uz", VOICES[("uz", "male")]) == "Кодекснинг ўн бешинчи моддаси"
    assert prepare(text, "uz", VOICES[("uz", "female")]) == "Kodeksning o'n beshinchi moddasi"
    assert prepare("Статья 15.", "ru", VOICES[("ru", "male")]) == "Статья пятнадцать."
