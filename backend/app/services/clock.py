"""Время как зависимость: движок времени не знает, тесты подменяют get_now."""

from __future__ import annotations

from datetime import UTC, datetime


def get_now() -> datetime:
    return datetime.now(UTC)
