import pytest

import ing_synthetic as syn
from app.rag.search import strip_header
from legal_ingestion.chunk import MAX_TOKENS, build_chunks, estimate_tokens
from legal_ingestion.normalize import clean_text, normalize_blocks
from legal_ingestion.parse import parse_docx, parse_html
from legal_ingestion.segment import segment


def _blocks(lang, fmt, tmp_path, variant="v1"):
    if fmt == "html":
        return parse_html(syn.html_doc(lang, variant), lang, body_selectors=("main",))
    path = tmp_path / "x.docx"
    syn.write_docx(path, lang, variant)
    return parse_docx(path, lang)


@pytest.mark.parametrize("fmt", ["html", "docx"])
@pytest.mark.parametrize("lang", syn.LANGS)
def test_parse_removes_junk_and_keeps_order(lang, fmt, tmp_path):
    blocks = _blocks(lang, fmt, tmp_path)
    texts = [b["text"] for b in blocks]
    joined = " ".join(texts)
    for junk in ("Шапка", "Меню", "Подвал", "tracker", "track()", "color: red"):
        assert junk not in joined
    expected = [t for _, t in syn.blocks(lang)]
    assert [t.replace("\xa0", " ") for t in texts] == expected
    assert [b["idx"] for b in blocks] == list(range(len(blocks)))
    styles = {b["text"].replace("\xa0", " "): b["style"] for b in blocks}
    t = syn._T[lang]
    assert styles[t["note"]] == "note"
    assert styles[t["art"].format(n=1, t=t["t1"])] == "heading"
    assert styles[t["preamble"]] == "paragraph"


def test_parse_html_fallback_to_body_when_no_selector():
    blocks = parse_html("<body><nav>x</nav><p>Один</p><div>Два<br>Три</div></body>", "ru", body_selectors=("#nope",))
    assert [b["text"] for b in blocks] == ["Один", "Два", "Три"]


def test_clean_text_only_junk():
    assert clean_text("a  b  c­d&nbsp;e<br>f") == "a b cd e f"
    # дословность: регистр, апострофы, нумерация и оговорки не трогаются
    s = "Статья 5¹. Oʻzbek ’ ʼ 1) а) за исключением случаев…"
    assert clean_text(s) == s


@pytest.mark.parametrize("fmt", ["html", "docx"])
@pytest.mark.parametrize("lang", syn.LANGS)
def test_segment_structure(lang, fmt, tmp_path):
    t = syn._T[lang]
    cleaned = normalize_blocks(_blocks(lang, fmt, tmp_path))
    articles, issues = segment(cleaned, lang, "T")
    assert issues == []
    assert [a["article_number"] for a in articles] == ["preamble", "1", "2", "2¹", "3", "4"]
    by = {a["article_number"]: a for a in articles}

    assert [p["content"] for p in by["preamble"]["parts"]] == [t["title"], t["preamble"]]
    assert by["preamble"]["article_title"] is None

    a1 = by["1"]
    assert a1["article_title"] == t["t1"]
    assert a1["section"] == "I" and a1["chapter"] == "1"
    assert [p["part_number"] for p in a1["parts"]] == [1, 2]
    assert a1["parts"][0]["content"] == t["p1a"] + "\n1) " + t["point"]  # пункт остался в своей части
    assert a1["parts"][1]["content"] == t["p1b"]

    a2 = by["2"]
    assert [p["kind"] for p in a2["parts"]] == ["text", "note"]
    assert a2["parts"][1]["content"] == t["note"]

    assert by["2¹"]["article_title"] == t["t2i"]
    assert by["3"]["status"] == "repealed"
    assert by["3"]["parts"][0]["content"] == t["repealed"]
    assert by["1"]["status"] == "in_force"
    assert by["4"]["chapter"] == "2"
    assert len(by["4"]["parts"]) == syn.LONG_PARTS
    assert a1["content"] == "\n".join(p["content"] for p in a1["parts"])
    # поиск: нормализованный текст в латинице для uz-Cyrl
    if lang == "uz-Cyrl":
        assert "birinchi" in a1["content_normalized"]
    assert a1["content_normalized"] == a1["content_normalized"].lower()


def test_segment_dash_number_kept_and_duplicates_reported():
    blocks = [
        {"idx": 0, "text": "Статья 25-1. Вставная", "style": "heading"},
        {"idx": 1, "text": "Текст.", "style": "paragraph"},
        {"idx": 2, "text": "Статья 25-1. Дубль", "style": "heading"},
        {"idx": 3, "text": "Текст.", "style": "paragraph"},
    ]
    articles, issues = segment(blocks, "ru", "T")
    assert articles[0]["article_number"] == "25-1"
    assert any("повторяющийся" in i for i in issues)


def test_segment_chapter_title_on_next_line():
    blocks = [
        {"idx": 0, "text": "Глава 3", "style": "heading"},
        {"idx": 1, "text": "Название главы", "style": "heading"},
        {"idx": 2, "text": "Статья 7. Т", "style": "heading"},
        {"idx": 3, "text": "Текст.", "style": "paragraph"},
    ]
    articles, _ = segment(blocks, "ru", "T")
    assert [a["article_number"] for a in articles] == ["7"]
    assert articles[0]["chapter"] == "3"


@pytest.mark.parametrize("lang", syn.LANGS)
def test_chunks(lang, tmp_path):
    cleaned = normalize_blocks(_blocks(lang, "html", tmp_path))
    articles, _ = segment(cleaned, lang, "T")
    title = "Тестовый закон"
    chunks = build_chunks(articles, doc_title=title, language=lang, effective_from="2024-01-01")
    by_art: dict[str, list] = {}
    for c in chunks:
        by_art.setdefault(c["article_number"], []).append(c)

    assert len(by_art["1"]) == 1 and (by_art["1"][0]["part_from"], by_art["1"][0]["part_to"]) == (1, 2)
    long_chunks = by_art["4"]
    assert len(long_chunks) >= 2
    assert all(c["token_count"] <= MAX_TOKENS for c in long_chunks)
    assert all(estimate_tokens(c["text"]) == c["token_count"] for c in long_chunks)
    # границы только между частями: диапазоны смежные, без пропусков и наложений, части целиком
    assert long_chunks[0]["part_from"] == 1 and long_chunks[-1]["part_to"] == syn.LONG_PARTS
    for a, b in zip(long_chunks, long_chunks[1:]):
        assert b["part_from"] == a["part_to"] + 1
    a4 = next(a for a in articles if a["article_number"] == "4")
    for c in long_chunks:
        body = strip_header(c["text"])  # формат заголовка совпадает с форматом бэкенда
        for p in a4["parts"][c["part_from"] - 1 : c["part_to"]]:
            assert p["content"] in body
        assert not body.startswith("[")
    # заголовок: «[документ · статья. название · части · редакция от даты · язык]»
    head = by_art["1"][0]["text"].split("\n", 1)[0]
    assert head.startswith(f"[{title} · ") and head.endswith(f" · редакция от 2024-01-01 · {lang}]")
    assert "части 1–2" in head
    assert strip_header(by_art["1"][0]["text"]).startswith(syn._T[lang]["p1a"])
    assert all(c["text_normalized"] == c["text_normalized"].lower() for c in chunks)
