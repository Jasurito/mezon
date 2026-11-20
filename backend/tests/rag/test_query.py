"""Разбор запроса без БД: язык, нормализация, явные ссылки, стоп-слова, транслитерация."""

import pytest

from app.rag.fusion import rrf
from app.rag.language import detect_language
from app.rag.normalize import APOSTROPHE, cyr_to_lat, lat_to_cyr, normalize, tokenize
from app.rag.refs import extract_article_numbers, extract_refs, matches_document
from app.rag.stopwords import content_tokens
from app.rag.validate import validate_blocks
from app.schemas.rag import MentorBlock


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Как вернуть телефон с недостатком?", "ru"),
        ("Можно ли расторгнуть договор купли-продажи", "ru"),
        ("Nuqsonli telefonni qanday qaytarish mumkin?", "uz-Latn"),
        ("Oʻzbekiston Respublikasi fuqarolik kodeksi", "uz-Latn"),
        ("Нуқсонли телефонни қандай қайтариш мумкин?", "uz-Cyrl"),
        ("Харидор товарни қайтаришга ҳақлими", "uz-Cyrl"),
        ("Товар учун пул ва кафолат", "uz-Cyrl"),  # без особых букв, по стоп-словам
        ("12345 ???", "ru"),  # по умолчанию
    ],
)
def test_detect_language(text, expected):
    assert detect_language(text) == expected


def test_detect_language_default_is_configurable():
    assert detect_language("123", default="uz-Latn") == "uz-Latn"


def test_normalize_apostrophes_spaces_case():
    variants = ["o'zbek", "oʻzbek", "o‘zbek", "o’zbek", "oʼzbek", "o`zbek"]
    assert {normalize(v) for v in variants} == {f"o{APOSTROPHE}zbek"}
    assert normalize("Статья 15.   ЁЛКА  ") == "статья 15. елка"
    assert normalize("Soft­hyphen​") == "softhyphen"


def test_normalize_cyrillic_uzbek_to_latin_only_when_asked():
    assert normalize("Қайтариш") == "қайтариш"
    assert normalize("Қайтариш", "uz-Cyrl") == "qaytarish"
    assert normalize("ўзбек ғалаба ҳақ", "uz-Cyrl") == f"o{APOSTROPHE}zbek g{APOSTROPHE}alaba haq"
    assert normalize("Ёш еттита", "uz-Cyrl") == "yosh yettita"


def test_transliteration_roundtrip():
    assert cyr_to_lat("шаҳар чегара") == "shahar chegara"
    assert lat_to_cyr("shahar chegara") == "шаҳар чегара"
    for word in ["харидор", "сифатсиз", "қайтариш", "ўзбек"]:
        assert lat_to_cyr(cyr_to_lat(word)) == word


@pytest.mark.parametrize(
    "text,numbers",
    [
        ("Что сказано в ст. 15?", ["15"]),
        ("статья 15 и статья 16", ["15", "16"]),
        ("статьи 15, 16 и 17", ["15", "16", "17"]),
        ("ст.ст. 3, 4", ["3", "4"]),
        ("в статье 15-1 сказано", ["15-1"]),
        ("15-modda nima deydi", ["15"]),
        ("fuqarolik kodeksining 15-moddasi", ["15"]),
        ("15-модда бўйича", ["15"]),
        ("страница 15 и лист 3", []),
        ("стр. 15", []),
    ],
)
def test_extract_article_numbers(text, numbers):
    assert extract_article_numbers(text) == numbers


def test_extract_refs_with_document_hint():
    def pairs(text):
        return [(r.hint, r.number) for r in extract_refs(text)]

    assert pairs("ст. 15 ГК РУз") == [("civil", "15")]
    assert pairs("статья 15 ГПК") == [("civil_procedure", "15")]
    assert pairs("статья 7 закона о защите прав потребителей") == [("consumer", "7")]
    assert pairs("15-modda FK") == [("civil", "15")]
    assert pairs("в ГПК ст. 9") == [("civil_procedure", "9")]
    assert pairs("ст. 20") == [(None, "20")]
    assert pairs("ст. 5 ГК и ст. 6 ГПК") == [("civil", "5"), ("civil_procedure", "6")]


def test_matches_document_by_key_and_title():
    assert matches_document("civil_procedure", "TEST_CPC", ["x"])
    assert matches_document("civil", "CC", [])
    assert not matches_document("civil", "TEST_CPC", ["Тестовый документ"])
    assert matches_document("civil", "X", ["Гражданский кодекс Республики Узбекистан"])
    assert not matches_document("civil", "X", ["Гражданский процессуальный кодекс"])


def test_stopwords_removed():
    toks = tokenize(normalize("Как мне вернуть товар в магазин и что делать?"))
    assert content_tokens(toks, "ru") == ["вернуть", "товар", "магазин", "делать"]
    uz = tokenize(normalize("Tovarni qanday qaytarish mumkin va kerak?", "uz-Latn"))
    assert content_tokens(uz, "uz-Latn") == ["tovarni", "qaytarish"]
    assert content_tokens(["а", "15", "x"], "ru") == ["15"]


def test_tokenize_keeps_apostrophe_inside_word():
    assert tokenize(normalize("oʻzbek, g'alaba!")) == [f"o{APOSTROPHE}zbek", f"g{APOSTROPHE}alaba"]


def test_rrf_merge():
    scores = rrf([[1, 2, 3], [3, 1]], k=60)
    assert scores[1] == pytest.approx(1 / 61 + 1 / 62)
    assert scores[3] == pytest.approx(1 / 63 + 1 / 61)
    assert scores[2] == pytest.approx(1 / 62)
    assert sorted(scores, key=lambda d: -scores[d]) == [1, 3, 2]


def test_validate_blocks_rules():
    sources = {"c1": "10", "c2": "11"}
    blocks = [
        MentorBlock(text="Покупатель может вернуть товар.", source_ids=["c1"]),
        MentorBlock(text="Из выдуманного источника.", source_ids=["c9"]),
        MentorBlock(text="Это сказано в ст. 999.", source_ids=["c1"]),
        MentorBlock(text="Это сказано в статье 10.", source_ids=[]),
        MentorBlock(text="Общее пояснение без ссылок.", source_ids=[]),
        MentorBlock(text="Статья 10 и 11-modda вместе.", source_ids=["c1", "c2"]),
        MentorBlock(text="Статья 11 здесь, но источник только c1.", source_ids=["c1"]),
        MentorBlock(text="   ", source_ids=["c1"]),
    ]
    res = validate_blocks(blocks, sources)
    assert [b.text for b in res.kept] == [
        "Покупатель может вернуть товар.",
        "Общее пояснение без ссылок.",
        "Статья 10 и 11-modda вместе.",
    ]
    assert res.dropped == 5
    assert all(b.verified for b in res.kept)
