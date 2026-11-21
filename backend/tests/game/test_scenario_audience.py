"""Карточка дела говорит, для кого оно: professional (суд) или public (жизненная ситуация)."""

import pytest

from tests.game.conftest import SCENARIO_ID

pytestmark = pytest.mark.db


def test_audience_defaults_to_professional(api, seeded_db):
    cards = api.c.get("/api/scenarios", params={"locale": "ru"}).json()
    card = next(c for c in cards if c["scenario_id"] == SCENARIO_ID)
    assert card["audience"] == "professional"  # old scenario JSON without the field
    detail = api.c.get(f"/api/scenarios/{SCENARIO_ID}", params={"locale": "ru"}).json()
    assert detail["audience"] == "professional"
