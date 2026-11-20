"""Разбор SSE-ответа наставника в тестах."""

from __future__ import annotations

import json


def parse_sse(body: str) -> list[tuple[str, object]]:
    events = []
    for raw in body.strip().split("\n\n"):
        if not raw.strip():
            continue
        lines = raw.split("\n")
        assert lines[0].startswith("event: "), raw
        assert len(lines) == 2 and lines[1].startswith("data: "), raw  # JSON в одну строку
        events.append((lines[0][len("event: "):], json.loads(lines[1][len("data: "):])))
    return events


def names(events) -> list[str]:
    return [n for n, _ in events]


def first(events, name):
    return next(d for n, d in events if n == name)
