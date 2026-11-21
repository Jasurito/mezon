"""users.audience: lawyer / law student or not a legal professional

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-21
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("audience", sa.Text))  # NULL = not specified (all existing users)
    op.create_check_constraint("ck_users_audience", "users", "audience IN ('professional', 'public')")


def downgrade() -> None:
    op.drop_constraint("ck_users_audience", "users", type_="check")
    op.drop_column("users", "audience")
