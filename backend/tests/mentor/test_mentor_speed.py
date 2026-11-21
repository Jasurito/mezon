"""Ускорение наставника: правила вместо LLM-классификации, лимит источников, длина генерации."""

import json

import httpx
import pytest

from app.ai.classify import classify_by_rules
from app.ai.llm import FakeLLM
from app.ai.ollama import OllamaLLM
from app.config import Settings
from app.models.app_tables import Event
from app.schemas.rag import MentorAnswer, MentorBlock, QueryClassification
from sqlalchemy import select
from tests.mentor.helpers import first


@pytest.mark.parametrize(
    "question,has_session,expected",
    [
        ("Что говорит ст. 15 ГК?", False, "article_lookup"),
        ("15-modda nima haqida?", True, "article_lookup"),
        ("Почему суд отказал, я проиграл дело?", True, "case_specific"),
        ("Nega sud mening daʼvomni rad etdi?", True, "case_specific"),
        ("Men yutqazdim, nima qilish kerak?", True, "case_specific"),
        ("Почему суд отказал, я проиграл дело?", False, "concept"),
        ("Что такое встречный иск?", True, "concept"),
        ("Можно ли вернуть товар с недостатком?", False, "concept"),
    ],
)
def test_rules_classifier(question, has_session, expected):
    assert classify_by_rules(question, has_session) == expected


def answer():
    return MentorAnswer(
        answer_blocks=[MentorBlock(text="Покупатель вправе вернуть товар.", source_ids=["c1"])],
        insufficient_sources=False,
    )


@pytest.mark.db
def test_rules_mode_makes_single_llm_call(mentor_client, seeded_db):
    llm = FakeLLM({QueryClassification: QueryClassification(category="out_of_scope"), MentorAnswer: answer()})
    with mentor_client(llm=llm, MENTOR_CLASSIFIER="rules") as m:
        events = m.ask("Можно ли вернуть товар с недостатком?")
    assert len(llm.calls) == 1 and llm.calls_for(MentorAnswer)
    assert first(events, "done")["ai_unavailable"] is False
    row = list(seeded_db.scalars(select(Event).where(Event.type == "mentor_question")))[-1]
    assert row.payload["category"] == "concept"


@pytest.mark.db
def test_mentor_max_sources_limits_sources(mentor_client):
    llm = FakeLLM({MentorAnswer: answer()})
    with mentor_client(llm=llm, MENTOR_CLASSIFIER="rules", MENTOR_MAX_SOURCES=1) as m:
        events = m.ask("Можно ли вернуть товар с недостатком?")
    assert len(first(events, "sources")) == 1


def test_defaults():
    s = Settings()
    assert s.MENTOR_CLASSIFIER == "rules" and s.MENTOR_MAX_SOURCES == 5


def test_ollama_num_predict_from_max_tokens():
    seen = {}

    def handler(req):
        seen["body"] = json.loads(req.content)
        return httpx.Response(200, json={"message": {"content": '{"category": "concept"}'}})

    llm = OllamaLLM("http://o:1", "m", client=httpx.Client(transport=httpx.MockTransport(handler)))
    llm.structured(model="x", system="s", messages=[], output_model=QueryClassification,
                   max_tokens=700, timeout=5, effort="low")
    assert seen["body"]["options"]["num_predict"] == 700
