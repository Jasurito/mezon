import pytest
from alembic import command
from sqlalchemy import inspect

pytestmark = pytest.mark.db

TABLES = {
    "users", "sessions", "session_actions", "events", "quiz_attempts",
    "legal_documents", "document_versions", "articles", "article_parts", "chunks", "citations",
}
VIEWS = {"v_session_metrics", "v_learning_gain", "v_mistakes"}


def test_upgrade_creates_everything(db_engine):
    insp = inspect(db_engine)
    assert TABLES <= set(insp.get_table_names())
    assert VIEWS <= set(insp.get_view_names())


def test_downgrade_and_upgrade_again(db_engine, alembic_config):
    command.downgrade(alembic_config, "base")
    insp = inspect(db_engine)
    assert not (TABLES & set(insp.get_table_names()))
    assert not (VIEWS & set(insp.get_view_names()))
    command.upgrade(alembic_config, "head")
    insp = inspect(db_engine)
    assert TABLES <= set(insp.get_table_names())
    assert VIEWS <= set(insp.get_view_names())
