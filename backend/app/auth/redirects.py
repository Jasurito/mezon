"""Безопасный параметр next: только относительный путь на этом же сайте."""

from __future__ import annotations

from urllib.parse import urlsplit

MAX_NEXT_LEN = 512


def safe_next(value: str | None) -> str:
    if not value or len(value) > MAX_NEXT_LEN:
        return "/"
    if not value.startswith("/") or value.startswith("//") or "\\" in value:
        return "/"
    if any(ord(c) < 0x20 or ord(c) == 0x7F for c in value):  # браузеры вырезают \t \r \n и склеивают в //
        return "/"
    p = urlsplit(value)
    if p.scheme or p.netloc:
        return "/"
    return value
