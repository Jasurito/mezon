"""Дашборд пользователя."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics.summary import round_half_up
from app.errors import NotFoundError
from app.i18n import message, translate
from app.i18n.messages import MESSAGES
from app.models.app_tables import Event, GameSession, QuizAttempt, User
from app.scenarios.registry import Registry
from app.schemas.analytics import (
    CompletedSession,
    DashboardLearningGain,
    DashboardOut,
    DashboardUser,
    FocusTopic,
    KnowledgeLevel,
    MistakeCategoryOut,
    RecommendedScenario,
)
from app.schemas.legal import Locale
from app.services import presenter


def _level_label(score: int | None, locale: Locale) -> str:
    if score is None:
        return message("dashboard.level.none", locale)
    if score < 40:
        return message("dashboard.level.beginner", locale)
    if score < 70:
        return message("dashboard.level.confident", locale)
    return message("dashboard.level.advanced", locale)


def _category_title(category: str, locale: Locale) -> str:
    key = f"mistake_category.{category}"
    return message(key, locale) if key in MESSAGES else category


def _latest_attempts(db: Session, user_id: uuid.UUID, kind: str) -> dict[str, QuizAttempt]:
    rows = db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id, QuizAttempt.kind == kind)
        .order_by(QuizAttempt.ts, QuizAttempt.id)
    ).scalars()
    return {r.scenario_id: r for r in rows}  # последняя попытка перезаписывает предыдущие


def build_dashboard(db: Session, registry: Registry, user_id: uuid.UUID, locale: Locale) -> DashboardOut:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден", details={"user_id": str(user_id)})

    sessions = list(
        db.execute(
            select(GameSession).where(GameSession.user_id == user_id).order_by(GameSession.started_at, GameSession.id)
        ).scalars()
    )
    finished = sorted(
        (s for s in sessions if s.finished_at is not None),
        key=lambda s: (s.finished_at, s.started_at),
        reverse=True,
    )

    # --- завершённые игры
    completed: list[CompletedSession] = []
    for s in finished:
        loaded = registry.get(s.scenario_id)
        if loaded is None:
            continue
        rule = next((r for r in loaded.scenario.evaluation_rules if r.outcome == s.outcome), None)
        completed.append(
            CompletedSession(
                session_id=s.id,
                scenario_id=s.scenario_id,
                title=translate(loaded, loaded.scenario.card.title_key, locale),
                outcome=s.outcome,
                outcome_title=translate(loaded, rule.title_key, locale) if rule else (s.outcome or ""),
                score=s.score or 0,
                max_score=loaded.scenario.max_score,
                finished_at=s.finished_at,  # type: ignore[arg-type]
            )
        )

    # --- прирост знаний
    pre = _latest_attempts(db, user_id, "pre")
    post = _latest_attempts(db, user_id, "post")
    note = message("quiz.learning_gain_note", locale)
    gains = []
    for sid in sorted(set(pre) | set(post)):
        ref = post.get(sid) or pre[sid]
        gains.append(
            DashboardLearningGain(
                scenario_id=sid,
                pre=pre[sid].score if sid in pre else None,
                post=post[sid].score if sid in post else None,
                max=ref.max_score,
                note=note,
            )
        )

    # --- уровень знаний
    norm = [c.score / c.max_score * 100 for c in completed if c.max_score > 0]
    post_all = db.execute(
        select(QuizAttempt.score, QuizAttempt.max_score).where(
            QuizAttempt.user_id == user_id, QuizAttempt.kind == "post"
        )
    ).all()
    norm += [sc / mx * 100 for sc, mx in post_all if mx > 0]
    level = round_half_up(sum(norm) / len(norm)) if norm else None

    # --- категории ошибок
    cat_col = Event.payload["category"].astext.label("category")
    rows = db.execute(
        select(cat_col, func.count())
        .where(Event.user_id == user_id, Event.type == "mistake")
        .group_by(cat_col)
    ).all()
    counts = sorted(((c, n) for c, n in rows if c), key=lambda r: (-r[1], r[0]))
    mistake_categories = [
        MistakeCategoryOut(category=c, title=_category_title(c, locale), count=n) for c, n in counts
    ]

    # --- рекомендации
    done_ids = {s.scenario_id for s in finished}
    started_ids = {s.scenario_id for s in sessions}
    recommended: list[RecommendedScenario] = []
    for sid, loaded in registry.items():
        if sid in done_ids:
            continue
        card = presenter.build_scenario_card(loaded, locale)
        if not card.available:
            reason = "dashboard.reason.soon"
        elif sid in started_ids:
            reason = "dashboard.reason.unfinished"
        else:
            reason = "dashboard.reason.new"
        recommended.append(
            RecommendedScenario(
                scenario_id=sid,
                title=card.title,
                category=card.category,
                difficulty=card.difficulty,
                minutes=card.minutes,
                topics=card.topics,
                available=card.available,
                reason=message(reason, locale),
            )
        )

    focus: list[FocusTopic] = []
    played = sorted(started_ids)
    for category, _ in counts[:3]:
        for sid in played:
            loaded = registry.get(sid)
            rec = loaded.scenario.recommendations.get(category) if loaded else None
            if loaded is None or rec is None:
                continue
            focus.append(
                FocusTopic(
                    category=category,
                    topic=translate(loaded, rec.topic_key, locale),
                    citation_ids=list(rec.citation_ids),
                    scenario_id=rec.scenario_id,
                )
            )

    return DashboardOut(
        user=DashboardUser(user_id=user.id, display_name=user.display_name),
        knowledge_level=KnowledgeLevel(score=level, label=_level_label(level, locale)),
        completed=completed,
        learning_gain=gains,
        mistake_categories=mistake_categories,
        recommended=recommended,
        focus_topics=focus,
    )

