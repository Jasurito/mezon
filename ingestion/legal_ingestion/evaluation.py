"""eval: Recall@K по eval/gold.jsonl для sparse / dense / hybrid через пайплайн бэкенда (app.rag)."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models.legal import Article, Chunk, Citation, DocumentVersion, LegalDocument
from app.rag import retrieve
from app.rag.embedder import Embedder, NullEmbedder
from app.rag.pipeline import hybrid_search
from legal_ingestion.errors import IngestionError
from legal_ingestion.io import write_text_if_changed
from legal_ingestion.load import SessionFactory
from legal_ingestion.paths import Paths

MODES = ("sparse", "dense", "hybrid")
Key = tuple[str, str]  # (document_key, article_number)


def load_gold(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise IngestionError(
            f"eval: файл {path} не найден. Нужен набор вопросов eval/gold.jsonl "
            '(строка: {"id", "lang", "question", "expected_citations", "type"}), см. docs/INGESTION.md §7'
        )
    items = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except ValueError as exc:
            raise IngestionError(f"eval: {path}:{n}: некорректный JSON ({exc})") from exc
    return items


def _article_keys(db: Session, article_ids: list[int]) -> dict[int, Key]:
    rows = db.execute(
        select(Article.id, LegalDocument.document_key, Article.article_number)
        .join(DocumentVersion, DocumentVersion.id == Article.version_id)
        .join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
        .where(Article.id.in_(article_ids or [0]))
    ).all()
    return {r[0]: (r[1], r[2]) for r in rows}


def _chunk_keys(db: Session, chunk_ids: list[int]) -> dict[int, Key]:
    rows = db.execute(
        select(Chunk.id, LegalDocument.document_key, Article.article_number)
        .join(Article, Article.id == Chunk.article_id)
        .join(DocumentVersion, DocumentVersion.id == Article.version_id)
        .join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
        .where(Chunk.id.in_(chunk_ids or [0]))
    ).all()
    return {r[0]: (r[1], r[2]) for r in rows}


def _dedupe(keys: list[Key]) -> list[Key]:
    return list(dict.fromkeys(keys))


def rank_all(
    db: Session, question: str, locale: str, on_date: date, settings: Settings, embedder: Embedder
) -> dict[str, list[Key] | None]:
    """Упорядоченные (документ, статья) для каждого режима; None = режим недоступен (нет эмбеддера)."""
    out: dict[str, list[Key] | None] = {}
    sparse = hybrid_search(db, query=question, locale=locale, on_date=on_date, settings=settings, embedder=NullEmbedder())
    keys = _article_keys(db, [c.article_id for c in sparse.candidates])
    out["sparse"] = _dedupe([keys[c.article_id] for c in sparse.candidates if c.article_id in keys])

    vector = embedder.embed_query(question)
    if not vector or isinstance(embedder, NullEmbedder):
        out["dense"] = out["hybrid"] = None
        return out
    ids = retrieve.dense(db, retrieve.Scope(on_date, locale), vector, 50)
    ck = _chunk_keys(db, ids)
    out["dense"] = _dedupe([ck[i] for i in ids if i in ck])
    hyb = hybrid_search(db, query=question, locale=locale, on_date=on_date, settings=settings, embedder=embedder)
    keys = _article_keys(db, [c.article_id for c in hyb.candidates])
    out["hybrid"] = _dedupe([keys[c.article_id] for c in hyb.candidates if c.article_id in keys])
    return out


def run_eval(
    session_factory: SessionFactory,
    paths: Paths,
    settings: Settings,
    embedder: Embedder,
    *,
    k: int = 5,
    on_date: date | None = None,
    write: bool = True,
) -> str:
    items = load_gold(paths.gold_file)
    on_date = on_date or date.today()
    ks = sorted({k, 10})
    session = session_factory()
    try:
        # (lang, mode, K) -> [recall по вопросам]
        scores: dict[tuple[str, str, int], list[float]] = defaultdict(list)
        unresolved: list[str] = []
        skipped = 0
        for item in items:
            expected = item.get("expected_citations") or []
            if not expected:
                skipped += 1  # out_of_scope: Recall не определён
                continue
            want: set[Key] = set()
            for cid in expected:
                row = session.execute(
                    select(LegalDocument.document_key, Citation.article_number)
                    .join(LegalDocument, LegalDocument.id == Citation.document_id)
                    .where(Citation.citation_id == cid)
                ).first()
                if row is None:
                    unresolved.append(f"{item.get('id')}: {cid}")
                else:
                    want.add((row[0], row[1]))
            if not want:
                continue
            lang = item.get("lang", "ru")
            ranked = rank_all(session, item["question"], lang, on_date, settings, embedder)
            for mode in MODES:
                r = ranked[mode]
                if r is None:
                    continue
                for kk in ks:
                    scores[(lang, mode, kk)].append(len(want & set(r[:kk])) / len(want))
    finally:
        session.close()

    langs = sorted({lang for lang, _, _ in scores} | {i.get("lang", "ru") for i in items})
    lines = ["# Eval: Recall@K", "", f"Вопросов: {len(items)} (без ожидаемых ссылок, в том числе out_of_scope: {skipped}).", ""]
    header = "| язык | режим | " + " | ".join(f"Recall@{kk}" for kk in ks) + " | вопросов |"
    lines += [header, "|" + "---|" * (len(ks) + 3)]
    for lang in langs:
        for mode in MODES:
            n = len(scores.get((lang, mode, ks[0]), []))
            if n == 0:
                cells = ["n/a"] * len(ks)
            else:
                cells = [f"{sum(scores[(lang, mode, kk)]) / n:.3f}" for kk in ks]
            lines.append(f"| {lang} | {mode} | " + " | ".join(cells) + f" | {n} |")
    if unresolved:
        lines += ["", "Ожидаемые citation_id не найдены в базе (вопрос не учтён):", *[f"- {u}" for u in unresolved]]
    lines.append("")
    text = "\n".join(lines)
    if write:
        write_text_if_changed(paths.processed_dir / "eval_report.md", text)
    return text
