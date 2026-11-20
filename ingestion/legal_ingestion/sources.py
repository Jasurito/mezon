"""Шаг 1. validate: sources.yaml → pydantic-модели (docs/INGESTION.md §3.2)."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

Language = Literal["ru", "uz-Latn", "uz-Cyrl"]
LANGUAGES = ("ru", "uz-Latn", "uz-Cyrl")
DOCUMENT_TYPES = ("constitution", "code", "law", "plenum_resolution", "decree")
SUPPORTED_EXT = ("html", "htm", "docx")

# <key>_<lang>_<date>.<ext>; ключ может содержать «_», поэтому разбор с конца
FILENAME_RE = re.compile(
    r"^(?P<key>.+)_(?P<lang>ru|uz-Latn|uz-Cyrl)_(?P<date>\d{4}-\d{2}-\d{2})\.(?P<ext>[A-Za-z0-9]+)$"
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TermsOfUse(_Strict):
    checked_at: date | None = None
    checked_by: str | None = None
    summary: str | None = None
    fetch_allowed: bool = False


class SourceVersion(_Strict):
    language: Language
    file: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    effective_from: date
    effective_to: date | None = None
    is_official_text: bool | None = None
    retrieved_at: date
    verified_by: str | None = None
    version_label: str | None = None

    @field_validator("verified_by", mode="before")
    @classmethod
    def _blank_to_none(cls, v: Any) -> Any:
        return None if isinstance(v, str) and not v.strip() else v


class SourceDocument(_Strict):
    document_key: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_]*$")
    title: dict[Language, str]
    document_type: Literal["constitution", "code", "law", "plenum_resolution", "decree"]
    document_number: str | None = None
    adoption_date: date | None = None
    issuing_body: str | None = None
    source_url: str = Field(min_length=1)
    status: Literal["in_force", "repealed"] = "in_force"
    versions: list[SourceVersion] = Field(min_length=1)
    # пропуски в нумерации статей, которые не ошибка: {язык: ["5", "6"]}
    known_gaps: dict[Language, list[str]] = Field(default_factory=dict)

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, v: dict[str, str]) -> dict[str, str]:
        if not v or not any(t.strip() for t in v.values()):
            raise ValueError("нужно хотя бы одно название")
        return v

    @field_validator("known_gaps", mode="before")
    @classmethod
    def _gaps_as_str(cls, v: Any) -> Any:
        if isinstance(v, dict):
            return {k: [str(x) for x in vals] if isinstance(vals, list) else vals for k, vals in v.items()}
        return v


class SourcesFile(_Strict):
    terms_of_use: TermsOfUse | None = None
    documents: list[SourceDocument] = Field(default_factory=list)

    def get(self, key: str) -> SourceDocument | None:
        return next((d for d in self.documents if d.document_key == key), None)


def _loc(err: dict[str, Any]) -> str:
    out = ""
    for part in err["loc"]:
        out += f"[{part}]" if isinstance(part, int) else (f".{part}" if out else str(part))
    return out or "<корень>"


def load_sources(path: Path, legal_dir: Path) -> tuple[SourcesFile | None, list[str]]:
    """Прочитать и проверить sources.yaml. Возвращает (модель или None, список понятных ошибок)."""
    if not path.is_file():
        return None, [f"{path}: файл не найден (скопируйте legal_data/sources.example.yaml и заполните)"]
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [f"{path}: некорректный YAML: {exc}"]
    if not isinstance(raw, dict):
        return None, [f"{path}: ожидается словарь с ключом documents"]
    try:
        sources = SourcesFile.model_validate(raw)
    except ValidationError as exc:
        return None, [f"{_loc(e)}: {e['msg']}" for e in exc.errors()]

    errors: list[str] = []
    seen_keys: set[str] = set()
    for di, doc in enumerate(sources.documents):
        where = f"documents[{di}] ({doc.document_key})"
        if doc.document_key in seen_keys:
            errors.append(f"{where}: повторяющийся document_key")
        seen_keys.add(doc.document_key)
        seen_versions: set[tuple[str, date]] = set()
        for vi, v in enumerate(doc.versions):
            vw = f"{where}.versions[{vi}] ({v.language} {v.effective_from})"
            if (v.language, v.effective_from) in seen_versions:
                errors.append(f"{vw}: две редакции с одним языком и effective_from")
            seen_versions.add((v.language, v.effective_from))
            errors.extend(f"{vw}: {m}" for m in check_version_file(doc, v, legal_dir))
            if v.effective_to is not None and v.effective_to <= v.effective_from:
                errors.append(f"{vw}: effective_to должно быть позже effective_from")
    return (sources if not errors else None), errors


def check_version_file(doc: SourceDocument, v: SourceVersion, legal_dir: Path) -> list[str]:
    """Имя файла, расширение и наличие файла редакции."""
    errors: list[str] = []
    path = legal_dir / v.file
    m = FILENAME_RE.match(Path(v.file).name)
    if m is None:
        errors.append(f"имя файла {Path(v.file).name!r} не соответствует <document_key>_<language>_<date>.<ext>")
    else:
        if m["key"] != doc.document_key:
            errors.append(f"имя файла: ключ {m['key']!r} не совпадает с document_key {doc.document_key!r}")
        if m["lang"] != v.language:
            errors.append(f"имя файла: язык {m['lang']!r} не совпадает с language {v.language!r}")
        # Дата в имени: effective_from или дата скачивания (страница lex.uz скачивается «как есть»,
        # а действующая редакция на ней указана внутри файла; sources-draft кладёт в имя retrieved_at)
        if m["date"] not in (v.effective_from.isoformat(), v.retrieved_at.isoformat()):
            errors.append(
                f"имя файла: дата {m['date']} не совпадает с effective_from {v.effective_from}"
                f" и retrieved_at {v.retrieved_at}"
            )
        if m["ext"].lower() not in SUPPORTED_EXT:
            errors.append(f"формат .{m['ext']} не поддерживается (html, docx)")
    if not path.is_file():
        errors.append(f"файл {v.file} не найден в {legal_dir}")
    return errors


def stem_of(doc: SourceDocument | str, v: SourceVersion) -> str:
    """Имя для файлов processed/: стем исходного файла (<ключ>_<язык>_<дата>), как у raw_file_path в БД."""
    key = doc if isinstance(doc, str) else doc.document_key
    stem = Path(v.file).stem
    return stem if FILENAME_RE.match(f"{stem}.x") else f"{key}_{v.language}_{v.effective_from.isoformat()}"
