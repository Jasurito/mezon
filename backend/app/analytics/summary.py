"""Сводка по сценарию через SQL-представления."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.i18n import message
from app.scenarios.registry import Registry
from app.schemas.analytics import ScenarioSummary
from app.schemas.legal import Locale


def round_half_up(x: float) -> int:
    return int(x + 0.5)


def scenario_summary(db: Session, registry: Registry, scenario_id: str, locale: Locale) -> ScenarioSummary:
    if scenario_id not in registry:
        raise NotFoundError("Сценарий не найден", details={"scenario_id": scenario_id})
    p = {"sid": scenario_id}
    m = db.execute(
        text(
            """
            SELECT count(*) AS started,
                   count(*) FILTER (WHERE finished) AS done,
                   avg(score) FILTER (WHERE finished) AS avg_score,
                   avg(correct_decision_rate) FILTER (WHERE finished) AS cdr,
                   avg(duration_seconds) FILTER (WHERE finished) AS avg_time
            FROM v_session_metrics WHERE scenario_id = :sid
            """
        ),
        p,
    ).one()
    gain = db.execute(
        text("SELECT avg(delta) FROM v_learning_gain WHERE scenario_id = :sid"), p
    ).scalar_one()
    rows = db.execute(
        text(
            """
            SELECT category, count(*) AS n FROM v_mistakes
            WHERE scenario_id = :sid AND category IS NOT NULL
            GROUP BY category ORDER BY n DESC, category
            """
        ),
        p,
    ).all()
    started = int(m.started)
    return ScenarioSummary(
        sessions_started=started,
        completion_rate=round(int(m.done) / started, 2) if started else None,
        avg_score=round_half_up(float(m.avg_score)) if m.avg_score is not None else None,
        correct_decision_rate=round(float(m.cdr), 2) if m.cdr is not None else None,
        avg_time_sec=round_half_up(float(m.avg_time)) if m.avg_time is not None else None,
        avg_learning_gain=round(float(gain), 2) if gain is not None else None,
        mistakes_by_category={r.category: int(r.n) for r in rows},
        note=message("analytics.summary_note", locale),
    )
