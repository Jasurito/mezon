"""drop users.audience: Mezon is for everyone, no lawyer / non-lawyer split (added in 0007 the same day)

Revision ID: 0008
Revises: 0007
Create Date: 2026-11-21
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_users_audience", "users", type_="check")
    op.drop_column("users", "audience")


def downgrade() -> None:
    op.add_column("users", sa.Column("audience", sa.Text))
    op.create_check_constraint("ck_users_audience", "users", "audience IN ('professional', 'public')")
