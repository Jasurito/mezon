"""Интерфейс эмбеддера для dense-ветки поиска.

Реальную модель (BGE-M3, multilingual-e5-large или облачный API) выбирает ingestion по
eval/gold.jsonl, см. docs/INGESTION.md §7. Здесь только точка расширения: добавьте
фабрику в ``EMBEDDERS`` под значением переменной EMBEDDER. Эмбеддер запроса обязан
быть той же моделью, что и эмбеддинги чанков (иначе размерности не совпадут, и ветка
просто даст пустой результат).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Protocol

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
