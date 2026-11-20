"""Тонкий интерфейс вызова LLM со структурированным выводом.

Пайплайн наставника знает только протокол ``LLM``. Другого провайдера можно добавить
ещё одной реализацией и веткой в ``get_llm``, остальной код не меняется.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol, TypeVar

import anthropic
from fastapi import Depends
from pydantic import BaseModel, ValidationError

from app.config import Settings, get_settings

log = logging.getLogger("adolat.ai")

T = TypeVar("T", bound=BaseModel)


class LLM(Protocol):
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
        """Ответ модели, разобранный в ``output_model``. None = модель недоступна:
        таймаут, ошибка сети или API, отказ (refusal), обрыв по max_tokens, невалидный ответ."""
        ...


class AnthropicLLM:
    def __init__(self, api_key: str | None = None, *, client: anthropic.Anthropic | None = None) -> None:
        self._client = client or anthropic.Anthropic(api_key=api_key)

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
        kwargs: dict[str, Any] = {}
        if thinking_disabled:
            kwargs["thinking"] = {"type": "disabled"}
        try:
            resp = self._client.with_options(timeout=timeout, max_retries=0).messages.parse(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                output_format=output_model,
                output_config={"effort": effort},
                **kwargs,
            )
        except anthropic.APITimeoutError:
            log.warning("LLM %s: таймаут %.1fs", model, timeout)
            return None
        except anthropic.APIConnectionError as exc:
            log.warning("LLM %s: нет соединения: %s", model, exc)
            return None
        except anthropic.RateLimitError:
            log.warning("LLM %s: лимит запросов", model)
            return None
        except anthropic.APIStatusError as exc:
            log.warning("LLM %s: ошибка API %s", model, exc.status_code)
            return None
        except (ValidationError, ValueError, TypeError) as exc:
            log.warning("LLM %s: ответ не разобран: %s", model, exc)
            return None
        if resp.stop_reason != "end_turn":
            # "refusal" (у Haiku 5.5 нет серверного fallback) или "max_tokens": ответ неполный.
            log.warning("LLM %s: stop_reason=%s", model, resp.stop_reason)
            return None
        parsed = resp.parsed_output
        if parsed is None:
            log.warning("LLM %s: пустой structured output", model)
            return None
        return parsed


_clients: dict[str, LLM] = {}


def get_llm(settings: Settings = Depends(get_settings)) -> LLM | None:
    """None, если ключа нет: AI-режим выключен, LLM не вызывается вовсе."""
    if not settings.llm_configured:
        return None
    if settings.LLM_PROVIDER == "ollama":
        from app.ai.ollama import OllamaLLM

        k = f"ollama|{settings.OLLAMA_URL}|{settings.OLLAMA_MODEL}"
        if k not in _clients:
            _clients[k] = OllamaLLM(url=settings.OLLAMA_URL, model=settings.OLLAMA_MODEL)
        return _clients[k]
    key = settings.ANTHROPIC_API_KEY or ""
    if key not in _clients:
        _clients[key] = AnthropicLLM(api_key=key)
    return _clients[key]


class FakeLLM:
    """Для тестов: отдаёт заданные ответы, считает вызовы, хранит промпты.

    ``responses``: словарь «класс модели вывода → ответ». Ответ может быть экземпляром,
    None (недоступно), исключением (будет поднято) или функцией ``(system, messages) -> ...``.
    """

    def __init__(self, responses: dict[type, Any] | None = None) -> None:
        self.responses = dict(responses or {})
        self.calls: list[dict[str, Any]] = []

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
        self.calls.append(
            {
                "model": model,
                "system": system,
                "messages": messages,
                "output_model": output_model,
                "max_tokens": max_tokens,
                "timeout": timeout,
                "effort": effort,
                "thinking_disabled": thinking_disabled,
            }
        )
        resp = self.responses.get(output_model)
        if callable(resp):
            resp = resp(system, messages)
        if isinstance(resp, BaseException):
            raise resp
        return resp

    def calls_for(self, output_model: type) -> list[dict[str, Any]]:
        return [c for c in self.calls if c["output_model"] is output_model]
