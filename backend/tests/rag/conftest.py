"""Фикстуры поиска: тестовый корпус с чанками, клиент из игровых тестов."""

from __future__ import annotations

import pytest

from tests.fixtures.legal_seed import seed_test_legal_data
from tests.fixtures.rag_seed import seed_test_chunks
from tests.game.conftest import Clock, clock, make_client  # noqa: F401  (переиспользуются)


@pytest.fixture
def seeded_db(db_session):
    seed_test_legal_data(db_session)
    seed_test_chunks(db_session)
    return db_session
