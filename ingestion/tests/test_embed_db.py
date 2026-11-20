"""Эмбеддинги в конвейере: Ollama на MockTransport, кэш, ошибки."""

import json

import httpx
import pytest
from sqlalchemy import func, select, text

from app.models.legal import Chunk, DocumentVersion
from app.rag.embedder import OllamaEmbedder
from legal_ingestion import pipeline
from legal_ingestion.embed import embed_texts

KEY = "TESTDOC"


class Calls:
    def __init__(self, status=200, dim=4):
        self.requests: list[list[str]] = []
        self.status = status
        self.dim = dim

    def transport(self):
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            self.requests.append(body["input"])
            if self.status != 200:
                return httpx.Response(self.status, text="boom")
            return httpx.Response(200, json={"embeddings": [[1.0] + [0.0] * (self.dim - 1) for _ in body["input"]]})

        return httpx.MockTransport(handler)


def test_embed_texts_batches_and_cache(tmp_path):
    calls = Calls()
    emb = OllamaEmbedder("http://x", transport=calls.transport())
    texts = [f"текст {i}" for i in range(70)] + ["текст 0"]  # дубль не считается дважды
    out = embed_texts(texts, emb, tmp_path)
    assert [len(r) for r in calls.requests] == [32, 32, 6]
    assert len(out) == 71 and out[0] == out[70]
    # второй прогон: всё из кэша, запросов нет
    calls.requests.clear()
    assert embed_texts(texts, emb, tmp_path) == out
    assert calls.requests == []
    # --reembed игнорирует кэш
    embed_texts(texts[:3], emb, tmp_path, reembed=True)
    assert len(calls.requests) == 1


def test_embed_texts_without_embedder(tmp_path):
    from app.rag.embedder import NullEmbedder

    assert embed_texts(["a", "b"], NullEmbedder(), tmp_path) == [None, None]
    assert embed_texts(["a"], None, tmp_path) == [None]


def test_run_with_embedder_fills_vectors_and_cache_prevents_requests(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    calls = Calls()
    emb = OllamaEmbedder("http://x", transport=calls.transport())
    res = pipeline.run(ws.paths, session_factory, emb)
    assert res.ok and calls.requests
    with session_factory() as s:
        total = s.scalar(select(func.count()).select_from(Chunk))
        embedded = s.scalar(text("select count(*) from chunks where embedding is not null and vector_dims(embedding) = 4"))
        assert total == embedded > 0
    assert (ws.paths.cache_dir / "bge-m3.jsonl").is_file()

    # повторный run: редакция не меняется, запросов к Ollama нет
    n = len(calls.requests)
    res = pipeline.run(ws.paths, session_factory, emb)
    assert [e.action for e in res.editions] == ["unchanged"] and len(calls.requests) == n

    # база пуста, кэш на месте: загрузка снова с векторами, но без запросов
    with session_factory.begin() as s:
        s.execute(text("TRUNCATE citations, chunks, article_parts, articles, document_versions, legal_documents RESTART IDENTITY CASCADE"))
    res = pipeline.run(ws.paths, session_factory, emb)
    assert [e.action for e in res.editions] == ["loaded"] and len(calls.requests) == n
    with session_factory() as s:
        assert s.scalar(text("select count(*) from chunks where embedding is null")) == 0


def test_run_fills_missing_vectors_for_existing_edition(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    assert pipeline.run(ws.paths, session_factory).ok  # без эмбеддера
    with session_factory() as s:
        assert s.scalar(text("select count(*) from chunks where embedding is not null")) == 0
    emb = OllamaEmbedder("http://x", transport=Calls().transport())
    res = pipeline.run(ws.paths, session_factory, emb)
    assert [e.action for e in res.editions] == ["updated"]
    with session_factory() as s:
        assert s.scalar(text("select count(*) from chunks where embedding is null")) == 0
        assert s.scalar(select(func.count()).select_from(DocumentVersion)) == 1


def test_ollama_error_fails_edition_with_clear_message_and_loads_nothing(ws, session_factory):
    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    emb = OllamaEmbedder("http://x", transport=Calls(status=404).transport())
    res = pipeline.run(ws.paths, session_factory, emb)
    assert not res.ok
    (e,) = res.editions
    assert e.action == "failed" and "эмбеддинги не посчитаны" in e.error and "ollama pull bge-m3" in e.error
    with session_factory() as s:
        assert s.scalar(select(func.count()).select_from(DocumentVersion)) == 0


def test_backend_search_skips_dense_branch_when_ollama_fails(ws, session_factory, ing_db_url):
    from fastapi.testclient import TestClient

    from app.config import Settings, get_settings
    from app.db import get_db
    from app.main import create_app
    from app.rag.deps import embedder_dep

    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    assert pipeline.run(ws.paths, session_factory, OllamaEmbedder("http://x", transport=Calls().transport())).ok

    bad = OllamaEmbedder("http://x", transport=Calls(status=500).transport())
    app = create_app()
    session = session_factory()
    app.dependency_overrides[get_db] = lambda: session
    app.dependency_overrides[get_settings] = lambda: Settings(DATABASE_URL=ing_db_url, SCENARIOS_DIR=ws.root / "no_scenarios")
    app.dependency_overrides[embedder_dep] = lambda: bad
    with TestClient(app) as c:
        r = c.get("/api/legal/search", params={"q": "первая часть первой статьи", "locale": "ru"})
        assert r.status_code == 200, r.text
        hits = r.json()["results"]
        assert any(h["article_number"] == "1" for h in hits)
        assert all(h["match"]["dense_rank"] is None for h in hits)

    # рабочий эмбеддер: dense-ветка участвует (все векторы одинаковые, ранги заполнены)
    good = OllamaEmbedder("http://x", transport=Calls().transport())
    app.dependency_overrides[embedder_dep] = lambda: good
    with TestClient(app) as c:
        hits = c.get("/api/legal/search", params={"q": "первая часть первой статьи", "locale": "ru"}).json()["results"]
        assert any(h["match"]["dense_rank"] is not None for h in hits)
    session.close()


def test_eval_without_gold_file_gives_clear_message(ws, session_factory):
    from app.config import Settings
    from app.rag.embedder import NullEmbedder
    from legal_ingestion.errors import IngestionError
    from legal_ingestion.evaluation import run_eval

    with pytest.raises(IngestionError, match="gold.jsonl"):
        run_eval(session_factory, ws.paths, Settings(), NullEmbedder())


def test_eval_recall(ws, session_factory, tmp_path):
    from app.config import Settings
    from app.rag.embedder import NullEmbedder
    from legal_ingestion.evaluation import run_eval
    from dataclasses import replace

    ws.add_doc(KEY, [("ru", "2024-01-01", "v1", "html")])
    ws.write_citations('- citation_id: TESTDOC.art.1\n  document_key: TESTDOC\n  article_number: "1"\n')
    assert pipeline.run(ws.paths, session_factory).ok
    gold = tmp_path / "gold.jsonl"
    gold.write_text(
        json.dumps({"id": "g1", "lang": "ru", "question": "первая часть первой статьи", "expected_citations": ["TESTDOC.art.1"], "type": "term"}, ensure_ascii=False)
        + "\n"
        + json.dumps({"id": "g2", "lang": "ru", "question": "погода", "expected_citations": [], "type": "out_of_scope"})
        + "\n",
        encoding="utf-8",
    )
    report = run_eval(session_factory, replace(ws.paths, gold=gold), Settings(), NullEmbedder(), k=5)
    assert "| ru | sparse | 1.000 | 1.000 | 1 |" in report
    assert "| ru | dense | n/a | n/a | 0 |" in report
