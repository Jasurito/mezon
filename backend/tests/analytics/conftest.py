"""Фикстуры аналитики: переиспользуют игровые (сценарий test_consumer, часы, база)."""

from __future__ import annotations

import pytest

from tests.game.conftest import make_client, game_client, api, seeded_db, clock  # noqa: F401

pytestmark = pytest.mark.db
