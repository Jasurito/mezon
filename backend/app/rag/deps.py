"""FastAPI-зависимости RAG. Тесты подменяют их через app.dependency_overrides."""

from __future__ import annotations

from fastapi import Depends

from app.config import Settings, get_settings
from app.rag.embedder import Embedder, get_embedder


def embedder_dep(settings: Settings = Depends(get_settings)) -> Embedder:
    return get_embedder(settings)
