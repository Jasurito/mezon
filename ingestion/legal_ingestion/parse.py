"""Шаг 2. parse: HTML/DOCX → упорядоченные текстовые блоки {idx, text, style[, lex_id]}.

Страницы lex.uz (в HTML есть элементы `.lx_elem`) разбираются специализированно (_parse_lexuz): текст акта
лежит только в `.lx_elem`, панель интерфейса `.lx_elem2` и служебные вставки `.lx_no_select` (комментарии,
«в редакции Закона…», классификаторы) в блоки не попадают. Прочий HTML и DOCX идут общим путём
(BODY_SELECTORS / STRIP_*).

style блока: heading | paragraph | note (общий путь); для lex.uz дополнительно meta (форма и название акта),
clause (заголовок статьи), footer (подпись, место, дата, номер акта в конце).
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from legal_ingestion.errors import IngestionError
from legal_ingestion.patterns import SUP_TABLE, is_note

log = logging.getLogger("legal_ingestion")

# --- Настройка под lex.uz ----------------------------------------------------------------
# Общий путь (не lex.uz): кандидаты CSS-селекторов тела документа; берётся первый найденный, иначе <body>.
# Для lex.uz эти константы не используются: см. LEXUZ_* ниже.
BODY_SELECTORS: tuple[str, ...] = ("#actContent", ".ACT_TEXT", "main", "article")
# Что вырезается вокруг тела (навигация, меню, скрипты)
STRIP_TAGS: tuple[str, ...] = (
    "script", "style", "noscript", "nav", "header", "footer", "aside", "form", "iframe",
    "svg", "button", "select", "template",
)
STRIP_SELECTORS: tuple[str, ...] = (
    "[role=navigation]", ".menu", ".navbar", ".breadcrumb", ".breadcrumbs", ".sidebar", ".pagination",
)
# Разметка lex.uz: класс элемента `.lx_elem` → style блока. BY_DEFAULT — пустой разделитель (пустые пропускаются).
LEXUZ_ELEM = ".lx_elem"
LEXUZ_STYLES: dict[str, str] = {
    "ACT_FORM": "meta",
    "ACT_TITLE": "meta",
    "TEXT_HEADER_DEFAULT": "heading",
    "TEXT_BOLD_CENTER": "heading",
    "CLAUSE_DEFAULT": "clause",
    "ACT_TEXT": "paragraph",
    "BY_DEFAULT": "paragraph",
    "SIGNATURE": "footer",
    "ACT_ESSENTIAL_ELEMENTS": "footer",
}
LEXUZ_UI_CLASS = "lx_elem2"  # «Предложения по документу», «Прослушать аудио», «Получить ссылку…»
LEXUZ_SKIP_CLASS = "lx_no_select"  # служебные вставки lex.uz, не текст закона
# -------------------------------------------------------------------------------------------

BLOCK_TAGS = {
    "p", "div", "li", "ul", "ol", "table", "tr", "td", "th", "blockquote", "pre", "section",
    "article", "main", "h1", "h2", "h3", "h4", "h5", "h6", "dd", "dt", "dl", "center", "tbody", "thead",
}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BOLD_TAGS = {"b", "strong"}
_WS = re.compile(r"[ \t\r\n\f\v]+")


def _style(text: str, language: str | None, *, heading: bool) -> str:
    if is_note(text, language):
        return "note"
    return "heading" if heading else "paragraph"


class _Collector:
    def __init__(self, language: str | None) -> None:
        self.language = language
        self.blocks: list[dict[str, Any]] = []
        self.buf: list[tuple[str, bool]] = []  # (текст, жирный)
        self.in_heading = 0

    def flush(self) -> None:
        text = _WS.sub(" ", "".join(t for t, _ in self.buf)).strip()
        if text:
            visible = [(t, b) for t, b in self.buf if t.strip()]
            bold = self.in_heading > 0 or (bool(visible) and all(b for _, b in visible))
            self.blocks.append(
                {"idx": len(self.blocks), "text": text, "style": _style(text, self.language, heading=bold)}
            )
        self.buf = []

    def walk(self, node: Node, bold: bool) -> None:
        for child in node.iter(include_text=True):
            tag = child.tag
            if tag == "-text":
                self.buf.append((child.text_content or "", bold))
            elif tag == "br":
                self.flush()
            elif tag.startswith("-"):  # комментарии и прочее
                continue
            elif tag in BLOCK_TAGS:
                self.flush()
                is_h = tag in HEADING_TAGS
                if is_h:
                    self.in_heading += 1
                self.walk(child, bold)
                self.flush()
                if is_h:
                    self.in_heading -= 1
            else:
                self.walk(child, bold or tag in BOLD_TAGS)


def _classes(node: Node) -> list[str]:
    return (node.attributes.get("class") or "").split()


def _inline_text(node: Node, sep: str, out: list[str]) -> None:
    """Текст узла: <sup>N</sup> → надстрочные («26¹»), <br> → sep, служебные вставки пропускаются."""
    for child in node.iter(include_text=True):
        tag = child.tag
        if tag == "-text":
            out.append(child.text_content or "")
        elif tag == "br":
            out.append(sep)
        elif tag.startswith("-") or tag in ("script", "style"):
            continue
        elif LEXUZ_SKIP_CLASS in _classes(child):
            continue
        elif tag == "sup":
            sup = child.text().strip()
            # на lex.uz бывает «285<sup>1.</sup>»: знак препинания внутри sup остаётся как есть
            out.append(sup.translate(SUP_TABLE) if re.fullmatch(r"\d+\W*", sup) else sup)
        else:
            _inline_text(child, sep, out)


def iter_lexuz(tree: HTMLParser) -> Iterator[tuple[str | None, str | None, str]]:
    """Элементы `.lx_elem` по порядку: (класс стиля, lex_id, текст). Пустые элементы пропускаются."""
    unknown: set[str] = set()
    for elem in tree.css(LEXUZ_ELEM):
        cls = [c for c in _classes(elem) if c != "lx_elem"]
        kind = next((c for c in cls if c in LEXUZ_STYLES), None)
        if kind is None:
            unknown.update(cls)
        # текст — дочерний div[id]; id = номер элемента lex.uz
        body = next(
            (c for c in elem.iter() if c.tag == "div" and LEXUZ_UI_CLASS not in _classes(c) and c.attributes.get("id") is not None),
            None,
        )
        if body is None:
            continue
        parts: list[str] = []
        _inline_text(body, "\n" if kind == "ACT_TEXT" else " ", parts)
        text = "\n".join(_WS.sub(" ", line).strip() for line in "".join(parts).split("\n"))
        text = re.sub(r"\n{2,}", "\n", text).strip()
        if text:
            yield kind, body.attributes.get("id") or None, text
    if unknown:
        log.warning("lex.uz: неизвестные классы элементов (разобраны как абзацы): %s", ", ".join(sorted(unknown)))


def _parse_lexuz(tree: HTMLParser) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for kind, lex_id, text in iter_lexuz(tree):
        block: dict[str, Any] = {"idx": len(blocks), "text": text, "style": LEXUZ_STYLES.get(kind or "", "paragraph")}
        if lex_id:
            block["lex_id"] = lex_id
        blocks.append(block)
    return blocks


def parse_html(
    html: str, language: str | None = None, body_selectors: tuple[str, ...] | None = None
) -> list[dict[str, Any]]:
    tree = HTMLParser(html)
    if body_selectors is None and tree.css_first(LEXUZ_ELEM) is not None:
        blocks = _parse_lexuz(tree)
        for b in blocks:
            if b["style"] == "paragraph" and is_note(b["text"], language):
                b["style"] = "note"
        return blocks
    tree.strip_tags(list(STRIP_TAGS))
    for sel in STRIP_SELECTORS:
        for n in tree.css(sel):
            n.decompose()
    body = None
    for sel in body_selectors if body_selectors is not None else BODY_SELECTORS:
        body = tree.css_first(sel)
        if body is not None:
            break
    if body is None:
        body = tree.body or tree.root
    if body is None:
        raise IngestionError("в HTML не найдено тело документа")
    col = _Collector(language)
    col.walk(body, False)
    col.flush()
    return col.blocks


def parse_docx(path: Path, language: str | None = None) -> list[dict[str, Any]]:
    import docx

    document = docx.Document(str(path))
    blocks: list[dict[str, Any]] = []
    for para in document.paragraphs:
        runs = [r for r in para.runs if r.text.strip()]
        bold = bool(runs) and all(r.bold for r in runs)
        style_name = (para.style.name if para.style is not None else "") or ""
        heading = bold or style_name.lower().startswith(("heading", "title"))
        for line in re.split(r"[\n\v]", para.text):
            text = _WS.sub(" ", line).strip()
            if text:
                blocks.append({"idx": len(blocks), "text": text, "style": _style(text, language, heading=heading)})
    return blocks


def parse_file(path: Path, language: str | None = None) -> list[dict[str, Any]]:
    ext = path.suffix.lower()
    if ext in (".html", ".htm"):
        raw = path.read_bytes()
        try:
            html = raw.decode("utf-8")
        except UnicodeDecodeError:
            html = raw.decode("cp1251", errors="replace")
        blocks = parse_html(html, language)
    elif ext == ".docx":
        blocks = parse_docx(path, language)
    else:
        raise IngestionError(f"{path.name}: формат {ext} не поддерживается (html, docx)")
    if not blocks:
        raise IngestionError(f"{path.name}: в файле не найден текст (проверьте BODY_SELECTORS в parse.py)")
    return blocks
