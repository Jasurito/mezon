"""GET /api/legal/search на тестовом корпусе (без LLM, без сети)."""

import pytest

from app.rag.deps import embedder_dep
from tests.fixtures.rag_seed import RAG_CITATION_RETURN, FakeEmbedder, seed_fake_embeddings

pytestmark = pytest.mark.db


@pytest.fixture
def client(make_client):
    with make_client() as c:
        yield c


def search(client, q, **params):
    r = client.get("/api/legal/search", params={"q": q, **params})
    assert r.status_code == 200, r.text
    return r.json()


def test_semantic_query_found_by_fts(client):
    body = search(client, "вернуть товар с недостатком", locale="ru")
    assert body["detected_language"] == "ru"
    top = body["results"][0]
    assert top["article_number"] == "10"
    assert top["citation_id"] == RAG_CITATION_RETURN
    assert top["document_title"] == "Тестовый закон о возврате товара"
    assert top["article_title"] == "Возврат товара ненадлежащего качества"
    assert top["parts"] == "1–2"
    assert top["edition_status"] == "current"
    assert top["source_url"] == "https://example.test/TEST_RAG/ru"
    assert top["match"] == {"exact_article": False, "dense_rank": None, "sparse_rank": 1}
    assert top["score"] > 0
    assert "вернуть товар" in top["snippet"] and len(top["snippet"]) <= 300
    assert not top["snippet"].startswith("[")  # заголовок чанка в выдачу не попадает
    assert set(top) == {
        "chunk_id", "article_id", "citation_id", "document_title", "article_number", "article_title",
        "parts", "snippet", "edition_status", "source_url", "score", "match",
    }


def test_stopwords_do_not_match_everything(client):
    # Только стоп-слова: без них FTS 'simple' совпал бы с любым текстом.
    assert search(client, "как и в что это", locale="ru")["results"] == []


def test_one_result_per_article(client):
    ids = [r["article_id"] for r in search(client, "товар статья тестовая", locale="ru")["results"]]
    assert len(ids) == len(set(ids))


def test_explicit_reference_goes_first(client):
    body = search(client, "что говорит ст. 11", locale="ru")
    first = body["results"][0]
    assert first["article_number"] == "11" and first["match"]["exact_article"] is True
    assert all(not r["match"]["exact_article"] for r in body["results"][1:])


def test_explicit_reference_with_document_hint(client):
    body = search(client, "статья 1 ГПК", locale="ru")
    first = body["results"][0]
    assert first["match"]["exact_article"] is True
    assert first["document_title"] == "Тестовый документ TEST_CPC"
    exact = [r for r in body["results"] if r["match"]["exact_article"]]
    assert len(exact) == 1  # статья 1 других документов под подсказку не подпадает


def test_explicit_reference_to_missing_document_is_not_substituted(client):
    # Конституции в корпусе нет: статью 1 других документов подставлять нельзя.
    body = search(client, "статья 1 Конституции", locale="ru")
    assert not any(r["match"]["exact_article"] for r in body["results"])


def test_explicit_reference_uzbek(client):
    body = search(client, "10-modda", locale="uz-Latn")
    first = body["results"][0]
    assert first["article_number"] == "10" and first["match"]["exact_article"] is True
    assert first["article_title"] == "Sifatsiz tovarni qaytarish"
    assert first["document_title"] == "Tovarni qaytarish haqida test qonuni"


def test_query_outside_corpus_is_empty(client):
    body = search(client, "оформить развод через загс", locale="ru")
    assert body["results"] == []


def test_uzbek_cyrillic_query_hits_transliterated_text(client):
    body = search(client, "сифатсиз товарни қайтариш")
    assert body["detected_language"] == "uz-Cyrl"
    top = body["results"][0]
    assert top["article_number"] == "10"
    assert top["document_title"] == "Товарни қайтариш ҳақида тест қонуни"
    assert top["article_title"] == "Сифатсиз товарни қайтариш"


def test_language_filter_prefers_locale_version(client):
    body = search(client, "tovarni qaytarish", locale="uz-Latn")
    assert body["results"][0]["document_title"] == "Tovarni qaytarish haqida test qonuni"
    ru = search(client, "вернуть товар", locale="ru")
    assert all(r["document_title"] != "Tovarni qaytarish haqida test qonuni" for r in ru["results"])


def test_past_date_gets_historical_edition(client):
    past = search(client, "старая", locale="ru", date="2022-06-01")
    hit = past["results"][0]
    assert hit["edition_status"] == "historical" and "старая" in hit["snippet"]
    assert past["date"] == "2022-06-01"
    # сегодня старая редакция не действует
    assert search(client, "старая", locale="ru")["results"] == []
    # а новая редакция в 2022 году ещё не действовала
    assert search(client, "новая", locale="ru", date="2022-06-01")["results"] == []
    assert search(client, "новая", locale="ru")["results"][0]["edition_status"] == "current"


def test_limit(client):
    body = search(client, "тестовая статья", locale="ru", limit=2)
    assert len(body["results"]) == 2


def test_empty_query_is_422(client):
    for q in ("", "   "):
        r = client.get("/api/legal/search", params={"q": q})
        assert r.status_code == 422
        assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert client.get("/api/legal/search").status_code == 422


def test_sql_injection_is_just_text(client):
    body = search(client, "'; DROP TABLE chunks; -- | & ! ( ) :*", locale="ru")
    assert body["results"] == []
    assert search(client, "вернуть товар", locale="ru")["results"]  # таблица на месте


# ---------------------------------------------------------------- dense branch


@pytest.fixture
def dense_client(make_client, seeded_db):
    seed_fake_embeddings(seeded_db)

    def make(vector):
        emb = FakeEmbedder(vector)
        cm = make_client()
        c = cm.__enter__()
        c.app.dependency_overrides[embedder_dep] = lambda: emb
        return cm, c, emb

    made = []

    def factory(vector):
        item = make(vector)
        made.append(item[0])
        return item[1], item[2]

    yield factory
    for cm in made:
        cm.__exit__(None, None, None)


def test_dense_branch_orders_by_vector(dense_client):
    # Запрос на латинице без совпадений в тексте: работает только dense-ветка.
    c, emb = dense_client([0.0, 0.1, 1.0])
    body = search(c, "qwertyuiop", locale="ru")
    assert emb.calls == ["qwertyuiop"]
    got = [(r["article_number"], r["match"]["dense_rank"], r["match"]["sparse_rank"]) for r in body["results"]]
    assert got == [("12", 1, None), ("11", 2, None), ("10", 3, None)]

    c2, _ = dense_client([1.0, 0.0, 0.1])
    got2 = [r["article_number"] for r in search(c2, "qwertyuiop", locale="ru")["results"]]
    assert got2 == ["10", "12", "11"]  # другой вектор: другие ранги


def test_dense_adds_to_sparse_score(client, dense_client):
    base = search(client, "вернуть товар", locale="ru")["results"][0]
    c, _ = dense_client([1.0, 0.0, 0.0])
    boosted = search(c, "вернуть товар", locale="ru")["results"][0]
    assert boosted["article_number"] == "10"
    assert boosted["match"]["dense_rank"] == 1 and boosted["match"]["sparse_rank"] == 1
    assert boosted["score"] > base["score"]


def test_null_embedder_skips_dense(client):
    body = search(client, "qwertyuiop", locale="ru")
    assert body["results"] == []


def test_dense_ignores_vectors_of_other_dimension(dense_client):
    c, _ = dense_client([1.0, 0.0])  # у чанков 3-мерные векторы: совпадений нет, ошибки тоже
    assert search(c, "qwertyuiop", locale="ru")["results"] == []


def test_word_forms_match_without_stemmer(client):
    """Конфиг 'simple' не знает русских окончаний: префиксный поиск находит другие формы слова."""
    body = search(client, "гарантийные недостатки", locale="ru")
    numbers = [r["article_number"] for r in body["results"]]
    assert numbers, "форма «недостатки» должна находить «недостатком» / «недостатка»"
    body = search(client, "экспертизы", locale="ru")
    assert any("экспертиз" in r["snippet"].lower() for r in body["results"])


def test_prefix_stem_rules():
    from app.rag.retrieve import _tsquery, prefix_stem

    assert prefix_stem("недостатком") == "недостат"
    assert prefix_stem("товар") == "това"
    assert prefix_stem("ст") == "ст" and prefix_stem("1834") == "1834"
    assert _tsquery(["недостатком", "15"]) == "'недостат':* | '15'"
    assert _tsquery(["o'g'il"]) == "'o''g''i':*"  # апострофы внутри лексемы экранированы
