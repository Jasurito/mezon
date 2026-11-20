"""Конвейер на тестовой БД: загрузка, идемпотентность, версии, link, check, бэкенд поверх загруженных данных."""

import datetime as dt

import pytest
from sqlalchemy import func, select, text

from app.models.legal import Article, ArticlePart, Chunk, Citation, DocumentVersion, LegalDocument
from legal_ingestion import pipeline
from legal_ingestion.cli import main as cli_main
from legal_ingestion.diff import diff_document
from legal_ingestion.load import Edition, load_edition
from legal_ingestion.sources import load_sources

KEY = "TESTDOC"
ALL_LANGS = [(lang, "2024-01-01", "v1", "html") for lang in ("ru", "uz-Latn", "uz-Cyrl")]


def snapshot(sf):
    with sf() as s:
        tables = (LegalDocument, DocumentVersion, Article, ArticlePart, Chunk, Citation)
        return {
            "counts": [s.scalar(select(func.count()).select_from(t)) for t in tables],
            "versions": s.execute(
                select(DocumentVersion.id, DocumentVersion.content_hash, DocumentVersion.review_status, DocumentVersion.effective_to).order_by(DocumentVersion.id)
            ).all(),
            "chunk_ids": list(s.scalars(select(Chunk.id).order_by(Chunk.id))),
        }


def versions(sf):
    with sf() as s:
        return list(s.scalars(select(DocumentVersion).order_by(DocumentVersion.effective_from, DocumentVersion.id)))


def test_run_loads_and_second_run_changes_nothing(ws, session_factory):
    ws.add_doc(KEY, ALL_LANGS)
    r1 = pipeline.run(ws.paths, session_factory)
    assert r1.ok, (r1.errors, r1.check.errors if r1.check else None)
    assert [e.action for e in r1.editions] == ["loaded"] * 3
    snap1 = snapshot(session_factory)
    assert snap1["counts"][0:3] == [1, 3, 18]  # документ, 3 редакции, 6 статей на язык (с преамбулой)
    assert snap1["counts"][4] > 18  # длинная статья дала несколько чанков

    with session_factory() as s:
        v = s.scalars(select(DocumentVersion).where(DocumentVersion.language == "ru")).one()
        assert v.review_status == "active" and v.verified_by == "QA" and v.version_label == "2024-01-01"
        arts = {a.article_number: a for a in s.scalars(select(Article).where(Article.version_id == v.id))}
        assert set(arts) == {"preamble", "1", "2", "2¹", "3", "4"}
        assert arts["3"].status == "repealed"
        # content дословный (без NBSP из HTML), нормализованный текст в нижнем регистре
        assert "\xa0" not in arts["1"].content and arts["1"].content.startswith("Первая часть первой статьи.")
        assert arts["1"].content_normalized == arts["1"].content_normalized.lower()
        chunk = s.scalars(select(Chunk).where(Chunk.article_id == arts["1"].id)).one()
        assert chunk.text.startswith("[Тестовый закон · Статья 1. Первая статья · части 1–2 · редакция от 2024-01-01 · ru]")
        assert chunk.embedding is None  # EMBEDDER не задан
        assert s.scalar(text("select tsv is not null from chunks where id = :i"), {"i": chunk.id})

    r2 = pipeline.run(ws.paths, session_factory)
    assert r2.ok
    assert [e.action for e in r2.editions] == ["unchanged"] * 3
    assert snapshot(session_factory) == snap1


def test_processed_files_written_per_step(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    pipeline.run(ws.paths, session_factory)
    stem = f"{KEY}_ru_2024-01-01"
    for suffix in ("blocks", "norm", "articles", "chunks"):
        assert (ws.paths.processed_dir / f"{stem}.{suffix}.jsonl").is_file()
    assert (ws.paths.processed_dir / "check_report.md").is_file()


def test_new_edition_pending_then_activate(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    assert pipeline.run(ws.paths, session_factory).ok
    ws.add_doc(KEY, [("ru", "2025-03-01", "v2", "html")], verified_by=None)
    # у новой редакции нет verified_by, у старой есть

    res = pipeline.run(ws.paths, session_factory)
    assert [e.action for e in res.editions] == ["unchanged", "loaded"]
    old, new = versions(session_factory)
    assert (old.review_status, old.effective_to) == ("active", None)
    assert new.review_status == "pending_review" and new.verified_by is None
    assert res.check and not any("verified_by" in i.message for i in res.check.errors)

    # pending_review не участвует в статусе действующей редакции; повторный run ничего не меняет
    snap = snapshot(session_factory)
    pipeline.run(ws.paths, session_factory)
    assert snapshot(session_factory) == snap

    # diff между редакциями
    written = diff_document(session_factory, ws.paths, KEY)
    assert [p.name for p in written] == [f"{KEY}_diff_2024-01-01_2025-03-01.md"]
    report = written[0].read_text(encoding="utf-8")
    assert "Добавлено: 1" in report and "Изменено: 1" in report and "Новая статья" in report

    code = cli_main(
        ["--legal-dir", str(ws.legal), "--processed-dir", str(ws.paths.processed_dir), "activate", "--doc", KEY,
         "--version", str(new.id), "--by", "AB", "--database-url", str(session_factory.kw["bind"].url.render_as_string(hide_password=False))]
    )
    assert code == 0
    old, new = versions(session_factory)
    assert new.review_status == "active" and new.verified_by == "AB" and new.last_verified_at == dt.date.today()
    assert old.review_status == "superseded" and old.effective_to == dt.date(2025, 3, 1)
    # старая редакция не удалена
    with session_factory() as s:
        assert s.scalar(select(func.count()).select_from(Article).where(Article.version_id == old.id)) == 6


def test_new_edition_with_verified_by_supersedes_immediately(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html"), ("ru", "2025-03-01", "v2", "docx")])
    assert pipeline.run(ws.paths, session_factory).ok
    old, new = versions(session_factory)
    assert (old.review_status, old.effective_to) == ("superseded", dt.date(2025, 3, 1))
    assert (new.review_status, new.effective_to) == ("active", None)


def test_load_is_atomic(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    sources, errs = load_sources(ws.paths.sources_file, ws.paths.legal_dir)
    assert not errs
    d = sources.documents[0]
    ed = pipeline.prepare_edition(ws.paths, d, d.versions[0])
    ed.chunks = pipeline.chunk_edition(ws.paths, d, d.versions[0], ed.articles)
    ed.chunks[-1] = {**ed.chunks[-1], "article_number": "no-such-article"}  # упадёт в середине загрузки
    with pytest.raises(KeyError):
        load_edition(session_factory, ed)
    snap = snapshot(session_factory)
    assert snap["counts"] == [0, 0, 0, 0, 0, 0]


CIT_OK = """
- citation_id: TESTDOC.art.1
  document_key: TESTDOC
  article_number: "1"
  topic: "первая"
  verified_by: "QA"
- citation_id: TESTDOC.art.2-1
  document_key: TESTDOC
  article_number: "2¹"
  part: 1
  topic: "вставная"
  verified_by: "QA"
"""


def test_link_ok_and_missing_article_is_error(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    ws.write_citations(CIT_OK + '- citation_id: TESTDOC.art.99\n  document_key: TESTDOC\n  article_number: "99"\n')
    res = pipeline.run(ws.paths, session_factory)
    assert not res.ok
    assert any("TESTDOC.art.99" in m and "не найдена" in m for m in res.link_errors)
    assert snapshot(session_factory)["counts"][5] == 0  # ничего из citations не записано

    ws.write_citations(CIT_OK)
    res = pipeline.run(ws.paths, session_factory)
    assert res.ok and res.citations == 2
    snap = snapshot(session_factory)
    assert snap["counts"][5] == 2
    pipeline.run(ws.paths, session_factory)
    assert snapshot(session_factory) == snap

    # часть, которой нет, тоже ошибка
    ws.write_citations(CIT_OK + '- citation_id: TESTDOC.art.1.p9\n  document_key: TESTDOC\n  article_number: "1"\n  part: 9\n')
    res = pipeline.run(ws.paths, session_factory)
    assert any("нет части 9" in m for m in res.link_errors)


def test_check_finds_gap_and_empty_article(ws, session_factory):
    ws.add_doc("GAPDOC", [("ru", "2024-01-01", "gap", "html")])
    ws.add_doc("EMPTYDOC", [("ru", "2024-01-01", "empty", "html")])
    res = pipeline.run(ws.paths, session_factory)
    assert not res.ok
    msgs = [i.message for i in res.check.errors]
    assert any("GAPDOC" in m and "пропущены номера статей 3" in m for m in msgs)
    assert any("EMPTYDOC" in m and "пустая статья 2" in m for m in msgs)
    report = (ws.paths.processed_dir / "check_report.md").read_text(encoding="utf-8")
    assert "пропущены номера статей 3" in report
    assert cli_main(
        ["--legal-dir", str(ws.legal), "--processed-dir", str(ws.paths.processed_dir), "--scenarios-dir", str(ws.root / "none"),
         "check", "--database-url", str(session_factory.kw["bind"].url.render_as_string(hide_password=False))]
    ) == 1


def test_known_gaps_silence_error(ws, session_factory):
    ws.add_doc("GAPDOC", [("ru", "2024-01-01", "gap", "html")], known_gaps={"ru": ["3"]})
    res = pipeline.run(ws.paths, session_factory)
    assert not any("GAPDOC" in i.message and "пропущены" in i.message for i in res.check.errors)


def test_check_validates_scenario_citations(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    ws.write_citations(CIT_OK)
    sc = ws.root / "scenarios" / "demo"
    sc.mkdir(parents=True)
    (sc / "scenario.json").write_text(
        '{"citations": ["TESTDOC.art.1", "TESTDOC.art.404"], "stages": [{"hint_citation_ids": ["TESTDOC.art.77"]}]}',
        encoding="utf-8",
    )
    res = pipeline.run(ws.paths, session_factory)
    msgs = [i.message for i in res.check.errors]
    assert any("TESTDOC.art.404" in m for m in msgs) and any("TESTDOC.art.77" in m for m in msgs)
    assert not any("TESTDOC.art.1 " in m for m in msgs)


def test_check_reports_active_without_verified_by(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    assert pipeline.run(ws.paths, session_factory).ok
    with session_factory.begin() as s:
        s.execute(text("update document_versions set verified_by = null"))
    from legal_ingestion.check import run_check

    res = run_check(session_factory, ws.paths, load_sources(ws.paths.sources_file, ws.paths.legal_dir)[0])
    assert any("без verified_by" in i.message for i in res.errors)


def test_run_aborts_on_invalid_sources(ws, session_factory):
    from legal_ingestion.errors import IngestionError

    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    (ws.legal / "raw" / f"{KEY}_ru_2024-01-01.html").unlink()
    with pytest.raises(IngestionError, match="не найден"):
        pipeline.run(ws.paths, session_factory)


def test_backend_serves_loaded_data(ws, session_factory, ing_db_url):
    from fastapi.testclient import TestClient

    from app.config import Settings, get_settings
    from app.db import get_db
    from app.main import create_app

    ws.add_doc(KEY, ALL_LANGS)
    ws.write_citations(CIT_OK)
    assert pipeline.run(ws.paths, session_factory).ok

    app = create_app()
    session = session_factory()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_settings] = lambda: Settings(DATABASE_URL=ing_db_url, SCENARIOS_DIR=ws.root / "no_scenarios")
    with TestClient(app) as c:
        r = c.get("/api/legal/search", params={"q": "первая часть первой статьи", "locale": "ru"})
        assert r.status_code == 200, r.text
        hits = r.json()["results"]
        assert any(h["article_number"] == "1" and h["citation_id"] == "TESTDOC.art.1" for h in hits)
        top = next(h for h in hits if h["article_number"] == "1")
        assert not top["snippet"].startswith("[") and "Первая часть" in top["snippet"]
        assert top["edition_status"] == "current"

        r = c.get("/api/legal/search", params={"q": "birinchi moddaning ikkinchi qismi", "locale": "uz-Latn"})
        assert any(h["article_number"] == "1" for h in r.json()["results"])
        r = c.get("/api/legal/search", params={"q": "биринчи модданинг иккинчи қисми", "locale": "uz-Cyrl"})
        assert any(h["article_number"] == "1" for h in r.json()["results"])

        r = c.get("/api/legal/citations/TESTDOC.art.1", params={"locale": "ru"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["article_number"] == "1" and body["document_key"] == KEY
        assert body["text"].startswith("Первая часть первой статьи.")
        assert [p["part_number"] for p in body["parts"]] == [1, 2]
        r = c.get("/api/legal/citations/TESTDOC.art.2-1", params={"locale": "ru"})
        assert r.status_code == 200 and r.json()["part"] == 1
    session.close()
