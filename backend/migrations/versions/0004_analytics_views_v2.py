"""analytics views v2: correct_decision_rate, started_at, scenario_id in v_mistakes

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-20
"""
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_mistakes")
    op.execute("DROP VIEW IF EXISTS v_session_metrics")
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
            (s.finished_at IS NOT NULL) AS finished,
            s.started_at,
            s.finished_at,
            (
                SELECT (e.payload->>'correct_decision_rate')::numeric
                FROM events e
                WHERE e.session_id = s.id AND e.type = 'session_finished'
                ORDER BY e.id DESC LIMIT 1
            ) AS correct_decision_rate
        FROM sessions s
        """
    )
    op.execute(
        """
        CREATE VIEW v_mistakes AS
        SELECT
            e.session_id,
            e.user_id,
            s.scenario_id,
            e.payload->>'category' AS category
        FROM events e
        JOIN sessions s ON s.id = e.session_id
        WHERE e.type = 'mistake'
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_mistakes")
    op.execute("DROP VIEW IF EXISTS v_session_metrics")
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
        CREATE VIEW v_mistakes AS
        SELECT
            e.session_id,
            e.user_id,
            e.payload->>'category' AS category
        FROM events e
        WHERE e.type = 'mistake'
        """
    )
