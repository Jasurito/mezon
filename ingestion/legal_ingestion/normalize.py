"""Шаг 3. normalize: content (только мусор убран) и content_normalized (для поиска, из бэкенда)."""

from __future__ import annotations

import html
import re
from typing import Any

from app.rag.normalize import normalize as search_normalize  # те же правила, что у поиска бэкенда

# NBSP, en/em/thin/narrow/ideographic пробелы → обычный пробел
_SPACES = "               　"
_SPACE_TABLE = {ord(c): " " for c in _SPACES}
# мягкий перенос, zero-width, word joiner, BOM
_REMOVE_TABLE = {ord(c): None for c in "­​‌‍⁠﻿"}
_ENTITY = re.compile(r"&(?:nbsp|amp|quot|lt|gt|apos|shy|#\d+|#x[0-9a-fA-F]+);")
_TAG = re.compile(r"</?(?:br|p|span|div|b|i|u|em|strong|a|font|nobr|sup|sub)\b[^<>]*>", re.IGNORECASE)
_MULTI = re.compile(r"[ \t]{2,}")


def clean_text(text: str) -> str:
    """Только мусор: HTML-артефакты, NBSP, мягкие переносы, двойные пробелы. Остальное дословно."""
    s = _TAG.sub(" ", text)
    s = _ENTITY.sub(lambda m: html.unescape(m.group(0)), s)
    s = s.translate(_REMOVE_TABLE).translate(_SPACE_TABLE)
    s = _MULTI.sub(" ", s)
    return s.strip()


def to_search(text: str, language: str) -> str:
    return search_normalize(text, language)


def normalize_blocks(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for b in blocks:
        text = clean_text(b["text"])
        if text:
            nb = {"idx": b["idx"], "text": text, "style": b["style"]}
            if b.get("lex_id"):
                nb["lex_id"] = b["lex_id"]
            out.append(nb)
    return out
