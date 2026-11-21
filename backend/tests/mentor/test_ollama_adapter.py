"""Адаптер Ollama без сети: httpx.MockTransport."""

import json

import httpx
import pytest

from app.ai.llm import get_llm
from app.ai.ollama import OllamaLLM
from app.config import Settings
from app.schemas.rag import MentorAnswer, MentorBlock, QueryClassification
from tests.mentor.helpers import first, names


def make(handler):
    return OllamaLLM("http://ollama:11434", "qwen2.5:7b", client=httpx.Client(transport=httpx.MockTransport(handler)))


def call(llm, model=QueryClassification):
    return llm.structured(
        model="claude-x", system="SYS", messages=[{"role": "user", "content": "q"}],
        output_model=model, max_tokens=256, timeout=5, effort="low", thinking_disabled=True,
    )


def reply(content, status=200):
    return lambda req: httpx.Response(status, json={"message": {"role": "assistant", "content": content}})


def test_success_and_request_shape():
    seen = {}

    def handler(req):
        seen["url"] = str(req.url)
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json={"message": {"content": '{"category": "concept"}'}})

    result = call(make(handler))
    assert result == QueryClassification(category="concept")
    b = seen["body"]
    assert seen["url"] == "http://ollama:11434/api/chat"
    assert b["model"] == "qwen2.5:7b" and b["stream"] is False
    assert b["format"] == QueryClassification.model_json_schema()
    assert b["messages"][0] == {"role": "system", "content": "SYS"}
    assert b["messages"][1]["role"] == "user" and b["options"] == {"temperature": 0, "num_predict": 256}


def test_bad_json_and_schema_mismatch():
    assert call(make(reply("не json"))) is None
    assert call(make(reply('{"category": 123, "x": 1}'))) is None
    assert call(make(reply('{"other": 1}'))) is None


def test_http_500():
    assert call(make(lambda req: httpx.Response(500, text="boom"))) is None


def test_timeout_and_connect_error():
    def timeout(req):
        raise httpx.ReadTimeout("slow", request=req)

    def refused(req):
        raise httpx.ConnectError("refused", request=req)

    assert call(make(timeout)) is None
    assert call(make(refused)) is None


def test_get_llm_selects_provider():
    assert isinstance(get_llm(Settings(LLM_PROVIDER="ollama", ANTHROPIC_API_KEY=None)), OllamaLLM)
    assert get_llm(Settings(LLM_PROVIDER="anthropic", ANTHROPIC_API_KEY=None)) is None
    s = Settings(LLM_PROVIDER="ollama")
    assert s.mentor_timeout == s.OLLAMA_MENTOR_TIMEOUT and s.fast_timeout == s.OLLAMA_FAST_TIMEOUT
    a = Settings(LLM_PROVIDER="anthropic")
    assert a.mentor_timeout == a.LLM_MENTOR_TIMEOUT and a.fast_timeout == a.LLM_FAST_TIMEOUT


@pytest.mark.db
def test_mentor_ask_end_to_end_with_ollama(mentor_client, seeded_db):
    answer = MentorAnswer(
        answer_blocks=[
            MentorBlock(text="Общий смысл правила понятен.", source_ids=[]),
            MentorBlock(text="Покупатель вправе вернуть товар с недостатком.", source_ids=["c1"]),
        ],
        insufficient_sources=False,
    )

    def handler(req):
        body = json.loads(req.content)
        if body["format"] == QueryClassification.model_json_schema():
            content = QueryClassification(category="concept").model_dump_json()
        else:
            content = answer.model_dump_json()
        return httpx.Response(200, json={"message": {"content": content}})

    with mentor_client(llm=make(handler)) as m:
        events = m.ask("Можно ли вернуть товар с недостатком?")
    assert "block" in names(events)
    assert first(events, "done")["ai_unavailable"] is False
