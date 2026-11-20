"""Защита от выдуманных статей: до пользователя доходят только проверенные блоки."""

import pytest
from sqlalchemy import select

from app.ai.llm import FakeLLM
from app.models.app_tables import Event
from app.schemas.rag import MentorAnswer, MentorBlock, QueryClassification
from tests.mentor.helpers import first, names

pytestmark = pytest.mark.db

QUESTION = "Можно ли вернуть товар с недостатком?"


def concept():
    return QueryClassification(category="concept")


def mentor_events(db):
    return [e.payload for e in db.scalars(select(Event).where(Event.type == "mentor_question"))]


def test_only_valid_block_passes(mentor_client, seeded_db):
    llm = FakeLLM(
        {
            QueryClassification: concept(),
            MentorAnswer: MentorAnswer(
                answer_blocks=[
                    MentorBlock(text="Выдуманный источник.", source_ids=["c99"]),
                    MentorBlock(text="Согласно ст. 999 покупатель всегда прав.", source_ids=["c1"]),
                    MentorBlock(text="Это закреплено в статье 10.", source_ids=[]),
                    MentorBlock(text="Покупатель вправе вернуть товар с существенным недостатком.", source_ids=["c1"]),
                ],
                insufficient_sources=False,
            ),
        }
    )
    with mentor_client(llm=llm) as m:
        events = m.ask(QUESTION)

    assert names(events) == ["sources", "block", "done"]
    block = first(events, "block")
    assert block == {
        "text": "Покупатель вправе вернуть товар с существенным недостатком.",
        "source_ids": ["c1"],
        "verified": True,
    }
    done = first(events, "done")
    assert done["insufficient_sources"] is False and done["ai_unavailable"] is False
    assert done["disclaimer"]

    (payload,) = mentor_events(seeded_db)
    assert payload["blocks_kept"] == 1 and payload["blocks_dropped"] == 3


def test_general_block_without_sources_is_allowed(mentor_client):
    llm = FakeLLM(
        {
            QueryClassification: concept(),
            MentorAnswer: MentorAnswer(
                answer_blocks=[
                    MentorBlock(text="Сначала важно понять, в чём именно недостаток.", source_ids=[]),
                    MentorBlock(text="Статья 10 даёт право вернуть товар.", source_ids=["c1"]),
                ],
                insufficient_sources=False,
            ),
        }
    )
    with mentor_client(llm=llm) as m:
        events = m.ask(QUESTION)
    blocks = [d for n, d in events if n == "block"]
    assert [b["source_ids"] for b in blocks] == [[], ["c1"]]
    assert all(b["verified"] for b in blocks)


def test_all_blocks_dropped_means_insufficient(mentor_client, seeded_db):
    llm = FakeLLM(
        {
            QueryClassification: concept(),
            MentorAnswer: MentorAnswer(
                answer_blocks=[MentorBlock(text="По статье 77 всё иначе.", source_ids=["c1"])],
                insufficient_sources=False,
            ),
        }
    )
    with mentor_client(llm=llm) as m:
        events = m.ask(QUESTION)
    assert names(events) == ["sources", "done"]
    assert first(events, "done")["insufficient_sources"] is True
    (payload,) = mentor_events(seeded_db)
    assert payload["blocks_dropped"] == 1 and payload["insufficient"] is True


def test_model_may_declare_insufficient_sources(mentor_client):
    llm = FakeLLM(
        {
            QueryClassification: concept(),
            MentorAnswer: MentorAnswer(answer_blocks=[], insufficient_sources=True),
        }
    )
    with mentor_client(llm=llm) as m:
        events = m.ask(QUESTION)
    done = first(events, "done")
    assert done["insufficient_sources"] is True and done["ai_unavailable"] is False
    assert done["message"].startswith("В загруженной правовой базе недостаточно")


def test_inline_source_marks_are_stripped():
    from app.rag.validate import strip_source_marks

    assert strip_source_marks("Продавец устраняет недостаток. [c1]") == "Продавец устраняет недостаток."
    assert strip_source_marks("Текст [c1, c2] дальше") == "Текст дальше"
    assert strip_source_marks("ст. 10 [не ссылка]") == "ст. 10 [не ссылка]"
