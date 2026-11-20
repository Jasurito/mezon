"""Гибридный поиск: точная ветка + sparse + dense → RRF → дедупликация по статье → порог."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import Settings
from app.rag import retrieve
from app.rag.embedder import Embedder, NullEmbedder
from app.rag.fusion import rrf, rrf_score
from app.rag.normalize import normalize, tokenize
from app.rag.refs import extract_refs
from app.rag.stopwords import content_tokens


@dataclass
class Candidate:
    chunk_id: int
    article_id: int
    score: float
    exact: bool = False
    dense_rank: int | None = None
    sparse_rank: int | None = None
    scenario: bool = False  # добавлен как кандидат сценария, органического совпадения нет


@dataclass
class SearchOutcome:
    candidates: list[Candidate]  # по статьям, лучшие первыми
    best_score: float
    sufficient: bool  # есть кандидаты и лучший балл не ниже RAG_MIN_SCORE


def _ranks(ids: Sequence[int]) -> dict[int, int]:
    return {cid: i for i, cid in enumerate(ids, start=1)}


def hybrid_search(
    db: Session,
    *,
    query: str,
    locale: str,
    on_date: date,
    settings: Settings,
    embedder: Embedder | None = None,
    document_keys: Sequence[str] | None = None,
    scenario_citation_ids: Sequence[str] = (),
) -> SearchOutcome:
    scope = retrieve.Scope(on_date, locale, tuple(document_keys) if document_keys else None)
    top_k = settings.RAG_TOP_K
    k = settings.RAG_RRF_K

    normalized = normalize(query, locale)
    tokens = content_tokens(tokenize(normalized), locale)
    refs = extract_refs(query)

    exact_ids = retrieve.exact(db, scope, refs)
    fts_ids = retrieve.sparse_fts(db, scope, tokens, top_k)
    title_ids = retrieve.sparse_titles(db, scope, " ".join(tokens), top_k, settings.RAG_TITLE_SIMILARITY)
    # Вклад триграмм по названию входит в sparse-ранг: две подветки сливаются через RRF.
    merged = rrf([fts_ids, title_ids], k)
    sparse_ids = [cid for cid, _ in sorted(merged.items(), key=lambda kv: (-kv[1], kv[0]))][:top_k]

    dense_ids: list[int] = []
    vector = (embedder or NullEmbedder()).embed_query(query)
    if vector:
        dense_ids = retrieve.dense(db, scope, vector, top_k)

    scores = rrf([exact_ids, sparse_ids, dense_ids], k)
    exact_set = set(exact_ids)
    sparse_rank = _ranks(sparse_ids)
    dense_rank = _ranks(dense_ids)

    # Статьи сценария всегда среди кандидатов, но с баллом ранга top_k+1: реальные совпадения их не уступают.
    fallback = rrf_score(top_k + 1, k)
    scenario_only: set[int] = set()
    for cid in retrieve.scenario_chunks(db, scope, scenario_citation_ids):
        if cid not in scores:
            scores[cid] = fallback
            scenario_only.add(cid)

    if not scores:
        return SearchOutcome([], 0.0, False)

    article_of = dict(
        db.execute(
            text("SELECT id, article_id FROM chunks WHERE id = ANY(:ids)"), {"ids": list(scores)}
        ).all()
    )
    order: dict[int, int] = {}
    for cid in [*exact_ids, *sparse_ids, *dense_ids, *scores]:
        order.setdefault(cid, len(order))
    best: dict[int, Candidate] = {}
    for cid, score in scores.items():
        art = article_of.get(cid)
        if art is None:
            continue
        cand = Candidate(
            chunk_id=cid,
            article_id=art,
            score=score,
            exact=cid in exact_set,
            dense_rank=dense_rank.get(cid),
            sparse_rank=sparse_rank.get(cid),
            scenario=cid in scenario_only,
        )
        cur = best.get(art)
        if cur is None or (cand.exact, cand.score, -order[cid]) > (cur.exact, cur.score, -order[cur.chunk_id]):
            # Чанки одной статьи: если у какого-то есть точное совпадение, ранги берём у лучшего.
            best[art] = cand
    ordered = sorted(
        best.values(), key=lambda c: (not c.exact, -c.score, order[c.chunk_id])
    )
    top = ordered[0].score if ordered else 0.0
    return SearchOutcome(ordered, top, bool(ordered) and top >= settings.RAG_MIN_SCORE)
