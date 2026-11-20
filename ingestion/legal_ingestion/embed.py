"""Шаг 7. embed: векторы чанков с кэшем по (model, sha256(text)).

Эмбеддер берётся из бэкенда (app.rag.embedder.get_embedder, переменная EMBEDDER). Без EMBEDDER
(NullEmbedder) векторов нет: embedding = null, остальной конвейер работает.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from app.rag.embedder import EmbedderError

from legal_ingestion.errors import IngestionError

log = logging.getLogger("legal_ingestion")

BATCH_SIZE = 32
_PRECISION = 6


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def can_embed(embedder: Any) -> bool:
    return embedder is not None and callable(getattr(embedder, "embed", None))


class EmbeddingCache:
    """JSONL на модель: {"h": sha256, "v": [...]}; дописывается по мере счёта."""

    def __init__(self, cache_dir: Path, model: str) -> None:
        self.path = cache_dir / (re.sub(r"[^A-Za-z0-9._-]+", "_", model) + ".jsonl")
        self.data: dict[str, list[float]] = {}
        if self.path.is_file():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.data[row["h"]] = row["v"]

    def put_many(self, items: dict[str, list[float]]) -> None:
        if not items:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            for h, v in items.items():
                f.write(json.dumps({"h": h, "v": v}) + "\n")
        self.data.update(items)


def embed_texts(
    texts: Sequence[str],
    embedder: Any,
    cache_dir: Path,
    *,
    reembed: bool = False,
    batch_size: int = BATCH_SIZE,
) -> list[list[float] | None]:
    """Векторы в порядке texts. Эмбеддера нет → все None. Ошибка Ollama → IngestionError."""
    if not can_embed(embedder):
        return [None] * len(texts)
    model = getattr(embedder, "model", None) or getattr(embedder, "name", "embedder")
    cache = EmbeddingCache(cache_dir, model)
    hashes = [text_hash(t) for t in texts]
    todo: dict[str, str] = {}
    for h, t in zip(hashes, texts):
        if (reembed or h not in cache.data) and h not in todo:
            todo[h] = t
    items = list(todo.items())
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        try:
            vectors = embedder.embed([t for _, t in batch], kind="passage")
        except EmbedderError as exc:
            raise IngestionError(f"эмбеддинги не посчитаны: {exc}") from exc
        cache.put_many({h: [round(x, _PRECISION) for x in v] for (h, _), v in zip(batch, vectors)})
        log.info("embed: %d/%d новых текстов", min(i + batch_size, len(items)), len(items))
    return [cache.data[h] for h in hashes]
