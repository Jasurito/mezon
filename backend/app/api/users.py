from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.api import CreateUser, UserOut
from app.services import game
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
