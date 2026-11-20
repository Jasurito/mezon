"""diff: изменения по статьям между редакциями → processed/<key>_diff_<old>_<new>.md (для юриста)."""

from __future__ import annotations

import difflib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.legal import Article, DocumentVersion, LegalDocument
from legal_ingestion.errors import IngestionError
from legal_ingestion.io import write_text_if_changed
from legal_ingestion.load import SessionFactory
from legal_ingestion.paths import Paths


def _articles(session: Session, version_id: int) -> dict[str, Article]:
    rows = session.scalars(select(Article).where(Article.version_id == version_id).order_by(Article.id))
    return {a.article_number: a for a in rows}


def _section(session: Session, old: DocumentVersion, new: DocumentVersion) -> tuple[list[str], tuple[int, int, int]]:
    a_old, a_new = _articles(session, old.id), _articles(session, new.id)
    added = [n for n in a_new if n not in a_old]
    removed = [n for n in a_old if n not in a_new]
    changed = [n for n in a_new if n in a_old and a_old[n].content != a_new[n].content]
    lines = [
        f"## {new.language}: редакция {old.effective_from} (id={old.id}, {old.review_status}) → "
        f"{new.effective_from} (id={new.id}, {new.review_status})",
        "",
        f"Добавлено: {len(added)}. Удалено: {len(removed)}. Изменено: {len(changed)}.",
        "",
    ]
    lines.append("### Добавлены")
    lines.extend([f"- {n}. {a_new[n].article_title or ''}".rstrip() for n in added] or ["нет"])
    lines += ["", "### Удалены"]
    lines.extend([f"- {n}. {a_old[n].article_title or ''}".rstrip() for n in removed] or ["нет"])
    lines += ["", "### Изменены"]
    if not changed:
        lines.append("нет")
    for n in changed:
        lines += ["", f"#### Статья {n}. {a_new[n].article_title or ''}".rstrip(), "```diff"]
        lines.extend(
            difflib.unified_diff(
                a_old[n].content.splitlines(), a_new[n].content.splitlines(), "старая", "новая", lineterm="", n=1
            )
        )
        lines.append("```")
    lines.append("")
    return lines, (len(added), len(removed), len(changed))


def diff_document(session_factory: SessionFactory, paths: Paths, document_key: str) -> list[Path]:
    """Для каждого языка сравнить две последние редакции. Возвращает записанные файлы отчётов."""
    session = session_factory()
    try:
        doc = session.scalar(select(LegalDocument).where(LegalDocument.document_key == document_key))
        if doc is None:
            raise IngestionError(f"документ {document_key} не загружен в базу")
        versions = list(
            session.scalars(
                select(DocumentVersion)
                .where(DocumentVersion.document_id == doc.id)
                .order_by(DocumentVersion.language, DocumentVersion.effective_from, DocumentVersion.id)
            )
        )
        by_lang: dict[str, list[DocumentVersion]] = {}
        for v in versions:
            by_lang.setdefault(v.language, []).append(v)
        reports: dict[tuple[str, str], list[str]] = {}
        for vs in by_lang.values():
            if len(vs) < 2:
                continue
            old, new = vs[-2], vs[-1]
            lines, _ = _section(session, old, new)
            reports.setdefault((str(old.effective_from), str(new.effective_from)), []).extend(lines)
        written: list[Path] = []
        for (d_old, d_new), lines in reports.items():
            path = paths.processed_dir / f"{document_key}_diff_{d_old}_{d_new}.md"
            text = f"# {document_key}: изменения между редакциями\n\n" + "\n".join(lines)
            write_text_if_changed(path, text)
            written.append(path)
        return written
    finally:
        session.close()
