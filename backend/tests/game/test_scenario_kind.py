"""Категория дела: court (судебное дело) или situation (жизненная ситуация), для всех пользователей."""

import pytest

from app.schemas.scenario import Card
from tests.game.conftest import SCENARIO_ID

pytestmark = pytest.mark.db


def test_kind_defaults_to_court(api, seeded_db):
    cards = api.c.get("/api/scenarios", params={"locale": "ru"}).json()
    card = next(c for c in cards if c["scenario_id"] == SCENARIO_ID)
    assert card["kind"] == "court" and "audience" not in card
    detail = api.c.get(f"/api/scenarios/{SCENARIO_ID}", params={"locale": "ru"}).json()
    assert detail["kind"] == "court"


@pytest.mark.parametrize("audience,kind", [("public", "situation"), ("professional", "court")])
def test_legacy_audience_key_is_read_as_kind(audience, kind):
    base = {"title_key": "t", "category_key": "c", "difficulty": "beginner", "minutes": 5, "topic_keys": []}
    assert Card.model_validate({**base, "audience": audience}).kind == kind
    assert Card.model_validate({**base, "kind": "situation"}).kind == "situation"
