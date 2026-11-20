"""user_stats and users.preferred_locale

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-20
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def _int(name: str) -> sa.Column:
    return sa.Column(name, sa.Integer, nullable=False, server_default="0")


def upgrade() -> None:
    op.add_column("users", sa.Column("preferred_locale", sa.Text))
    op.create_table(
        "user_stats",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        _int("sessions_started"),
        _int("sessions_finished"),
        _int("total_score"),
        _int("best_score"),
        _int("total_time_sec"),
        _int("quizzes_taken"),
        sa.Column("last_active_at", sa.DateTime(timezone=True)),
        _int("active_days"),
        _int("streak_days"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_stats")
    op.drop_column("users", "preferred_locale")
