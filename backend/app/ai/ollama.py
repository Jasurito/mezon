"""Адаптер локального Ollama с тем же интерфейсом, что и AnthropicLLM."""

from __future__ import annotations

import logging
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

log = logging.getLogger("adolat.ai")

T = TypeVar("T", bound=BaseModel)


class OllamaLLM:
    def __init__(self, url: str, model: str, *, client: httpx.Client | None = None) -> None:
        self._url = url.rstrip("/")
        self._model = model
        self._client = client or httpx.Client()

    def structured(
        self,
        *,
        model: str,
        system: str,
        messages: list[dict[str, Any]],
        output_model: type[T],
        max_tokens: int,
        timeout: float,
        effort: str,
        thinking_disabled: bool = False,
    ) -> T | None:
        # model, max_tokens, effort, thinking_disabled — параметры Anthropic, здесь игнорируются.
        body = {
            "model": self._model,
            "messages": [{"role": "system", "content": system}, *messages],
            "stream": False,
            "format": output_model.model_json_schema(),
            "options": {"temperature": 0},
        }
        try:
            resp = self._client.post(f"{self._url}/api/chat", json=body, timeout=timeout)
            resp.raise_for_status()
            return output_model.model_validate_json(resp.json()["message"]["content"])
        except httpx.TimeoutException:
            log.warning("Ollama %s: таймаут %.1fs", self._model, timeout)
        except Exception as exc:  # noqa: BLE001 - любой сбой = «AI недоступен»
            log.warning("Ollama %s: ошибка: %s", self._model, exc)
        return None
