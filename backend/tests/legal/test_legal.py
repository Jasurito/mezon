from datetime import date

import pytest

from app.errors import NotFoundError
from app.legal import service
from tests.fixtures.legal_seed import ALL_CITATION_IDS, SCENARIO_CITATION_IDS, seed_test_legal_data

pytestmark = pytest.mark.db

SCENARIO_DATE = date(2026, 3, 1)


@pytest.fixture
def seeded(db_session):
    seed_test_legal_data(db_session)
    return db_session


def test_current_edition_on_date(seeded):
    v = service.get_citation_view(seeded, "TEST_CPRL.art.1", SCENARIO_DATE, "ru")
    assert v.edition.status == "current"
    assert v.edition.effective_from == date(2020, 1, 1)
    assert v.language == "ru" and v.translation_note is None
    assert v.document_title == "Тестовый документ TEST_CPRL"
    assert v.source_url == "https://example.test/TEST_CPRL"
    assert v.last_verified_at == date(2026, 1, 15)


def test_all_scenario_citations_resolve(seeded):
    for loc in ("ru", "uz-Latn"):
        views = service.get_citation_views(seeded, SCENARIO_CITATION_IDS, SCENARIO_DATE, loc)
        assert all(v.edition.status == "current" for v in views)


def test_historical_edition(seeded):
    v = service.get_citation_view(seeded, "TEST_EDGE.art.1", date(2022, 6, 1), "ru")
    assert v.edition.status == "historical"
    assert "старая" in v.text
    cur = service.get_citation_view(seeded, "TEST_EDGE.art.1", SCENARIO_DATE, "ru")
    assert cur.edition.status == "current" and "новая" in cur.text


def test_locale_selection(seeded):
    v = service.get_citation_view(seeded, "TEST_CPRL.art.1", SCENARIO_DATE, "uz-Latn")
    assert v.language == "uz-Latn"
    assert "Test moddasi" in v.text
    assert v.document_title == "Test hujjati TEST_CPRL"
    assert v.translation_note is None


def test_language_fallback(seeded):
    v = service.get_citation_view(seeded, "TEST_CC.art.1", SCENARIO_DATE, "uz-Latn")
    assert v.language == "ru"
    assert v.is_official_text is True
    assert v.edition.status == "current"
    assert v.translation_note and "rus tilida" in v.translation_note
    assert "Тестовая статья" in v.text  # text is not translated


def test_unconfirmed_edition(seeded):
    v = service.get_citation_view(seeded, "TEST_FUTURE.art.1", SCENARIO_DATE, "ru")
    assert v.edition.status == "unconfirmed"
    assert v.edition.effective_from is None and v.edition.effective_to is None
    assert v.is_official_text is None
    assert v.translation_note == (
        "Редакция на 01.03.2026 не подтверждена. Показан текст действующей редакции."
    )


def test_part_citation(seeded):
    v = service.get_citation_view(seeded, "TEST_EDGE.art.2.p2", SCENARIO_DATE, "ru")
    assert v.part == 2
    assert v.text == "Тестовая часть два."
    assert [p.part_number for p in v.parts] == [1, 2]
    whole = service.get_citation_view(seeded, "TEST_EDGE.art.2", SCENARIO_DATE, "ru")
    assert whole.part is None and whole.text == "Тестовая статья 2 целиком."


def test_not_found(seeded):
    with pytest.raises(NotFoundError):
        service.get_citation_view(seeded, "NOPE.art.1", SCENARIO_DATE, "ru")
    with pytest.raises(NotFoundError):
        service.get_citation_view(seeded, "TEST_BROKEN.art.9", SCENARIO_DATE, "ru")


def test_article_view(seeded):
    cv = service.get_citation_view(seeded, "TEST_EDGE.art.1", date(2022, 6, 1), "ru")
    v = service.get_article_view(seeded, cv.article_id, "ru")
    assert v.edition.status == "historical" and "старая" in v.text
    assert v.citation_id == "TEST_EDGE.art.1"
    art2 = service.get_citation_view(seeded, "TEST_EDGE.art.2.p2", SCENARIO_DATE, "ru")
    assert service.get_article_view(seeded, art2.article_id, "ru").citation_id == "TEST_EDGE.art.2"
    with pytest.raises(NotFoundError):
        service.get_article_view(seeded, 10**9, "ru")


def test_missing_citation_ids(seeded):
    assert service.missing_citation_ids(seeded, ALL_CITATION_IDS[:-1]) == set()
    assert service.missing_citation_ids(seeded, []) == set()
    assert service.missing_citation_ids(
        seeded, ["TEST_CPRL.art.1", "NOPE.art.1", "TEST_BROKEN.art.9"]
    ) == {"NOPE.art.1", "TEST_BROKEN.art.9"}


def test_get_legal_acts(seeded):
    acts = service.get_legal_acts(seeded, ["TEST_CPC", "UNKNOWN", "TEST_CPRL"], "uz-Latn")
    assert [a.document_key for a in acts] == ["TEST_CPC", "TEST_CPRL"]
    assert acts[0].title == "Test hujjati TEST_CPC"
    assert acts[0].source_url == "https://example.test/TEST_CPC"


def test_get_citation_views_order_and_dedup(seeded):
    views = service.get_citation_views(
        seeded, ["TEST_CPC.art.2", "TEST_CPRL.art.1", "TEST_CPC.art.2"], SCENARIO_DATE, "ru"
    )
    assert [v.citation_id for v in views] == ["TEST_CPC.art.2", "TEST_CPRL.art.1"]


def test_api_citation(seeded, client):
    r = client.get("/api/legal/citations/TEST_EDGE.art.1", params={"date": "2022-06-01"})
    assert r.status_code == 200
    body = r.json()
    assert body["edition"]["status"] == "historical" and "старая" in body["text"]
    assert client.get("/api/legal/citations/TEST_CC.art.1?locale=uz-Latn").status_code == 200


def test_api_article(seeded, client):
    art_id = client.get("/api/legal/citations/TEST_CPC.art.1?date=2026-03-01").json()["article_id"]
    r = client.get(f"/api/legal/articles/{art_id}")
    assert r.status_code == 200 and r.json()["citation_id"] == "TEST_CPC.art.1"


def test_api_errors(seeded, client):
    r = client.get("/api/legal/citations/NOPE.art.1")
    assert r.status_code == 404
    err = r.json()["error"]
    assert err["code"] == "NOT_FOUND" and err["details"] == {"citation_id": "NOPE.art.1"}
    assert client.get("/api/legal/articles/999999").status_code == 404
    assert client.get("/api/legal/citations/TEST_CC.art.1?locale=xx").status_code == 422
    assert client.get("/api/legal/articles/1?locale=xx").status_code == 422
