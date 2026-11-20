"""Тестовые чанки для поиска. Все тексты вымышленные, это не настоящий закон.

``seed_test_chunks`` вызывается после ``seed_test_legal_data``: добавляет тестовый документ
TEST_RAG (возврат товара, гарантия, экспертиза) и создаёт чанки для всех статей в базе.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.legal import Article, ArticlePart, Chunk, DocumentVersion, LegalDocument
from app.rag.normalize import normalize
from tests.fixtures.legal_seed import D_2020, _article, _cite, _doc, _version

RAG_DOC_KEY = "TEST_RAG"
RAG_CITATION_RETURN = "TEST_RAG.art.10"

# (номер, название, части): тестовые данные, не закон.
_RAG_RU = [
    (
        "10",
        "Возврат товара ненадлежащего качества",
        [
            "Тестовые данные. Покупатель вправе вернуть товар с существенным недостатком.",
            "Продавец обязан вернуть уплаченную за товар денежную сумму.",
        ],
    ),
    (
        "11",
        "Гарантийный срок на товар",
        [
            "Тестовые данные. Гарантийный срок исчисляется со дня передачи товара покупателю.",
            "Недостатки, обнаруженные в течение гарантийного срока, устраняются продавцом.",
        ],
    ),
    (
        "12",
        "Судебная экспертиза",
        ["Тестовые данные. Суд назначает экспертизу, если для установления причины недостатка нужны специальные знания."],
    ),
]


def _add_rag_document(session: Session) -> None:
    doc = _doc(
        session,
        RAG_DOC_KEY,
        {
            "ru": "Тестовый закон о возврате товара",
            "uz-Latn": "Tovarni qaytarish haqida test qonuni",
            "uz-Cyrl": "Товарни қайтариш ҳақида тест қонуни",
        },
        url="https://example.test/TEST_RAG",
    )
    ru = _version(session, doc, "ru", D_2020, source_url="https://example.test/TEST_RAG/ru")
    for number, title, parts in _RAG_RU:
        _article(session, ru, number, " ".join(parts), parts, title)
    lat = _version(session, doc, "uz-Latn", D_2020, source_url="https://example.test/TEST_RAG/uz")
    lat_parts = ["Test ma’lumoti. Xaridor sifatsiz tovarni qaytarishga haqli."]
    _article(session, lat, "10", " ".join(lat_parts), lat_parts, "Sifatsiz tovarni qaytarish")
    cyr = _version(session, doc, "uz-Cyrl", D_2020, source_url="https://example.test/TEST_RAG/uz-cyrl")
    cyr_parts = ["Тест маълумоти. Харидор сифатсиз товарни қайтаришга ҳақли."]
    _article(session, cyr, "10", " ".join(cyr_parts), cyr_parts, "Сифатсиз товарни қайтариш")
    _cite(session, RAG_CITATION_RETURN, doc, "10")
    session.flush()


def _header(doc: LegalDocument, version: DocumentVersion, article: Article, p_from, p_to) -> str:
    title = (doc.title or {}).get(version.language) or (doc.title or {}).get("ru") or doc.document_key
    label = f"{article.article_number}-modda" if version.language != "ru" else f"Статья {article.article_number}"
    parts = "" if p_from is None else (f" · части {p_from}" + (f"–{p_to}" if p_to != p_from else ""))
    return (
        f"[{title} · {label}. {article.article_title or ''}{parts}"
        f" · редакция от {version.effective_from} · {version.language}]"
    )


def seed_test_chunks(session: Session) -> None:
    """Один чанк на статью (формат INGESTION.md §4 шаг 6); embedding = null."""
    _add_rag_document(session)
    rows = session.execute(
        select(Article, DocumentVersion, LegalDocument)
        .join(DocumentVersion, DocumentVersion.id == Article.version_id)
        .join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
        .order_by(Article.id)
    ).all()
    for article, version, doc in rows:
        parts = list(
            session.scalars(
                select(ArticlePart).where(ArticlePart.article_id == article.id).order_by(ArticlePart.part_number)
            )
        )
        body = "\n".join(p.content for p in parts) if parts else article.content
        p_from = parts[0].part_number if parts else None
        p_to = parts[-1].part_number if parts else None
        full = f"{_header(doc, version, article, p_from, p_to)}\n{body}"
        session.add(
            Chunk(
                article_id=article.id,
                part_from=p_from,
                part_to=p_to,
                text=full,
                text_normalized=normalize(full, version.language),
                token_count=len(full.split()),
            )
        )
    session.flush()


FAKE_VECTORS = {"10": [1.0, 0.0, 0.0], "11": [0.0, 1.0, 0.0], "12": [0.0, 0.0, 1.0]}


def seed_fake_embeddings(session: Session) -> None:
    """3-мерные векторы для чанков TEST_RAG (русская версия): статья 10 → x, 11 → y, 12 → z."""
    rows = session.execute(
        select(Chunk, Article.article_number)
        .join(Article, Article.id == Chunk.article_id)
        .join(DocumentVersion, DocumentVersion.id == Article.version_id)
        .join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
        .where(LegalDocument.document_key == RAG_DOC_KEY, DocumentVersion.language == "ru")
    ).all()
    for chunk, number in rows:
        chunk.embedding = FAKE_VECTORS[number]
    session.flush()


class FakeEmbedder:
    """Эмбеддер запроса для тестов: всегда возвращает заданный вектор."""

    def __init__(self, vector: list[float] | None) -> None:
        self.vector = vector
        self.calls: list[str] = []

    def embed_query(self, text: str) -> list[float] | None:
        self.calls.append(text)
        return self.vector
