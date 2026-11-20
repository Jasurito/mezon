"""Квиз до и после игры."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AppError, NotFoundError
from app.i18n import message, translate
from app.models.app_tables import Event, QuizAttempt, User
from app.scenarios.loader import LoadedScenario
from app.scenarios.registry import Registry
from app.schemas.analytics import (
    LearningGainOut,
    QuizAttemptIn,
    QuizAttemptOut,
    QuizKind,
    QuizOut,
    QuizOptionOut,
    QuizQuestionOut,
    QuizReviewItem,
)
from app.schemas.legal import Locale
from app.schemas.quiz import Question


def _quiz_questions(registry: Registry, scenario_id: str, kind: QuizKind) -> tuple[LoadedScenario, list[Question]]:
    loaded = registry.get(scenario_id)
    if loaded is None:
        raise NotFoundError("Сценарий не найден", details={"scenario_id": scenario_id})
    if loaded.quiz is None:
        raise NotFoundError("У сценария нет теста", details={"scenario_id": scenario_id})
    return loaded, (loaded.quiz.pre if kind == "pre" else loaded.quiz.post)


def get_quiz(registry: Registry, scenario_id: str, kind: QuizKind, locale: Locale) -> QuizOut:
    loaded, questions = _quiz_questions(registry, scenario_id, kind)
    return QuizOut(
        scenario_id=scenario_id,
        kind=kind,
        questions=[
            QuizQuestionOut(
                question_id=q.question_id,
                text=translate(loaded, q.text_key, locale),
                options=[QuizOptionOut(id=o.id, text=translate(loaded, o.text_key, locale)) for o in q.options],
            )
            for q in questions
        ],
        total=len(questions),
    )


def submit_attempt(
    db: Session,
    registry: Registry,
    scenario_id: str,
    body: QuizAttemptIn,
    locale: Locale,
    now: datetime,
) -> QuizAttemptOut:
    loaded, questions = _quiz_questions(registry, scenario_id, body.kind)
    if db.get(User, body.user_id) is None:
        raise NotFoundError("Пользователь не найден", details={"user_id": str(body.user_id)})
    known = {q.question_id for q in questions}
    unknown = sorted(set(body.answers) - known)
    if unknown:
        raise AppError(
            "Неизвестный вопрос в ответах",
            code="VALIDATION_ERROR",
            http_status=422,
            details={"unknown_question_ids": unknown},
        )

    review: list[QuizReviewItem] = []
    for q in questions:
        chosen = body.answers.get(q.question_id)
        review.append(
            QuizReviewItem(
                question_id=q.question_id,
                chosen_option=chosen,
                correct=chosen == q.correct_option,
                correct_option=q.correct_option,
                explanation=translate(loaded, q.explanation_key, locale),
                citation_ids=list(q.citation_ids),
            )
        )
    score = sum(r.correct for r in review)
    max_score = len(questions)

    gain: LearningGainOut | None = None
    if body.kind == "post":
        pre = db.execute(
            select(QuizAttempt)
            .where(
                QuizAttempt.user_id == body.user_id,
                QuizAttempt.scenario_id == scenario_id,
                QuizAttempt.kind == "pre",
            )
            .order_by(QuizAttempt.ts.desc(), QuizAttempt.id.desc())
            .limit(1)
        ).scalar_one_or_none()
        if pre is not None:
            gain = LearningGainOut(
                pre=pre.score,
                post=score,
                max=max_score,
                delta=score - pre.score,
                note=message("quiz.learning_gain_note", locale),
            )

    attempt = QuizAttempt(
        user_id=body.user_id,
        scenario_id=scenario_id,
        kind=body.kind,
        answers=body.answers,
        score=score,
        max_score=max_score,
        ts=now,
    )
    db.add(attempt)
    db.add(
        Event(
            user_id=body.user_id,
            type="quiz_attempt",
            payload={"scenario_id": scenario_id, "kind": body.kind, "score": score, "max": max_score},
            ts=now,
        )
    )
    db.commit()
    return QuizAttemptOut(attempt_id=attempt.id, score=score, max=max_score, review=review, learning_gain=gain)

