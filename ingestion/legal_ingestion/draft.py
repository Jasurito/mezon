"""sources-draft: черновик legal_data/sources.yaml из скачанных страниц lex.uz (без сети).

Из файлов детерминированно берётся только то, что есть на странице; юридически значимое (is_official_text,
verified_by, дата вступления в силу) оставляется на проверку человеку. Черновик не запускает загрузку в БД.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from legal_ingestion.errors import IngestionError
from legal_ingestion.parse import iter_lexuz
from legal_ingestion.sources import FILENAME_RE

DOC_ORDER = ("CONST", "CC1", "CC2", "CPC", "CPRL")
# id документов на lex.uz (по языкам; у uz-Latn минус): https://lex.uz/docs/<id>
SOURCE_IDS: dict[str, dict[str, str]] = {
    "CONST": {"ru": "6445147", "uz-Latn": "-6445145"},
    "CC1": {"ru": "111181", "uz-Latn": "-111189"},
    "CC2": {"ru": "180550", "uz-Latn": "-180552"},
    "CPC": {"ru": "3517334", "uz-Latn": "-3517337"},
    "CPRL": {"ru": "14643", "uz-Latn": "-4704"},
}
TERMS_SUMMARY = (
    "Отдельной страницы условий использования на lex.uz нет; robots.txt отсутствует (404); в подвале "
    "© ГУ «Национальный правовой информационный центр „Адолат“» при Минюсте. 10 страниц скачаны вручную "
    "по одной с паузой 3 с."
)
SUGGEST_COMMENT = "# предложено автоматически, проверить на lex.uz"

_DATE = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")
_TITLE = re.compile(r"^(?:(?P<num>\S+?)-(?:сон|son)\s+)?(?P<date>\d{2}\.\d{2}\.\d{4})\.\s*(?P<title>.+)$", re.DOTALL)
_DOC_ID = re.compile(r"/docs/(-?\d+)")
_WS = re.compile(r"\s+")


def _d(s: str) -> date:
    m = _DATE.search(s)
    if not m:
        raise ValueError(s)
    return date(int(m[3]), int(m[2]), int(m[1]))


@dataclass
class PageInfo:
    page_title: str = ""
    act_title: str = ""
    act_form: str = ""
    title: str = ""  # название без даты и номера (из <title> страницы, иначе ACT_TITLE)
    number: str | None = None
    adoption_date: date | None = None
    essential: list[str] = field(default_factory=list)
    edition_dates: list[date] = field(default_factory=list)  # выпадающий список редакций (включая будущие)
    selected: date | None = None  # редакция, открытая на странице
    selected_raw: str | None = None
    doc_ids: set[str] = field(default_factory=set)  # id документа из ссылок списка редакций
    document_type: str | None = None


def read_page(html: str) -> PageInfo:
    tree = HTMLParser(html)
    info = PageInfo()
    t = tree.css_first("title")
    info.page_title = _WS.sub(" ", (t.text() if t else "").replace("\xa0", " ")).strip()
    for kind, _lex_id, text in iter_lexuz(tree):
        if kind == "ACT_TITLE" and not info.act_title:
            info.act_title = text
        elif kind == "ACT_FORM" and not info.act_form:
            info.act_form = text
        elif kind == "ACT_ESSENTIAL_ELEMENTS":
            info.essential.append(text)
    m = _TITLE.match(info.page_title)
    if m:
        info.title = m["title"].strip()
        info.adoption_date = _d(m["date"])
        info.number = m["num"]
    else:
        info.title = info.act_title
    if info.number is None:
        for e in info.essential:
            mm = re.match(r"^№\s*(\S+?),?$", e.strip())
            if mm:
                info.number = mm[1]
    for item in tree.css(".dropdown-menu__item.lx_date_link"):
        txt = item.text(strip=True)
        if _DATE.match(txt):
            info.edition_dates.append(_d(txt))
        for mm in _DOC_ID.finditer(item.attributes.get("onclick") or ""):
            info.doc_ids.add(mm[1])
    sel = tree.css_first(".lx_date_selected")
    if sel is not None and _DATE.match(sel.text(strip=True)):
        info.selected_raw = _WS.sub(" ", sel.text(strip=True))
        info.selected = _d(info.selected_raw)
    up = info.act_title.upper()
    form = info.act_form.lower()
    if "КОНСТИТУЦ" in up or "KONSTITUTSIYA" in up:
        info.document_type = "constitution"
    elif "КОДЕКС" in up or "KODEKS" in up:
        info.document_type = "code"
    elif "закон" in form or "qonun" in form:
        info.document_type = "law"
    return info


def suggest_effective_from(info: PageInfo, retrieved_at: date) -> date | None:
    """Самая поздняя дата из списка редакций (с открытой на странице), не позже даты скачивания."""
    cands = [d for d in [*info.edition_dates, *([info.selected] if info.selected else [])] if d <= retrieved_at]
    return max(cands) if cands else None


def scan_raw(raw_dir: Path) -> dict[str, dict[str, tuple[Path, date]]]:
    """{ключ: {язык: (файл, дата в имени)}} по файлам <ключ>_<язык>_<дата>.html в raw/."""
    found: dict[str, dict[str, tuple[Path, date]]] = {}
    for p in sorted(raw_dir.glob("*.htm*")):
        m = FILENAME_RE.match(p.name)
        if m:
            found.setdefault(m["key"], {})[m["lang"]] = (p, date.fromisoformat(m["date"]))
    return found


def build_draft(legal_dir: Path) -> tuple[dict[str, Any], list[str]]:
    """Вернуть (структура sources.yaml, предупреждения). Комментарии добавляет render_yaml."""
    raw = legal_dir / "raw"
    files = scan_raw(raw)
    if not files:
        raise IngestionError(f"в {raw} нет файлов вида <ключ>_<язык>_<дата>.html")
    warnings: list[str] = []
    keys = [k for k in DOC_ORDER if k in files] + sorted(k for k in files if k not in DOC_ORDER)
    documents: list[dict[str, Any]] = []
    for key in keys:
        langs = files[key]
        infos = {lang: read_page(path.read_text(encoding="utf-8")) for lang, (path, _) in langs.items()}
        main = infos.get("ru") or next(iter(infos.values()))
        title = {lang: i.title for lang, i in infos.items() if i.title}
        url_ids = SOURCE_IDS.get(key, {})
        versions: list[dict[str, Any]] = []
        for lang in sorted(langs, key=lambda x: ("ru", "uz-Latn", "uz-Cyrl").index(x)):
            path, fdate = langs[lang]
            info = infos[lang]
            doc_id = url_ids.get(lang) or (sorted(info.doc_ids)[0] if len(info.doc_ids) == 1 else None)
            if info.doc_ids and doc_id not in info.doc_ids:
                warnings.append(f"{key} {lang}: id {doc_id} не совпадает с id в ссылках страницы {sorted(info.doc_ids)}")
            if doc_id is None:
                warnings.append(f"{key} {lang}: не удалось определить source_url")
            eff = suggest_effective_from(info, fdate)
            if eff is None:
                warnings.append(f"{key} {lang}: в списке редакций нет даты ≤ {fdate}; effective_from нужно указать вручную")
            versions.append(
                {
                    "language": lang,
                    "file": f"raw/{path.name}",
                    "source_url": f"https://lex.uz/docs/{doc_id}" if doc_id else "TODO",
                    "effective_from": eff,
                    "effective_to": None,
                    "is_official_text": None,
                    "retrieved_at": fdate,
                    "verified_by": None,
                    "_suggested": eff,
                    "_note": _note(info, eff),
                }
            )
        ru_id = url_ids.get("ru") or (sorted(main.doc_ids)[0] if len(main.doc_ids) == 1 else None)
        documents.append(
            {
                "document_key": key,
                "title": title,
                "document_type": main.document_type or _type_from_key(key, warnings),
                "document_number": main.number,
                "adoption_date": main.adoption_date,
                "issuing_body": None,
                "source_url": f"https://lex.uz/docs/{ru_id}" if ru_id else "TODO",
                "status": "in_force",
                "known_gaps": {},
                "versions": versions,
            }
        )
    data = {
        "terms_of_use": {
            "checked_at": date(2026, 11, 20),
            "checked_by": None,
            "summary": TERMS_SUMMARY,
            "fetch_allowed": False,
        },
        "documents": documents,
    }
    return data, warnings


def _type_from_key(key: str, warnings: list[str]) -> str:
    warnings.append(f"{key}: не удалось определить document_type, поставлен law; проверьте")
    return "law"


def _note(info: PageInfo, eff: date | None) -> str:
    bits = []
    if info.selected_raw:
        bits.append(f"на странице открыта редакция «{info.selected_raw}»")
    later = sorted({d for d in info.edition_dates if eff is not None and d > eff})
    if later:
        bits.append("в списке есть более поздние (ещё не действуют): " + ", ".join(d.strftime("%d.%m.%Y") for d in later))
    return "; ".join(bits)


# --- слияние с существующим файлом и вывод YAML ---------------------------------------------


def _empty(v: Any) -> bool:
    return v is None or v == "" or v == {} or v == []


def merge_existing(draft: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    """Заполненные человеком (не пустые) значения из существующего sources.yaml имеют приоритет над черновиком."""

    def merge(new: Any, old: Any) -> Any:
        if isinstance(new, dict) and isinstance(old, dict):
            out = dict(new)
            for k, ov in old.items():
                out[k] = merge(new[k], ov) if k in new else ov
            return out
        return new if _empty(old) else old

    out = dict(draft)
    if isinstance(existing.get("terms_of_use"), dict):
        out["terms_of_use"] = merge(draft["terms_of_use"], existing["terms_of_use"])
    old_docs = {d.get("document_key"): d for d in existing.get("documents") or [] if isinstance(d, dict)}
    docs = []
    for d in draft["documents"]:
        o = old_docs.pop(d["document_key"], None)
        if o is None:
            docs.append(d)
            continue
        md = {k: merge(v, o[k]) if k in o and k != "versions" else v for k, v in d.items() if k != "versions"}
        md.update({k: v for k, v in o.items() if k not in d})
        old_versions = {v.get("language"): v for v in o.get("versions") or [] if isinstance(v, dict)}
        md["versions"] = [merge(v, old_versions.pop(v["language"])) if v["language"] in old_versions else v for v in d["versions"]]
        md["versions"] += list(old_versions.values())  # редакции, которых нет среди скачанных файлов
        docs.append(md)
    docs += list(old_docs.values())  # документы, добавленные человеком вручную
    out["documents"] = docs
    return out


def _q(v: Any) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, (int, float)):
        return str(v)
    return json.dumps(str(v), ensure_ascii=False)


def render_yaml(data: dict[str, Any]) -> str:
    out = [
        "# ЧЕРНОВИК, собран командой `sources-draft` из скачанных страниц lex.uz. Проверить человеку:",
        "#   - effective_from каждой редакции (дата вступления в силу, а не только дата на странице lex.uz);",
        "#   - is_official_text, verified_by (до проверки редакции грузятся как pending_review);",
        "#   - issuing_body, known_gaps, terms_of_use.checked_by.",
        "# Дата в имени файла = retrieved_at (дата скачивания), а не effective_from.",
        "",
    ]
    t = data["terms_of_use"]
    out += ["terms_of_use:"]
    for k in ("checked_at", "checked_by", "summary", "fetch_allowed"):
        out.append(f"  {k}: {_q(t.get(k))}")
    out += ["", "documents:"]
    for d in data["documents"]:
        out.append(f"  - document_key: {_q(d['document_key'])}")
        out.append("    title:")
        for lang, text in d["title"].items():
            out.append(f"      {lang}: {_q(text)}")
        for k in ("document_type", "document_number", "adoption_date", "issuing_body", "source_url", "status"):
            out.append(f"    {k}: {_q(d.get(k))}")
        gaps = d.get("known_gaps") or {}
        if not gaps:
            out.append("    known_gaps: {}")
        else:
            out.append("    known_gaps:")
            for lang, nums in gaps.items():
                out.append(f"      {lang}: [{', '.join(_q(str(n)) for n in nums)}]")
        out.append("    versions:")
        for v in d["versions"]:
            suggested = v.get("effective_from") is not None and v.get("effective_from") == v.get("_suggested")
            out.append(f"      - language: {_q(v['language'])}")
            out.append(f"        file: {_q(v['file'])}")
            out.append(f"        source_url: {_q(v['source_url'])}")
            ef = f"        effective_from: {_q(v.get('effective_from'))}"
            if suggested:
                ef += f"  {SUGGEST_COMMENT}"
            out.append(ef)
            if v.get("_note"):
                out.append(f"        # {v['_note']}")
            for k in ("effective_to", "is_official_text", "retrieved_at", "verified_by"):
                out.append(f"        {k}: {_q(v.get(k))}")
            if v.get("version_label"):
                out.append(f"        version_label: {_q(v['version_label'])}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def write_draft(legal_dir: Path, target: Path, *, force: bool) -> tuple[str, list[str]]:
    """Собрать и записать черновик. Существующий файл без force не трогается."""
    existed = target.is_file()
    if existed and not force:
        raise IngestionError(f"{target} уже существует; --force перезапишет его, сохранив заполненные поля")
    data, warnings = build_draft(legal_dir)
    if existed:
        try:
            old = yaml.safe_load(target.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise IngestionError(f"{target}: некорректный YAML, слияние невозможно: {exc}") from exc
        if isinstance(old, dict):
            data = merge_existing(data, old)
    text = render_yaml(data)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return text, warnings
