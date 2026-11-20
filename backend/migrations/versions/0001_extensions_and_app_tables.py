"""extensions and app tables

Revision ID: 0001
Revises:
Create Date: 2026-11-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("display_name", sa.Text),
        sa.Column("group_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scenario_id", sa.Text, nullable=False),
        sa.Column("scenario_version", sa.Text, nullable=False),
        sa.Column("locale", sa.Text, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("outcome", sa.Text),
        sa.Column("score", sa.Integer),
    )
    op.create_table(
        "session_actions",
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("seq", sa.Integer, nullable=False),
        sa.Column("action_id", sa.Text, nullable=False),
        sa.Column("params", postgresql.JSONB),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("session_id", "seq"),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True)),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_events_session_id", "events", ["session_id"])
    op.create_index("ix_events_type", "events", ["type"])
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("scenario_id", sa.Text, nullable=False),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("answers", postgresql.JSONB, nullable=False),
        sa.Column("score", sa.Integer, nullable=False),
        sa.Column("max_score", sa.Integer, nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("kind IN ('pre', 'post')", name="ck_quiz_attempts_kind"),
    )


def downgrade() -> None:
    op.drop_table("quiz_attempts")
    op.drop_index("ix_events_type", table_name="events")
    op.drop_index("ix_events_session_id", table_name="events")
    op.drop_table("events")
    op.drop_table("session_actions")
    op.drop_table("sessions")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
    op.execute("DROP EXTENSION IF EXISTS vector")
