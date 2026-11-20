"""История игрока в MongoDB (производная от Postgres). Без MONGO_URL работает NullHistoryStore."""

from __future__ import annotations

from fastapi import Request

from app.config import Settings
from app.history.store import HistoryStore, InMemoryHistoryStore, NullHistoryStore


def build_store(settings: Settings) -> HistoryStore:
    if not settings.MONGO_URL:
        return NullHistoryStore()
    from app.history.mongo import MongoHistoryStore

    return MongoHistoryStore(settings.MONGO_URL, settings.MONGO_DB)


def get_history(request: Request) -> HistoryStore:
    """Зависимость FastAPI; тесты подменяют через dependency_overrides[get_history]."""
    return getattr(request.app.state, "history", None) or NullHistoryStore()


__all__ = ["HistoryStore", "InMemoryHistoryStore", "NullHistoryStore", "build_store", "get_history"]
