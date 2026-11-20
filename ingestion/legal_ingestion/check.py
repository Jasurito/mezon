"""Шаг 10. check: проверки целостности и отчёт processed/check_report.md (docs/INGESTION.md §4 шаг 10)."""

from __future__ import annotations

import json
import random
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.legal.service import missing_citation_ids
from app.models.legal import Article, ArticlePart, Chunk, Citation, DocumentVersion, LegalDocument
from legal_ingestion.io import read_jsonl, write_text_if_changed
from legal_ingestion.link import load_citations
from legal_ingestion.load import SessionFactory
from legal_ingestion.paths import Paths
from legal_ingestion.patterns import PREAMBLE
from legal_ingestion.sources import SourcesFile

SAMPLE_SIZE = 10
COUNT_CHANGE_RATIO = 0.2
_LEADING_INT = re.compile(r"^(\d+)")


@dataclass
class Issue:
    level: str  # error | warning
    message: str


@dataclass
class CheckResult:
    issues: list[Issue] = field(default_factory=list)
    samples: list[dict[str, Any]] = field(default_factory=list)
    report: str = ""

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    def error(self, msg: str) -> None:
        self.issues.append(Issue("error", msg))

    def warn(self, msg: str) -> None:
        self.issues.append(Issue("warning", msg))


def find_gaps(numbers: list[str]) -> tuple[list[int], list[str]]:
    """Пропущенные целые номера и нарушения порядка. Вставные 25¹ / 25-1 относятся к базе 25."""
    bases: list[int] = []
    for n in numbers:
        m = _LEADING_INT.match(n)
        if m and n != PREAMBLE:
            b = int(m.group(1))
            if not bases or bases[-1] != b:
                bases.append(b)
    missing: list[int] = []
    order: list[str] = []
    for prev, nxt in zip(bases, bases[1:]):
        if nxt > prev + 1:
            missing.extend(range(prev + 1, nxt))
        elif nxt < prev:
            order.append(f"номер {nxt} после {prev}")
    return missing, order


def scenario_citation_ids(scenarios_dir: Path) -> dict[str, set[str]]:
    """{scenario.json: citation_id}: объявленные `citations` плюс все упоминания в сценарии."""
    out: dict[str, set[str]] = {}
    if not scenarios_dir.is_dir():
        return out
    for path in sorted(scenarios_dir.rglob("scenario.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        ids: set[str] = set()
        if isinstance(data, dict) and isinstance(data.get("citations"), list):
            ids.update(x for x in data["citations"] if isinstance(x, str))
        ids.update(_mentioned(data, root=True))
        out[str(path.relative_to(scenarios_dir))] = ids
    return out


def _mentioned(data: Any, root: bool = False) -> Iterator[str]:
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "citation_id" and isinstance(v, str):
                yield v
            elif k.endswith("citation_ids") and isinstance(v, list):
                yield from (x for x in v if isinstance(x, str))
            elif k != "citations":
                yield from _mentioned(v)
    elif isinstance(data, list):
        for item in data:
            yield from _mentioned(item)


def _label(key: str, v: DocumentVersion) -> str:
    return f"{key} {v.language} {v.effective_from} (version id={v.id})"


def run_check(
    session_factory: SessionFactory,
    paths: Paths,
    sources: SourcesFile | None,
    source_errors: list[str] | None = None,
    *,
    write: bool = True,
) -> CheckResult:
    res = CheckResult()
    for e in source_errors or []:
        res.error(f"sources.yaml: {e}")
    if sources is not None:
        for d in sources.documents:
            for v in d.versions:
                if v.is_official_text is None:
                    res.warn(f"sources.yaml: {d.document_key} {v.language} {v.effective_from}: is_official_text не проверен (null)")

    known = {d.document_key: {lang: set(g) for lang, g in d.known_gaps.items()} for d in sources.documents} if sources else {}
    session = session_factory()
    try:
        _check_db(session, res, paths, sources, known)
    finally:
        session.close()
    res.report = render_report(res)
    if write:
        write_text_if_changed(paths.processed_dir / "check_report.md", res.report)
    return res


def _check_db(session: Session, res: CheckResult, paths: Paths, sources: SourcesFile | None, known: dict) -> None:
    q = select(DocumentVersion, LegalDocument.document_key).join(LegalDocument, LegalDocument.id == DocumentVersion.document_id)
    if sources is not None:
        q = q.where(LegalDocument.document_key.in_(list(known) or [""]))
    versions = session.execute(q.order_by(LegalDocument.document_key, DocumentVersion.language, DocumentVersion.effective_from, DocumentVersion.id)).all()
    if not versions:
        res.warn("в базе нет загруженных редакций")

    latest_counts: dict[str, int] = {}
    sample_pool: list[tuple[int, int, str]] = []
    for v, key in versions:
        label = _label(key, v)
        if v.review_status == "active":
            if not (v.verified_by and v.verified_by.strip()):
                res.error(f"{label}: активная редакция без verified_by")
            if not v.source_url:
                res.error(f"{label}: нет source_url")
            if v.retrieved_at is None:
                res.error(f"{label}: нет retrieved_at")
        if not v.source_url and v.review_status != "active":
            res.error(f"{label}: нет source_url")
        if v.is_official_text is None:
            res.warn(f"{label}: is_official_text не проверен (null)")

        arts = list(session.scalars(select(Article).where(Article.version_id == v.id).order_by(Article.id)))
        numbers = [a.article_number for a in arts]
        seen: set[str] = set()
        for n in numbers:
            if n in seen:
                res.error(f"{label}: повторяющийся номер статьи {n}")
            seen.add(n)
        missing, order = find_gaps(numbers)
        allowed = known.get(key, {}).get(v.language, set())
        unexplained = [n for n in missing if str(n) not in allowed]
        if unexplained:
            res.error(f"{label}: пропущены номера статей {', '.join(map(str, unexplained))} (если так и задумано, добавьте в known_gaps)")
        for o in order:
            res.error(f"{label}: нарушен порядок статей, {o}")

        chunk_counts = dict(
            session.execute(
                select(Chunk.article_id, func.count()).where(Chunk.article_id.in_([a.id for a in arts] or [0])).group_by(Chunk.article_id)
            ).all()
        )
        part_max = dict(
            session.execute(
                select(ArticlePart.article_id, func.max(ArticlePart.part_number)).where(
                    ArticlePart.article_id.in_([a.id for a in arts] or [0])
                ).group_by(ArticlePart.article_id)
            ).all()
        )
        for a in arts:
            if not (a.content or "").strip():
                res.error(f"{label}: пустая статья {a.article_number}")
                continue
            if chunk_counts.get(a.id, 0) == 0:
                res.error(f"{label}: у статьи {a.article_number} нет чанков (цепочка chunk → article разорвана)")
            if a.article_number != PREAMBLE:
                sample_pool.append((v.id, a.id, key))
        for c, num in session.execute(
            select(Chunk, Article.article_number).join(Article, Article.id == Chunk.article_id).where(Article.version_id == v.id)
        ):
            if not (c.text or "").strip():
                res.error(f"{label}: пустой чанк id={c.id} (статья {num})")
            elif c.part_from is not None and c.article_id in part_max and (c.part_to or c.part_from) > part_max[c.article_id]:
                res.error(f"{label}: чанк id={c.id} ссылается на несуществующую часть статьи {num}")

        latest_counts[f"{key}|{v.language}"] = len(arts)  # версии отсортированы по дате: останется последняя

    orphan_chunks = session.scalar(
        select(func.count()).select_from(Chunk).outerjoin(Article, Article.id == Chunk.article_id).where(Article.id.is_(None))
    )
    if orphan_chunks:
        res.error(f"{orphan_chunks} чанков без статьи")
    orphan_articles = session.scalar(
        select(func.count()).select_from(Article).outerjoin(DocumentVersion, DocumentVersion.id == Article.version_id).where(DocumentVersion.id.is_(None))
    )
    if orphan_articles:
        res.error(f"{orphan_articles} статей без редакции")

    _check_counts(res, paths, latest_counts)
    _check_citations(session, res, paths)

    rng = random.Random(20260101)
    for vid, aid, key in rng.sample(sorted(sample_pool), min(SAMPLE_SIZE, len(sample_pool))):
        res.samples.append(_sample(session, paths, vid, aid, key))


def _check_counts(res: CheckResult, paths: Paths, counts: dict[str, int]) -> None:
    state = paths.processed_dir / "article_counts.json"
    prev: dict[str, int] = {}
    if state.is_file():
        try:
            prev = json.loads(state.read_text(encoding="utf-8"))
        except ValueError:
            prev = {}
    for k, n in counts.items():
        old = prev.get(k)
        if old and abs(n - old) >= 2 and abs(n - old) / old > COUNT_CHANGE_RATIO:
            res.warn(f"{k}: число статей изменилось с {old} до {n} по сравнению с прошлым запуском")
    merged = {**prev, **counts}
    write_text_if_changed(state, json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def _check_citations(session: Session, res: CheckResult, paths: Paths) -> None:
    yaml_ids: set[str] = set()
    if paths.citations_file.is_file():
        entries, errs = load_citations(paths.citations_file)
        for e in errs:
            res.error(f"citations.yaml: {e}")
        yaml_ids = {e.citation_id for e in entries}
        for cid in sorted(missing_citation_ids(session, yaml_ids)):
            res.error(f"citations.yaml: {cid} не находит статью в базе")
        db_ids = set(session.scalars(select(Citation.citation_id)))
        for cid in sorted(db_ids - yaml_ids):
            res.warn(f"citation {cid} есть в базе, но не в citations.yaml")
    for sc, ids in scenario_citation_ids(paths.scenarios_dir).items():
        for cid in sorted(missing_citation_ids(session, ids)):
            res.error(f"scenarios/{sc}: {cid} не находит статью в базе")


def _sample(session: Session, paths: Paths, vid: int, aid: int, key: str) -> dict[str, Any]:
    v = session.get(DocumentVersion, vid)
    a = session.get(Article, aid)
    assert v is not None and a is not None
    raw = None
    stem = Path(v.raw_file_path).stem if v.raw_file_path else None
    if stem:
        arts_file = paths.processed_dir / f"{stem}.articles.jsonl"
        blocks_file = paths.processed_dir / f"{stem}.blocks.jsonl"
        if arts_file.is_file() and blocks_file.is_file():
            src = next((x for x in read_jsonl(arts_file) if x["article_number"] == a.article_number), None)
            if src:
                lo, hi = src["source_blocks"]
                raw = "\n".join(b["text"] for b in read_jsonl(blocks_file) if lo <= b["idx"] <= hi)
    return {
        "label": f"{key} {v.language} {v.effective_from}, статья {a.article_number}",
        "title": a.article_title,
        "source_url": v.source_url,
        "raw_file": v.raw_file_path,
        "db": a.content,
        "raw": raw,
    }


def _clip(s: str, n: int = 800) -> str:
    return s if len(s) <= n else s[:n] + "…"


def render_report(res: CheckResult) -> str:
    lines = ["# Отчёт проверки (check)", ""]
    lines.append(f"Ошибок: {len(res.errors)}. Предупреждений: {len(res.warnings)}.")
    lines.append("")
    for title, items in (("Ошибки", res.errors), ("Предупреждения", res.warnings)):
        lines.append(f"## {title}")
        lines.append("")
        lines.extend([f"- {i.message}" for i in items] or ["нет"])
        lines.append("")
    lines.append("## Ручная проверка: случайные статьи рядом с исходником")
    lines.append("")
    if not res.samples:
        lines.extend(["нет статей", ""])
    for s in res.samples:
        lines.append(f"### {s['label']}")
        lines.append(f"Название: {s['title'] or '-'}. Файл: {s['raw_file'] or '-'}. Источник: {s['source_url'] or '-'}")
        lines.append("")
        lines.append("В базе:")
        lines.append("```")
        lines.append(_clip(s["db"]))
        lines.append("```")
        lines.append("В исходнике (блоки parse):")
        lines.append("```")
        lines.append(_clip(s["raw"]) if s["raw"] is not None else "(processed-файлы не найдены)")
        lines.append("```")
        lines.append("")
    return "\n".join(lines)
