"""Ветки поиска: точная (явные ссылки), sparse (FTS + триграммы по названию), dense (pgvector).

Каждая ветка возвращает упорядоченный список chunk_id (лучшие первыми). Все ветки делят
один фильтр: активные версии на дату, язык запроса или официальный текст, whitelist документов.
Пользовательский текст попадает в SQL только через bind-параметры.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from sqlalchemy import Text, bindparam, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Session

from app.rag.refs import ArticleRef, matches_document

_FROM = """
FROM chunks c
JOIN articles a ON a.id = c.article_id
JOIN document_versions v ON v.id = a.version_id
JOIN legal_documents d ON d.id = v.document_id
"""

# Версия подтверждена, действует на дату; язык запроса, а если для документа его нет, то официальный текст.
_VERSION_FILTER = """
WHERE v.review_status = 'active'
  AND v.effective_from <= :on_date
  AND (v.effective_to IS NULL OR :on_date < v.effective_to)
  AND (
    v.language = :locale
    OR (
      v.is_official_text IS TRUE
      AND NOT EXISTS (
        SELECT 1 FROM document_versions v2
        WHERE v2.document_id = v.document_id
          AND v2.language = :locale
          AND v2.review_status = 'active'
          AND v2.effective_from <= :on_date
          AND (v2.effective_to IS NULL OR :on_date < v2.effective_to)
      )
    )
  )
"""
_DOC_FILTER = " AND d.document_key = ANY(:doc_keys)"


@dataclass(frozen=True)
class Scope:
    on_date: date
    locale: str
    document_keys: tuple[str, ...] | None = None


def _where(scope: Scope, *, whitelist: bool = True) -> str:
    return _VERSION_FILTER + (_DOC_FILTER if whitelist and scope.document_keys else "")


def _run(db: Session, sql: str, scope: Scope, params: dict | None = None, *, whitelist: bool = True):
    stmt = text(sql)
    p = {"on_date": scope.on_date, "locale": scope.locale, **(params or {})}
    if whitelist and scope.document_keys:
        stmt = stmt.bindparams(bindparam("doc_keys", type_=ARRAY(Text)))
        p["doc_keys"] = list(scope.document_keys)
    return db.execute(stmt, p)


def prefix_stem(token: str) -> str:
    """Грубый стемминг для конфига 'simple' (нет ни русского, ни узбекского стеммера).

    Отрезаем окончание, остаток ищем как префикс: «недостатком» → «недостат:*» найдёт
    и «недостаток», и «недостатки». Короткие слова и числа (номера статей) — без изменений.
    """
    n = len(token)
    if token.isdigit() or n <= 4:
        return token
    return token[: n - 3] if n >= 7 else token[: n - 1]


def _tsquery(tokens: Sequence[str]) -> str:
    """'t1':* | 't2' ...; кавычки и обратная косая экранированы, значение уходит bind-параметром."""
    parts = []
    for t in tokens:
        stem = prefix_stem(t)
        lexeme = "'" + stem.replace("\\", "\\\\").replace("'", "''") + "'"
        parts.append(lexeme + (":*" if stem != t else ""))
    return " | ".join(parts)


def sparse_fts(db: Session, scope: Scope, tokens: Sequence[str], limit: int) -> list[int]:
    """to_tsquery('simple', 't1:* | t2 ...') по chunks.tsv, ранжирование ts_rank_cd."""
    if not tokens:
        return []
    quoted = _tsquery(tokens)
    sql = (
        "SELECT c.id AS chunk_id, ts_rank_cd(c.tsv, q.query) AS rank "
        + _FROM
        + ", (SELECT to_tsquery('simple', :tsq) AS query) q "
        + _where(scope)
        + " AND c.tsv @@ q.query ORDER BY rank DESC, c.id LIMIT :limit"
    )
    rows = _run(db, sql, scope, {"tsq": quoted, "limit": limit})
    return [r.chunk_id for r in rows]


def sparse_titles(
    db: Session, scope: Scope, query: str, limit: int, min_similarity: float
) -> list[int]:
    """pg_trgm: похожесть запроса на название статьи; по одному (первому) чанку на статью."""
    if not query.strip():
        return []
    sql = (
        "SELECT chunk_id FROM ("
        " SELECT DISTINCT ON (a.id) c.id AS chunk_id, word_similarity(:q, a.article_title) AS sim "
        + _FROM
        + _where(scope)
        + " AND a.article_title IS NOT NULL AND word_similarity(:q, a.article_title) > :min_sim"
        + " ORDER BY a.id, c.part_from NULLS FIRST, c.id"
        ") t ORDER BY sim DESC, chunk_id LIMIT :limit"
    )
    rows = _run(db, sql, scope, {"q": query, "min_sim": min_similarity, "limit": limit})
    return [r.chunk_id for r in rows]


def dense(db: Session, scope: Scope, vector: Sequence[float], limit: int) -> list[int]:
    """Косинусная близость pgvector по чанкам с непустым embedding той же размерности."""
    if not vector:
        return []
    literal = "[" + ",".join(repr(float(x)) for x in vector) + "]"
    sql = (
        "SELECT c.id AS chunk_id "
        + _FROM
        + _where(scope)
        + " AND c.embedding IS NOT NULL AND vector_dims(c.embedding) = :dim"
        + " ORDER BY c.embedding <=> CAST(:q AS vector), c.id LIMIT :limit"
    )
    rows = _run(db, sql, scope, {"q": literal, "dim": len(vector), "limit": limit})
    return [r.chunk_id for r in rows]


def exact(db: Session, scope: Scope, refs: Sequence[ArticleRef]) -> list[int]:
    """Явные ссылки → первый чанк каждой найденной статьи (в порядке ссылок).

    Если ссылка указывает документ («ст. 15 ГК»), а такого документа нет в корпусе,
    статьи с тем же номером из других документов не подставляются.
    """
    if not refs:
        return []
    numbers = sorted({n for r in refs for n in (r.number, r.number.replace("-", "–"))})
    sql = (
        "SELECT c.id AS chunk_id, a.id AS article_id, a.article_number, d.document_key, d.title "
        + _FROM
        + _where(scope)
        + " AND a.article_number = ANY(:nums)"
        + " ORDER BY d.document_key, a.id, c.part_from NULLS FIRST, c.id"
    )
    stmt = text(sql).bindparams(bindparam("nums", type_=ARRAY(Text)))
    if scope.document_keys:
        stmt = stmt.bindparams(bindparam("doc_keys", type_=ARRAY(Text)))
    params = {"on_date": scope.on_date, "locale": scope.locale, "nums": numbers}
    if scope.document_keys:
        params["doc_keys"] = list(scope.document_keys)
    rows = db.execute(stmt, params).all()
    first_per_article: dict[int, object] = {}
    for r in rows:
        first_per_article.setdefault(r.article_id, r)

    out: list[int] = []
    for ref in refs:
        for r in first_per_article.values():
            if r.article_number.replace("–", "-") != ref.number:
                continue
            if ref.hint is not None and not matches_document(
                ref.hint, r.document_key, [v for v in (r.title or {}).values() if v]
            ):
                continue
            if r.chunk_id not in out:
                out.append(r.chunk_id)
    return out


def scenario_chunks(db: Session, scope: Scope, citation_ids: Sequence[str]) -> list[int]:
    """Чанки статей, на которые ссылается сценарий (в порядке citation_ids)."""
    if not citation_ids:
        return []
    sql = (
        "SELECT ci.citation_id, ci.part, c.id AS chunk_id, c.part_from, c.part_to "
        "FROM citations ci "
        "JOIN legal_documents d ON d.id = ci.document_id "
        "JOIN document_versions v ON v.document_id = d.id "
        "JOIN articles a ON a.version_id = v.id AND a.article_number = ci.article_number "
        "JOIN chunks c ON c.article_id = a.id "
        + _where(scope, whitelist=False)
        + " AND ci.citation_id = ANY(:cids) ORDER BY c.part_from NULLS FIRST, c.id"
    )
    stmt = text(sql).bindparams(bindparam("cids", type_=ARRAY(Text)))
    rows = db.execute(
        stmt, {"on_date": scope.on_date, "locale": scope.locale, "cids": list(citation_ids)}
    ).all()
    by_cid: dict[str, list] = {}
    for r in rows:
        by_cid.setdefault(r.citation_id, []).append(r)
    out: list[int] = []
    for cid in citation_ids:
        cand = by_cid.get(cid)
        if not cand:
            continue
        pick = cand[0]
        part = cand[0].part
        if part is not None:
            pick = next(
                (r for r in cand if r.part_from is not None and r.part_from <= part <= (r.part_to or r.part_from)),
                cand[0],
            )
        if pick.chunk_id not in out:
            out.append(pick.chunk_id)
    return out
