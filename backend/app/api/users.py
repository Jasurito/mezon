import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.deps import require_path_user
from app.db import get_db
from app.errors import NotFoundError
from app.game_engine import IllegalAction, LoggedAction, ScenarioError, SessionFinished, evaluate, replay
from app.i18n import translate
from app.models.app_tables import GameSession, SessionAction, User, UserStats
from app.scenarios.registry import Registry, get_registry
from app.schemas.api import CreateUser, UserOut
from app.schemas.legal import Locale
from app.schemas.users import (
    PatchUser,
    UserProfileOut,
    UserSessionItem,
    UserSessionsOut,
    UserStatsOut,
)
from app.services import game, presenter
from app.services.clock import get_now

router = APIRouter(tags=["users"])


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: CreateUser | None = None,
    db: Session = Depends(get_db),
    now: datetime = Depends(get_now),
) -> UserOut:
    """Создать пользователя без авторизации; фронт хранит user_id в localStorage."""
    user = game.create_user(db, body.display_name if body else None, now)
    return UserOut(user_id=user.id, display_name=user.display_name, created_at=user.created_at)


def _get_user(db: Session, user_id: uuid.UUID) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден", details={"user_id": str(user_id)})
    return user


def _profile(db: Session, user: User) -> UserProfileOut:
    row = db.get(UserStats, user.id)
    stats = UserStatsOut.model_validate(row, from_attributes=True) if row is not None else UserStatsOut()
    return UserProfileOut(
        user_id=user.id,
        display_name=user.display_name,
        preferred_locale=user.preferred_locale,  # type: ignore[arg-type]
        created_at=user.created_at,
        stats=stats,
        audience=user.audience,  # type: ignore[arg-type]
    )


@router.get("/users/{user_id}", response_model=UserProfileOut, dependencies=[Depends(require_path_user)])
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> UserProfileOut:
    """Профиль и статистика игрока."""
    return _profile(db, _get_user(db, user_id))


@router.patch("/users/{user_id}", response_model=UserProfileOut, dependencies=[Depends(require_path_user)])
def patch_user(user_id: uuid.UUID, body: PatchUser, db: Session = Depends(get_db)) -> UserProfileOut:
    """Изменить имя, язык по умолчанию и/или audience; переданные поля заменяются, null очищает."""
    user = _get_user(db, user_id)
    if "display_name" in body.model_fields_set:
        user.display_name = body.display_name
    if "preferred_locale" in body.model_fields_set:
        user.preferred_locale = body.preferred_locale
    if "audience" in body.model_fields_set:
        user.audience = body.audience
    db.commit()
    return _profile(db, user)


def _outcome_title(loaded, log: list[SessionAction], locale: Locale) -> str | None:
    try:
        state, _ = replay(loaded.scenario, [LoggedAction(action_id=a.action_id, params=a.params) for a in log])
        if not state.finished:
            return None
        return translate(loaded, evaluate(loaded.scenario, state).title_key, locale)
    except (IllegalAction, SessionFinished, ScenarioError):
        return None


@router.get(
    "/users/{user_id}/sessions", response_model=UserSessionsOut, dependencies=[Depends(require_path_user)]
)
def get_user_sessions(
    user_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Literal["all", "finished", "active"] = "all",
    locale: Locale | None = None,
    db: Session = Depends(get_db),
    registry: Registry = Depends(get_registry),
) -> UserSessionsOut:
    """Игры пользователя, новые сверху."""
    user = _get_user(db, user_id)
    where = [GameSession.user_id == user_id]
    if status == "finished":
        where.append(GameSession.finished_at.is_not(None))
    elif status == "active":
        where.append(GameSession.finished_at.is_(None))
    total = db.execute(select(func.count()).select_from(GameSession).where(*where)).scalar_one()
    rows = list(
        db.execute(
            select(GameSession)
            .where(*where)
            .order_by(GameSession.started_at.desc(), GameSession.id)
            .limit(limit)
            .offset(offset)
        ).scalars()
    )
    ids = [s.id for s in rows]
    logs: dict[uuid.UUID, list[SessionAction]] = {i: [] for i in ids}
    if ids:
        for a in db.execute(
            select(SessionAction).where(SessionAction.session_id.in_(ids)).order_by(SessionAction.seq)
        ).scalars():
            logs[a.session_id].append(a)

    items: list[UserSessionItem] = []
    for s in rows:
        loc: Locale = locale or user.preferred_locale or s.locale  # type: ignore[assignment]
        loaded = registry.get(s.scenario_id)
        title = presenter.build_scenario_card(loaded, loc).title if loaded else None
        outcome_title = _outcome_title(loaded, logs[s.id], loc) if loaded and s.finished_at else None
        items.append(
            UserSessionItem(
                session_id=s.id,
                scenario_id=s.scenario_id,
                title=title,
                started_at=s.started_at,
                finished_at=s.finished_at,
                outcome=s.outcome,
                outcome_title=outcome_title,
                score=s.score,
                max_score=loaded.scenario.max_score if loaded else None,
                steps=len(logs[s.id]),
            )
        )
    return UserSessionsOut(items=items, total=total, limit=limit, offset=offset)
