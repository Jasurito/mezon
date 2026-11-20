"""analytics views

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-20
"""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE VIEW v_session_metrics AS
        SELECT
            s.id AS session_id,
            s.user_id,
            s.scenario_id,
            s.score,
            s.outcome,
            EXTRACT(EPOCH FROM (s.finished_at - s.started_at))::int AS duration_seconds,
            (s.finished_at IS NOT NULL) AS finished
        FROM sessions s
        """
    )
    op.execute(
        """
        CREATE VIEW v_learning_gain AS
        WITH last_pre AS (
            SELECT DISTINCT ON (user_id, scenario_id) user_id, scenario_id, score, max_score
            FROM quiz_attempts WHERE kind = 'pre'
            ORDER BY user_id, scenario_id, ts DESC, id DESC
        ),
        last_post AS (
            SELECT DISTINCT ON (user_id, scenario_id) user_id, scenario_id, score, max_score
            FROM quiz_attempts WHERE kind = 'post'
            ORDER BY user_id, scenario_id, ts DESC, id DESC
        )
        SELECT
            pre.user_id,
            pre.scenario_id,
            pre.score AS pre_score,
            post.score AS post_score,
            pre.max_score,
            post.score - pre.score AS delta
        FROM last_pre pre
        JOIN last_post post USING (user_id, scenario_id)
        """
    )
    op.execute(
        """
        CREATE VIEW v_mistakes AS
        SELECT
            e.session_id,
            e.user_id,
            e.payload->>'category' AS category
        FROM events e
        WHERE e.type = 'mistake'
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_mistakes")
    op.execute("DROP VIEW IF EXISTS v_learning_gain")
    op.execute("DROP VIEW IF EXISTS v_session_metrics")
