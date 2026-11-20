"""Интерфейс хранилища истории (MongoDB) и две реализации без сети: Null и InMemory.

Postgres остаётся источником истины; история производная и восстанавливается командой backfill.
Методы записи best-effort: ошибки хранилища логируются и наружу не выходят.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

log = logging.getLogger("adolat.history")


def _canon_ts(ts: datetime) -> str:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=UTC)
    return ts.astimezone(UTC).isoformat()


def activity_key(
    user_id: uuid.UUID | str, type_: str, ts: datetime, session_id: uuid.UUID | str | None, payload: dict[str, Any]
) -> str:
    """Детерминированный _id записи активности: живая запись и backfill дают один и тот же ключ."""
    raw = json.dumps(
        [str(user_id), type_, _canon_ts(ts), str(session_id) if session_id else None, payload],
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def make_activity(
    user_id: uuid.UUID | str,
    type_: str,
    ts: datetime,
    session_id: uuid.UUID | str | None,
    payload: dict[str, Any] | None,
) -> dict[str, Any]:
    payload = payload or {}
    return {
        "_id": activity_key(user_id, type_, ts, session_id, payload),
        "user_id": str(user_id),
        "type": type_,
        "ts": ts,
        "session_id": str(session_id) if session_id else None,
        "payload": payload,
    }


class HistoryStore(ABC):
    #: история включена (для Null = False); не гарантирует, что сервер доступен
    available: bool = True

    def ensure_indexes(self) -> None:  # noqa: B027
        pass

    def close(self) -> None:  # noqa: B027
        pass

    @abstractmethod
    def start_session(self, doc: dict[str, Any]) -> None:
        """Создать документ сессии (идемпотентно: существующий не трогается)."""

    @abstractmethod
    def push_step(self, session_id: str, step: dict[str, Any]) -> None:
        """Добавить шаг, если шага с таким seq ещё нет."""

    @abstractmethod
    def finish_session(self, session_id: str, fields: dict[str, Any]) -> None:
        """$set итогов: finished_at, outcome, score, max_score."""

    @abstractmethod
    def upsert_session(self, doc: dict[str, Any]) -> None:
        """Заменить документ целиком (backfill)."""

    @abstractmethod
    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Документ или None (нет документа, Mongo выключена или недоступна)."""

    @abstractmethod
    def add_activity(self, doc: dict[str, Any]) -> None:
        """Записать активность; повтор с тем же _id не создаёт дубль."""

    @abstractmethod
    def list_activity(self, user_id: str, limit: int, before: datetime | None) -> list[dict[str, Any]] | None:
        """Новые сверху; None = хранилище недоступно."""


class NullHistoryStore(HistoryStore):
    available = False

    def start_session(self, doc):
        pass

    def push_step(self, session_id, step):
        pass

    def finish_session(self, session_id, fields):
        pass

    def upsert_session(self, doc):
        pass

    def get_session(self, session_id):
        return None

    def add_activity(self, doc):
        pass

    def list_activity(self, user_id, limit, before):
        return []


class InMemoryHistoryStore(HistoryStore):
    """Для тестов без Mongo: те же семантики идемпотентности, что у MongoHistoryStore."""

    def __init__(self) -> None:
        self.sessions: dict[str, dict[str, Any]] = {}
        self.activity: dict[str, dict[str, Any]] = {}

    def start_session(self, doc):
        self.sessions.setdefault(doc["_id"], copy.deepcopy(doc))

    def push_step(self, session_id, step):
        d = self.sessions.get(session_id)
        if d is not None and all(s["seq"] != step["seq"] for s in d["steps"]):
            d["steps"].append(copy.deepcopy(step))

    def finish_session(self, session_id, fields):
        d = self.sessions.get(session_id)
        if d is not None:
            d.update(copy.deepcopy(fields))

    def upsert_session(self, doc):
        self.sessions[doc["_id"]] = copy.deepcopy(doc)

    def get_session(self, session_id):
        d = self.sessions.get(session_id)
        return copy.deepcopy(d) if d is not None else None

    def add_activity(self, doc):
        self.activity[doc["_id"]] = copy.deepcopy(doc)

    def list_activity(self, user_id, limit, before):
        rows = [a for a in self.activity.values() if a["user_id"] == user_id]
        if before is not None:
            rows = [a for a in rows if a["ts"] < before]
        rows.sort(key=lambda a: (a["ts"], a["_id"]), reverse=True)
        return copy.deepcopy(rows[:limit])


def safely(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
    """Вызов записи в историю: любая ошибка логируется и не ломает игровой запрос."""
    try:
        fn(*args, **kwargs)
    except Exception:  # noqa: BLE001
        log.exception("не удалось записать историю")
