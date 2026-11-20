"""Пути конвейера. По умолчанию всё относительно корня репозитория; каждый путь переопределяется."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Paths:
    legal_dir: Path = REPO_ROOT / "legal_data"
    scenarios_dir: Path = REPO_ROOT / "scenarios"
    sources: Path | None = None
    citations: Path | None = None
    processed: Path | None = None
    gold: Path | None = None
    seed: Path | None = None
    repo_root: Path = REPO_ROOT

    @property
    def sources_file(self) -> Path:
        return self.sources or self.legal_dir / "sources.yaml"

    @property
    def citations_file(self) -> Path:
        return self.citations or self.legal_dir / "citations.yaml"

    @property
    def processed_dir(self) -> Path:
        return self.processed or self.legal_dir / "processed"

    @property
    def gold_file(self) -> Path:
        return self.gold or self.repo_root / "eval" / "gold.jsonl"

    @property
    def seed_file(self) -> Path:
        return self.seed or self.legal_dir / "seed.sql.gz"

    @property
    def cache_dir(self) -> Path:
        return self.processed_dir / "embeddings_cache"
