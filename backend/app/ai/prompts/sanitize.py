"""Очистка недоверенного текста (чанки закона, история, вопрос) перед вставкой в промпт.

Текст в контексте остаётся данными: из него убираются угловые скобки (теги, в том числе
закрывающий </source>), метки ролей, ограждения кода и похожие на служебные токены.
"""

from __future__ import annotations

import re

_ANGLES = str.maketrans({"<": "‹", ">": "›"})
_ROLE_LINE = re.compile(r"(?im)^(\s*)(system|assistant|user|human|developer|ai)\s*:")
_SPECIAL = re.compile(r"\[/?(?:INST|SYS)\]|\{\{.*?\}\}|#{3,}|`{3,}|~{3,}", re.DOTALL)


def sanitize_text(text: str) -> str:
    s = text.translate(_ANGLES)
    s = _ROLE_LINE.sub(lambda m: f"{m.group(1)}{m.group(2)} -", s)
    s = _SPECIAL.sub(" ", s)
    return s.strip()


def escape_attr(value: str) -> str:
    """Значение XML-атрибута: без кавычек, угловых скобок и переводов строк."""
    return sanitize_text(value).replace('"', "'").replace("&", "и").replace("\n", " ")
