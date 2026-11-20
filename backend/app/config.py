import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]

# Тесты ставят ADOLAT_NO_DOTENV=1 (tests/conftest.py): локальный .env разработчика
# (ключи, LLM_PROVIDER=ollama и т. п.) не должен влиять на тесты.
_ENV_FILES = None if os.environ.get("ADOLAT_NO_DOTENV") == "1" else (str(REPO_ROOT / ".env"), ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://adolat:adolat@localhost:5433/adolat"
    ANTHROPIC_API_KEY: str | None = None
    LLM_PROVIDER: Literal["anthropic", "ollama"] = "anthropic"
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:12b"
    OLLAMA_MENTOR_TIMEOUT: float = 60
    OLLAMA_FAST_TIMEOUT: float = 15
    LLM_MODEL_MENTOR: str = "claude-haiku-5-5"
    LLM_MODEL_FAST: str = "claude-haiku-5-5"
    LLM_MENTOR_TIMEOUT: float = 20
    LLM_FAST_TIMEOUT: float = 4
    LLM_MENTOR_EFFORT: str = "medium"
    EMBEDDER: str | None = None
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3000"]
    RAG_MIN_SCORE: float = 0.01
    RAG_TOP_K: int = 30  # размер списка каждой ветки поиска перед слиянием
    RAG_RRF_K: int = 60
    RAG_TITLE_SIMILARITY: float = 0.6  # порог pg_trgm word_similarity по названию статьи
    RAG_MAX_SOURCES: int = 8  # сколько статей уходит наставнику
    RERANKER: Literal["none", "llm"] = "none"  # llm = один дополнительный вызов быстрой модели
    RERANK_CANDIDATES: int = 15  # сколько кандидатов отдаётся reranker'у
    RERANK_TIMEOUT: float | None = None  # None = fast_timeout
    SCENARIOS_DIR: Path = REPO_ROOT / "scenarios"
    SEED_PATH: Path | None = None
    STRICT_CITATIONS: bool = True

    @field_validator("ANTHROPIC_API_KEY", "EMBEDDER", "SEED_PATH", "RERANK_TIMEOUT", mode="before")
    @classmethod
    def _empty_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def llm_configured(self) -> bool:
        """«Настроен», а не «доступен»: для ollama доступность проверяется самим вызовом."""
        if self.LLM_PROVIDER == "ollama":
            return True
        return bool(self.ANTHROPIC_API_KEY and self.ANTHROPIC_API_KEY.strip())

    @property
    def mentor_timeout(self) -> float:
        return self.OLLAMA_MENTOR_TIMEOUT if self.LLM_PROVIDER == "ollama" else self.LLM_MENTOR_TIMEOUT

    @property
    def fast_timeout(self) -> float:
        return self.OLLAMA_FAST_TIMEOUT if self.LLM_PROVIDER == "ollama" else self.LLM_FAST_TIMEOUT


@lru_cache
def get_settings() -> Settings:
    return Settings()
