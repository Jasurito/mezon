"""OllamaEmbedder на httpx.MockTransport: сеть и модель не нужны."""

from __future__ import annotations

import json

import httpx
import pytest

from app.config import Settings
from app.rag.embedder import EMBEDDERS, EmbedderError, NullEmbedder, OllamaEmbedder, get_embedder


def _transport(calls: list[dict], *, status: int = 200, dim: int = 4):
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls.append({"url": str(request.url), "body": body})
        if status != 200:
            return httpx.Response(status, text="boom")
        return httpx.Response(200, json={"embeddings": [[float(len(t))] * dim for t in body["input"]]})

    return httpx.MockTransport(handler)


def test_embed_batches_and_request_shape():
    calls: list[dict] = []
    emb = OllamaEmbedder("http://ollama:11434/", batch_size=32, transport=_transport(calls))
    texts = [f"t{i}" * (i + 1) for i in range(70)]
    vectors = emb.embed(texts)
    assert [len(c["body"]["input"]) for c in calls] == [32, 32, 6]
    assert calls[0]["url"] == "http://ollama:11434/api/embed"
    assert calls[0]["body"]["model"] == "bge-m3"
    assert len(vectors) == 70
    assert vectors[5][0] == float(len(texts[5]))  # порядок сохранён


def test_embed_empty_makes_no_request():
    calls: list[dict] = []
    assert OllamaEmbedder("http://x", transport=_transport(calls)).embed([]) == []
    assert calls == []


def test_embed_query_returns_vector():
    calls: list[dict] = []
    emb = OllamaEmbedder("http://x", transport=_transport(calls))
    assert emb.embed_query("abc") == [3.0] * 4


@pytest.mark.parametrize("status", [404, 500])
def test_errors_raise_in_embed_and_skip_in_query(status):
    emb = OllamaEmbedder("http://x", transport=_transport([], status=status))
    with pytest.raises(EmbedderError):
        emb.embed(["a"])
    assert emb.embed_query("a") is None


def test_connection_error_is_embedder_error():
    def boom(request):
        raise httpx.ConnectError("refused")

    emb = OllamaEmbedder("http://x", transport=httpx.MockTransport(boom))
    with pytest.raises(EmbedderError, match="недоступна"):
        emb.embed(["a"])
    assert emb.embed_query("a") is None


def test_wrong_vector_count_is_error():
    emb = OllamaEmbedder("http://x", transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"embeddings": []})))
    with pytest.raises(EmbedderError):
        emb.embed(["a"])


def test_registry():
    assert "ollama-bge-m3" in EMBEDDERS
    emb = get_embedder(Settings(EMBEDDER="ollama-bge-m3", OLLAMA_URL="http://h:1"))
    assert isinstance(emb, OllamaEmbedder) and emb.base_url == "http://h:1"
    assert isinstance(get_embedder(Settings(EMBEDDER=None)), NullEmbedder)
