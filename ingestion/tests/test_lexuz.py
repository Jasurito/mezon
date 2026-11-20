"""parse/segment/sources-draft на фрагменте реальной разметки lex.uz (fixtures/lexuz_fragment.html)."""

from datetime import date
from pathlib import Path

import pytest

from legal_ingestion.draft import merge_existing, read_page, render_yaml, suggest_effective_from
from legal_ingestion.normalize import normalize_blocks
from legal_ingestion.parse import parse_html
from legal_ingestion.patterns import ARTICLE, CHAPTER, POINT, SECTION, normalize_number
from legal_ingestion.segment import segment

FIXTURE = Path(__file__).parent / "fixtures" / "lexuz_fragment.html"
JUNK = ("Предложения по документу", "Прослушать аудио", "Получить ссылку", "предыдущую редакцию", "в редакции")


@pytest.fixture(scope="module")
def html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def blocks(html):
    return parse_html(html, "ru")


def test_parse_lexuz_styles_ids_and_no_junk(blocks):
    assert [b["idx"] for b in blocks] == list(range(len(blocks)))
    joined = "\n".join(b["text"] for b in blocks)
    for junk in JUNK:
        assert junk not in joined
    assert "Статья 1. Основные понятия" not in joined  # оглавление .docNavbar не берётся
    styles = [b["style"] for b in blocks]
    assert styles[:2] == ["meta", "meta"]  # ACT_FORM, ACT_TITLE
    assert blocks[2]["style"] == blocks[3]["style"] == "heading"  # раздел, глава
    assert styles.count("clause") == 2 and styles.count("footer") == 4  # подпись, место, дата, номер
    assert all(b["lex_id"] for b in blocks)
    assert blocks[2]["text"] == "РАЗДЕЛ I ОБЩИЕ ПОЛОЖЕНИЯ"  # <br> внутри заголовка → пробел
    clause = next(b for b in blocks if b["style"] == "clause")
    assert clause["text"] == "Статья 26¹. Неплатежеспособность физического лица"  # <sup>1</sup> → «¹»
    assert clause["lex_id"] == "6821713"
    assert any(b["text"].startswith("4¹) ") for b in blocks)


def test_normalize_keeps_lex_id(blocks):
    cleaned = normalize_blocks(blocks)
    assert [b.get("lex_id") for b in cleaned] == [b["lex_id"] for b in blocks]


def test_segment_lexuz(blocks):
    articles, issues = segment(normalize_blocks(blocks), "ru", "T")
    assert issues == []
    assert [a["article_number"] for a in articles] == ["26¹", "26"]  # порядок фрагмента: статьи вырезаны из разных актов
    a1, a2 = articles
    assert a1["article_title"] == "Неплатежеспособность физического лица"
    assert (a1["section"], a1["chapter"]) == ("I", "3")
    assert a1["anchor"] == "6821713"
    assert len(a1["parts"]) == 2  # часть = абзац ACT_TEXT
    assert not any(j in a1["content"] for j in JUNK)
    # пункты 4) и 4¹) остались внутри своей части; подпись и реквизиты в конец статьи не попали
    assert len(a2["parts"]) == 1
    lines = a2["parts"][0]["content"].split("\n")
    assert lines[0].endswith("дела:") and lines[1].startswith("4) ") and lines[2].startswith("4¹) ")
    assert "КАРИМОВ" not in a2["content"] and "Ташкент" not in a2["content"]
    assert a2["anchor"] == "3518693"


def test_segment_lexuz_preamble_and_unknown_heading():
    def blk(i, text, style):
        return {"idx": i, "text": text, "style": style, "lex_id": str(100 + i)}

    articles, issues = segment(
        [
            blk(0, "КОНСТИТУЦИЯ РЕСПУБЛИКИ УЗБЕКИСТАН", "meta"),
            blk(1, "ПРЕАМБУЛА", "heading"),
            blk(2, "Мы, единый народ Узбекистана,", "paragraph"),
            blk(3, "РАЗДЕЛ ПЕРВЫЙ. ОСНОВНЫЕ ПРИНЦИПЫ", "heading"),
            blk(4, "Глава IХ. Права", "heading"),  # кириллическая «Х»
            blk(5, "Статья 1.", "clause"),
            blk(6, "Текст статьи.", "paragraph"),
            blk(7, "Статья 2. Договор. Статья 3. не заголовок", "paragraph"),  # в абзаце статьёй не считается
        ],
        "ru",
        "T",
    )
    assert issues == []
    pre, a1 = articles
    assert pre["article_number"] == "preamble" and pre["anchor"] == "101"
    assert [p["content"] for p in pre["parts"]] == ["Мы, единый народ Узбекистана,"]
    assert (a1["section"], a1["chapter"], a1["article_title"]) == ("I", "IX", None)
    assert len(a1["parts"]) == 2

    _, issues = segment(
        [blk(0, "Статья 1. Т", "clause"), blk(1, "Что-то непонятное", "heading"), blk(2, "Текст", "paragraph")], "ru", "T"
    )
    assert any("неопознанный заголовок" in i for i in issues) and any("вне статьи" in i for i in issues)


def test_segment_skips_part_subsection_paragraph_headings():
    def blk(i, text, style="heading"):
        return {"idx": i, "text": text, "style": style, "lex_id": str(i)}

    articles, issues = segment(
        [
            blk(0, "Часть первая"),
            blk(1, "РАЗДЕЛ I ОБЩИЕ ПОЛОЖЕНИЯ"),
            blk(2, "Подраздел 1 ОСНОВНЫЕ ПОЛОЖЕНИЯ"),
            blk(3, "ГЛАВА 1 ГРАЖДАНСКОЕ ЗАКОНОДАТЕЛЬСТВО"),
            blk(4, "§ 1. Общие положения"),
            blk(5, "Статья 1. Основные начала", "clause"),
            blk(6, "Текст.", "paragraph"),
            blk(7, "Birinchi qism"),  # другой язык не мешает: для ru это неопознанный заголовок
        ],
        "ru",
        "T",
    )
    assert [a["article_number"] for a in articles] == ["1"]
    assert (articles[0]["section"], articles[0]["chapter"]) == ("I", "1")
    assert len(issues) == 1 and "неопознанный заголовок" in issues[0]


@pytest.mark.parametrize(
    "lang,text,expected",
    [
        ("ru", "Глава 23¹. Особенности", "23¹"),
        ("ru", "ГЛАВА 14. ПРАВО", "14"),
        ("ru", "Глава ХХVII. Оборона", "ХХVII"),
        ("uz-Latn", "23¹-bob. Korxonalar", "23¹"),
        ("uz-Latn", "XVI bob. Maʼmuriy", "XVI"),
        ("uz-Latn", "3-BOB FUQAROLAR", "3"),
    ],
)
def test_chapter_patterns(lang, text, expected):
    assert CHAPTER[lang].match(text).group(1) == expected


@pytest.mark.parametrize(
    "lang,text,expected",
    [
        ("ru", "РАЗДЕЛ ПЕРВЫЙ. ОСНОВНЫЕ ПРИНЦИПЫ", "I"),
        ("ru", "РАЗДЕЛ ЧЕТВЕРТЫЙ. УСТРОЙСТВО", "IV"),
        ("ru", "Раздел III ОБЯЗАТЕЛЬСТВЕННОЕ ПРАВО", "III"),
        ("uz-Latn", "BIRINCHI BOʻLIM. ASOSIY PRINSIPLAR", "I"),
        ("uz-Latn", "TOʻRTINCHI BOʻLIM. TUZILISH", "IV"),
        ("uz-Latn", "I BOʻLIM. UMUMIY QOIDALAR", "I"),
    ],
)
def test_section_patterns(lang, text, expected):
    m = SECTION[lang].match(text)
    assert normalize_number(m.group(1), lang) == expected


def test_article_and_point_patterns():
    assert ARTICLE["ru"].match("Статья 173². Название").group(1) == "173²"
    assert ARTICLE["ru"].match("Стать 419²⁵. Сроки").group(1) == "419²⁵"  # опечатка lex.uz
    assert ARTICLE["uz-Latn"].match("31¹-modda. Nomi").group(1) == "31¹"
    assert ARTICLE["uz-Latn"].match("599- modda. Nomi").group(1) == "599"
    assert POINT.match("4¹) текст") and POINT.match("а) текст") and not POINT.match("Статья 4")


def test_read_page_and_suggested_date(html):
    info = read_page(html)
    assert (info.title, info.number, info.adoption_date) == ("О защите прав потребителей", "221-I", date(1996, 4, 26))
    assert info.document_type == "law"
    assert info.selected == date(2026, 1, 19)
    assert max(info.edition_dates) == date(2025, 11, 2)
    # самая поздняя дата ≤ даты скачивания; открытая на странице редакция входит в список
    assert suggest_effective_from(info, date(2026, 11, 20)) == date(2026, 1, 19)
    assert suggest_effective_from(info, date(2025, 12, 1)) == date(2025, 11, 2)


def test_merge_existing_keeps_human_fields():
    draft = {
        "terms_of_use": {"checked_by": None, "fetch_allowed": False},
        "documents": [
            {
                "document_key": "X",
                "title": {"ru": "A"},
                "document_type": "law",
                "source_url": "https://lex.uz/docs/1",
                "status": "in_force",
                "known_gaps": {},
                "issuing_body": None,
                "versions": [
                    {
                        "language": "ru",
                        "file": "raw/X_ru_2026-11-20.html",
                        "source_url": "https://lex.uz/docs/1",
                        "effective_from": date(2026, 1, 19),
                        "_suggested": date(2026, 1, 19),
                        "verified_by": None,
                        "_note": "n",
                    }
                ],
            }
        ],
    }
    existing = {
        "terms_of_use": {"checked_by": "AM"},
        "documents": [
            {
                "document_key": "X",
                "issuing_body": "Олий Мажлис",
                "known_gaps": {"ru": ["5"]},
                "versions": [{"language": "ru", "effective_from": date(2026, 2, 1), "verified_by": "AM"}],
            }
        ],
    }
    out = merge_existing(draft, existing)
    d = out["documents"][0]
    assert out["terms_of_use"]["checked_by"] == "AM"
    assert d["issuing_body"] == "Олий Мажлис" and d["known_gaps"] == {"ru": ["5"]}
    assert d["versions"][0]["effective_from"] == date(2026, 2, 1) and d["versions"][0]["verified_by"] == "AM"
    text = render_yaml(out)
    assert "2026-02-01\n" in text and "предложено автоматически" not in text  # изменённую человеком дату не помечаем
