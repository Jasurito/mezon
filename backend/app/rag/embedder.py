"""Интерфейс эмбеддера для dense-ветки поиска.

Реальную модель (BGE-M3, multilingual-e5-large или облачный API) выбирает ingestion по
eval/gold.jsonl, см. docs/INGESTION.md §7. Здесь только точка расширения: добавьте
фабрику в ``EMBEDDERS`` под значением переменной EMBEDDER. Эмбеддер запроса обязан
быть той же моделью, что и эмбеддинги чанков (иначе размерности не совпадут, и ветка
просто даст пустой результат).
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Sequence
from typing import Any, Literal, Protocol

import httpx

from app.config import Settings

log = logging.getLogger("adolat.rag")


class Embedder(Protocol):
    def embed_query(self, text: str) -> list[float] | None:
        """Вектор запроса; None = ветка недоступна и будет пропущена."""
        ...


class NullEmbedder:
    """Dense-ветка выключена."""

    def embed_query(self, text: str) -> list[float] | None:
        return None


EMBEDDERS: dict[str, Callable[[Settings], Embedder]] = {}


def get_embedder(settings: Settings) -> Embedder:
    name = settings.EMBEDDER
    if not name:
        return NullEmbedder()
    factory = EMBEDDERS.get(name)
    if factory is None:
        log.warning("EMBEDDER=%s не зарегистрирован, dense-ветка выключена", name)
        return NullEmbedder()
    return factory(settings)


# --- Ollama (bge-m3) -------------------------------------------------------------------


class EmbedderError(RuntimeError):
    """Эмбеддер не смог посчитать векторы (сервис недоступен, модель не скачана, мусорный ответ)."""


class OllamaEmbedder:
    """BGE-M3 через Ollama: ``POST {url}/api/embed`` с ``{"model", "input": [тексты]}``.

    Модель надо скачать вручную: ``ollama pull bge-m3``. Размерность вектора 1024.
    Для запросов и пассажей префиксы не нужны. ``embed`` (пачками) использует ingestion и
    поднимает ``EmbedderError``; ``embed_query`` используется поиском и при ошибке
    возвращает None, как NullEmbedder (dense-ветка пропускается).
    """

    name = "ollama-bge-m3"
    dim = 1024

    def __init__(
        self,
        base_url: str,
        *,
        model: str = "bge-m3",
        batch_size: int = 32,
        query_timeout: float = 15.0,
        batch_timeout: float = 120.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.batch_size = batch_size
        self.query_timeout = query_timeout
        self.batch_timeout = batch_timeout
        self._transport = transport

    def _post(self, texts: Sequence[str], timeout: float) -> list[list[float]]:
        url = f"{self.base_url}/api/embed"
        try:
            with httpx.Client(transport=self._transport, timeout=timeout) as client:
                resp = client.post(url, json={"model": self.model, "input": list(texts)})
        except httpx.HTTPError as exc:
            raise EmbedderError(
                f"Ollama недоступна по адресу {self.base_url} ({exc.__class__.__name__}): {exc}"
            ) from exc
        if resp.status_code == 404:
            raise EmbedderError(
                f"Ollama не знает модель {self.model} (HTTP 404). Скачайте её вручную: ollama pull {self.model}"
            )
        if resp.status_code != 200:
            raise EmbedderError(f"Ollama вернула HTTP {resp.status_code}: {resp.text[:200]}")
        try:
            data: Any = resp.json()
            vectors = data["embeddings"]
        except (ValueError, KeyError, TypeError) as exc:
            raise EmbedderError("Ollama вернула ответ без поля embeddings") from exc
        if (
            not isinstance(vectors, list)
            or len(vectors) != len(texts)
            or not all(isinstance(v, list) and v for v in vectors)
        ):
            raise EmbedderError(
                f"Ollama вернула {len(vectors) if isinstance(vectors, list) else '?'} векторов на {len(texts)} текстов"
            )
        return [[float(x) for x in v] for v in vectors]

    def embed(self, texts: Sequence[str], kind: Literal["passage", "query"] = "passage") -> list[list[float]]:
        """Векторы для списка текстов, пачками по ``batch_size``. Ошибка → EmbedderError."""
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            out.extend(self._post(texts[i : i + self.batch_size], self.batch_timeout))
        return out

    def embed_query(self, text: str) -> list[float] | None:
        try:
            return self._post([text], self.query_timeout)[0]
        except EmbedderError as exc:
            log.warning("эмбеддер запроса недоступен, dense-ветка пропущена: %s", exc)
            return None


EMBEDDERS["ollama-bge-m3"] = lambda s: OllamaEmbedder(s.OLLAMA_URL, query_timeout=s.OLLAMA_FAST_TIMEOUT)
