"""Оркестрация шагов: validate → parse → normalize → segment → version → chunk → embed → load → link → check."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from legal_ingestion import chunk as chunking
from legal_ingestion import embed as embedding
from legal_ingestion import load as loading
from legal_ingestion import version as ver
from legal_ingestion.check import CheckResult, run_check
from legal_ingestion.errors import IngestionError
from legal_ingestion.io import write_jsonl, write_text_if_changed
from legal_ingestion.link import LinkError, link_citations, load_citations
from legal_ingestion.normalize import normalize_blocks
from legal_ingestion.parse import parse_file
from legal_ingestion.paths import Paths
from legal_ingestion.segment import segment
from legal_ingestion.sources import SourceDocument, SourcesFile, SourceVersion, load_sources, stem_of

log = logging.getLogger("legal_ingestion")


@dataclass
class EditionOutcome:
    stem: str
    action: str  # loaded | unchanged | updated | failed
    version_id: int | None = None
    review_status: str | None = None
    articles: int = 0
    chunks: int = 0
    error: str | None = None


@dataclass
class RunResult:
    editions: list[EditionOutcome] = field(default_factory=list)
    citations: int = 0
    link_errors: list[str] = field(default_factory=list)
    check: CheckResult | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            not self.errors
            and not self.link_errors
            and all(e.action != "failed" for e in self.editions)
            and (self.check is None or not self.check.errors)
        )


def validate(paths: Paths) -> SourcesFile:
    sources, errors = load_sources(paths.sources_file, paths.legal_dir)
    if sources is None:
        raise IngestionError("sources.yaml не прошёл проверку:\n  " + "\n  ".join(errors))
    return sources


def select_documents(sources: SourcesFile, doc: str | None) -> list[SourceDocument]:
    docs = [d for d in sources.documents if doc is None or d.document_key == doc]
    if doc is not None and not docs:
        known = ", ".join(d.document_key for d in sources.documents) or "нет документов"
        raise IngestionError(f"документ {doc} не найден в sources.yaml (есть: {known})")
    return docs


def parse_edition(paths: Paths, doc: SourceDocument, v: SourceVersion) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Шаги 2–3: (сырые блоки, очищенные блоки); оба пишутся в processed/."""
    stem = stem_of(doc, v)
    blocks = parse_file(paths.legal_dir / v.file, v.language)
    write_jsonl(paths.processed_dir / f"{stem}.blocks.jsonl", blocks)
    cleaned = normalize_blocks(blocks)
    write_jsonl(paths.processed_dir / f"{stem}.norm.jsonl", cleaned)
    return blocks, cleaned


def segment_edition(
    paths: Paths, doc: SourceDocument, v: SourceVersion, cleaned: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Шаг 4. Ошибки сегментации (например, дубли номеров) = IngestionError."""
    articles, issues = segment(cleaned, v.language, doc.document_key)
    write_jsonl(paths.processed_dir / f"{stem_of(doc, v)}.articles.jsonl", articles)
    if issues:
        raise IngestionError(f"{stem_of(doc, v)}: " + "; ".join(issues))
    return articles


def chunk_edition(
    paths: Paths, doc: SourceDocument, v: SourceVersion, articles: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Шаг 6."""
    chunks = chunking.build_chunks(
        articles,
        doc_title=chunking.doc_title_for(dict(doc.title), v.language, doc.document_key),
        language=v.language,
        effective_from=v.effective_from,
    )
    write_jsonl(paths.processed_dir / f"{stem_of(doc, v)}.chunks.jsonl", chunks)
    return chunks


def prepare_edition(paths: Paths, doc: SourceDocument, v: SourceVersion) -> loading.Edition:
    """Шаги 2–5 без БД: parse, normalize, segment, хэш."""
    _, cleaned = parse_edition(paths, doc, v)
    articles = segment_edition(paths, doc, v, cleaned)
    chash = ver.content_hash(articles, v.language)
    write_text_if_changed(paths.processed_dir / f"{stem_of(doc, v)}.version.json", f'{{"content_hash": "{chash}"}}\n')
    return loading.Edition(doc=doc, version=v, stem=stem_of(doc, v), articles=articles, content_hash=chash)


def run(
    paths: Paths,
    session_factory: loading.SessionFactory,
    embedder: Any = None,
    *,
    doc: str | None = None,
    reembed: bool = False,
    do_check: bool = True,
    draft_activate: bool = False,
) -> RunResult:
    """Шаги 1–10. Падение одной редакции не мешает остальным; итог ok=False, если были ошибки.

    draft_activate: загрузить редакции как active даже без verified_by; только база *_demo.
    """
    if draft_activate:
        loading.assert_demo_database(session_factory)
    result = RunResult()
    sources = validate(paths)
    docs = select_documents(sources, doc)
    use_embedder = embedding.can_embed(embedder)

    todo = [(d, v) for d in docs for v in sorted(d.versions, key=lambda x: (x.language, x.effective_from))]
    for d, v in todo:
        stem = stem_of(d, v)
        try:
            ed = prepare_edition(paths, d, v)
            with session_factory() as s:
                existing = loading.lookup_existing(s, d.document_key, v.language, ed.content_hash)
            needs_vectors = existing is None or (use_embedder and (reembed or existing[1] > 0))
            if needs_vectors:
                ed.chunks = chunk_edition(paths, d, v, ed.articles)
                vectors = embedding.embed_texts(
                    [c["text"] for c in ed.chunks], embedder, paths.cache_dir, reembed=reembed
                )
                for c, vec in zip(ed.chunks, vectors):
                    c["embedding"] = vec
            res = loading.load_edition(session_factory, ed, reembed=reembed, draft_activate=draft_activate)
            result.editions.append(
                EditionOutcome(stem, res.action, res.version_id, res.review_status, res.articles, res.chunks)
            )
            log.info("%s: %s (version id=%s, %s)", stem, res.action, res.version_id, res.review_status)
        except IngestionError as exc:
            log.error("%s: %s", stem, exc)
            result.editions.append(EditionOutcome(stem, "failed", error=str(exc)))

    if paths.citations_file.is_file():
        entries, errs = load_citations(paths.citations_file)
        if errs:
            result.link_errors.extend(errs)
        else:
            try:
                result.citations = link_citations(session_factory, entries)
            except LinkError as exc:
                result.link_errors.extend(exc.errors)
    else:
        log.info("link: %s не найден, шаг пропущен", paths.citations_file)

    if do_check:
        result.check = run_check(session_factory, paths, sources)
    return result
