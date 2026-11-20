"""accounts: users auth columns, auth_sessions, auth_attempts, oauth_states

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-21
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.Text))
    op.add_column("users", sa.Column("email_verified", sa.Boolean, nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("password_hash", sa.Text))
    op.add_column("users", sa.Column("google_sub", sa.Text))
    op.add_column("users", sa.Column("avatar_url", sa.Text))
    op.add_column("users", sa.Column("merged_into", UUID, sa.ForeignKey("users.id")))
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.create_unique_constraint("uq_users_google_sub", "users", ["google_sub"])

    op.create_table(
        "auth_sessions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("user_agent", sa.Text),
        sa.Column("ip", sa.Text),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])

    op.create_table(
        "auth_attempts",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("email_hash", sa.Text),
        sa.Column("ip", sa.Text),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_attempts_email", "auth_attempts", ["kind", "email_hash", "ts"])
    op.create_index("ix_auth_attempts_ip", "auth_attempts", ["kind", "ip", "ts"])

    op.create_table(
        "oauth_states",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("state_hash", sa.Text, nullable=False, unique=True),
        sa.Column("bind_hash", sa.Text, nullable=False),
        sa.Column("code_verifier", sa.Text, nullable=False),
        sa.Column("nonce", sa.Text, nullable=False),
        sa.Column("next_path", sa.Text, nullable=False),
        sa.Column("guest_user_id", UUID),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_oauth_states_expires_at", "oauth_states", ["expires_at"])


def downgrade() -> None:
    op.drop_table("oauth_states")
    op.drop_table("auth_attempts")
    op.drop_table("auth_sessions")
    op.drop_constraint("uq_users_google_sub", "users", type_="unique")
    op.drop_constraint("uq_users_email", "users", type_="unique")
    for col in ("merged_into", "avatar_url", "google_sub", "password_hash", "email_verified", "email"):
        op.drop_column("users", col)
