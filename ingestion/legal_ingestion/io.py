"""JSONL-вывод шагов. Файл переписывается только если содержимое изменилось (идемпотентность)."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def write_text_if_changed(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> bool:
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    return write_text_if_changed(path, text)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out
