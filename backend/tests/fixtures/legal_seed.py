"""Test legal corpus. All texts are fictional test data, not real law."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.legal import Article, ArticlePart, Citation, DocumentVersion, LegalDocument

SCENARIO_CITATION_IDS = [
    "TEST_CPRL.art.1",
    "TEST_CPRL.art.2",
    "TEST_CC.art.1",
    "TEST_CPC.art.1",
    "TEST_CPC.art.2",
]
EDGE_CITATION_IDS = [
    "TEST_EDGE.art.1",
    "TEST_EDGE.art.2",
    "TEST_EDGE.art.2.p2",
    "TEST_FUTURE.art.1",
    "TEST_BROKEN.art.9",
]
ALL_CITATION_IDS = SCENARIO_CITATION_IDS + EDGE_CITATION_IDS

D_2020 = date(2020, 1, 1)
D_2024 = date(2024, 1, 1)
D_2025 = date(2025, 1, 1)
D_2027 = date(2027, 1, 1)

_hash = 0


def _doc(session: Session, key: str, titles: dict[str, str], *, url: str | None = None) -> LegalDocument:
    doc = LegalDocument(
        document_key=key,
        document_type="code",
        document_number=f"№ {key}",
        title=titles,
        source_url=url,
        status="active",
    )
    session.add(doc)
    session.flush()
    return doc


def _version(
    session: Session,
    doc: LegalDocument,
    language: str,
    effective_from: date,
    effective_to: date | None = None,
    *,
    official: bool = True,
    status: str = "active",
    source_url: str | None = None,
) -> DocumentVersion:
    global _hash
    _hash += 1
    v = DocumentVersion(
        document_id=doc.id,
        language=language,
        is_official_text=official,
        effective_from=effective_from,
        effective_to=effective_to,
        review_status=status,
        source_url=source_url,
        content_hash=f"test-hash-{_hash}",
        last_verified_at=date(2026, 1, 15),
    )
    session.add(v)
    session.flush()
    return v


def _article(
    session: Session,
    version: DocumentVersion,
    number: str,
    content: str,
    parts: list[str] | None = None,
    title: str | None = None,
) -> Article:
    a = Article(
        version_id=version.id,
        article_number=number,
        article_title=title or f"Тестовая статья {number}",
        chapter="Тестовая глава 1",
        status="active",
        content=content,
    )
    session.add(a)
    session.flush()
    for i, text in enumerate(parts or [], start=1):
        session.add(ArticlePart(article_id=a.id, part_number=i, kind="text", content=text))
    session.flush()
    return a


def _cite(session: Session, cid: str, doc: LegalDocument, number: str, part: int | None = None) -> None:
    session.add(Citation(citation_id=cid, document_id=doc.id, article_number=number, part=part))


def seed_test_legal_data(session: Session) -> None:
    # Scenario documents: current on 2026-03-01.
    for key, langs in (("TEST_CPRL", ("ru", "uz-Latn")), ("TEST_CC", ("ru",)), ("TEST_CPC", ("ru", "uz-Latn"))):
        doc = _doc(
            session,
            key,
            {"ru": f"Тестовый документ {key}", "uz-Latn": f"Test hujjati {key}"},
            url=f"https://example.test/{key}",
        )
        numbers = ["1", "2"] if key != "TEST_CC" else ["1"]
        for lang in langs:
            v = _version(session, doc, lang, D_2020)
            for n in numbers:
                prefix = "Тестовая статья" if lang == "ru" else "Test moddasi"
                _article(session, v, n, f"{prefix} {key} {n} ({lang}).", [f"{prefix} {key} {n}, часть 1 ({lang})."])
        for n in numbers:
            _cite(session, f"{key}.art.{n}", doc, n)

    # TEST_EDGE: historical + current edition, an article with two parts.
    edge = _doc(session, "TEST_EDGE", {"ru": "Тестовый краевой документ"})
    old = _version(session, edge, "ru", D_2020, D_2024)
    new = _version(session, edge, "ru", D_2024)
    _article(session, old, "1", "Тестовая статья 1, старая редакция.")
    _article(session, new, "1", "Тестовая статья 1, новая редакция.")
    _article(session, new, "2", "Тестовая статья 2 целиком.", ["Тестовая часть один.", "Тестовая часть два."])
    _cite(session, "TEST_EDGE.art.1", edge, "1")
    _cite(session, "TEST_EDGE.art.2", edge, "2")
    _cite(session, "TEST_EDGE.art.2.p2", edge, "2", part=2)

    # TEST_FUTURE: the only active edition starts after the scenario date.
    future = _doc(session, "TEST_FUTURE", {"ru": "Тестовый будущий документ"})
    fv = _version(session, future, "ru", D_2027)
    _article(session, fv, "1", "Тестовая статья будущей редакции.")
    _cite(session, "TEST_FUTURE.art.1", future, "1")

    # TEST_BROKEN: citation without an article in any version.
    broken = _doc(session, "TEST_BROKEN", {"ru": "Тестовый документ без статьи"})
    bv = _version(session, broken, "ru", D_2020)
    _article(session, bv, "1", "Тестовая статья 1.")
    _cite(session, "TEST_BROKEN.art.9", broken, "9")

    session.flush()
