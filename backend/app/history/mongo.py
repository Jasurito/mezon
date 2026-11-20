"""MongoHistoryStore: коллекции session_history и user_activity. Все методы ловят PyMongoError."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from pymongo import DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from app.history.store import HistoryStore

log = logging.getLogger("adolat.history")

COOLDOWN_SEC = 30.0  # после сбоя Mongo не дёргается, чтобы каждый запрос не ждал таймаут


class MongoHistoryStore(HistoryStore):
    available = True

    def __init__(self, url: str, db_name: str, *, timeout_ms: int = 1500) -> None:
        self._client: MongoClient = MongoClient(
            url, serverSelectionTimeoutMS=timeout_ms, connectTimeoutMS=timeout_ms, tz_aware=True
        )
        self._db = self._client[db_name]
        self.sessions = self._db["session_history"]
        self.activity = self._db["user_activity"]
        self._down_until = 0.0

    # --- helpers
    def _guard(self, what: str, fn, default=None):
        if time.monotonic() < self._down_until:
            return default
        try:
            return fn()
        except PyMongoError as exc:
            self._down_until = time.monotonic() + COOLDOWN_SEC
            log.warning("MongoDB: %s не удалось (%s: %s)", what, exc.__class__.__name__, str(exc)[:200])
            return default

    # --- lifecycle
    def ensure_indexes(self) -> None:
        def run():
            self.activity.create_index([("user_id", 1), ("ts", DESCENDING)], name="user_ts")
            self.sessions.create_index([("user_id", 1), ("started_at", DESCENDING)], name="user_started")

        self._guard("создание индексов", run)

    def close(self) -> None:
        try:
            self._client.close()
        except PyMongoError:  # pragma: no cover
            pass

    # --- sessions
    def start_session(self, doc: dict[str, Any]) -> None:
        body = {k: v for k, v in doc.items() if k != "_id"}
        self._guard(
            "start_session",
            lambda: self.sessions.update_one({"_id": doc["_id"]}, {"$setOnInsert": body}, upsert=True),
        )

    def push_step(self, session_id: str, step: dict[str, Any]) -> None:
        self._guard(
            "push_step",
            lambda: self.sessions.update_one(
                {"_id": session_id, "steps.seq": {"$ne": step["seq"]}}, {"$push": {"steps": step}}
            ),
        )

    def finish_session(self, session_id: str, fields: dict[str, Any]) -> None:
        self._guard("finish_session", lambda: self.sessions.update_one({"_id": session_id}, {"$set": fields}))

    def upsert_session(self, doc: dict[str, Any]) -> None:
        self._guard("upsert_session", lambda: self.sessions.replace_one({"_id": doc["_id"]}, doc, upsert=True))

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        return self._guard("get_session", lambda: self.sessions.find_one({"_id": session_id}))

    # --- activity
    def add_activity(self, doc: dict[str, Any]) -> None:
        self._guard("add_activity", lambda: self.activity.replace_one({"_id": doc["_id"]}, doc, upsert=True))

    def list_activity(self, user_id: str, limit: int, before: datetime | None) -> list[dict[str, Any]] | None:
        flt: dict[str, Any] = {"user_id": user_id}
        if before is not None:
            flt["ts"] = {"$lt": before}

        def run():
            return list(self.activity.find(flt).sort([("ts", DESCENDING), ("_id", DESCENDING)]).limit(limit))

        return self._guard("list_activity", run, default=None)
