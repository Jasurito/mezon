"""Ограничение перебора в базе: неудачные входы по email и auth-запросы по IP."""

from __future__ import annotations

import hashlib
import ipaddress
import math
from datetime import datetime, timedelta

from fastapi import Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import RateLimitedError
from app.models.auth import AuthAttempt

REQUEST = "request"
LOGIN_FAIL = "login_fail"


def email_hash(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()


def client_ip(request: Request, settings: Settings) -> str | None:
    """IP клиента. X-Forwarded-For только при TRUST_PROXY_HEADERS: берём правый элемент (его дописал наш nginx)."""
    if settings.TRUST_PROXY_HEADERS:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            last = xff.split(",")[-1].strip()
            try:
                return str(ipaddress.ip_address(last))
            except ValueError:
                pass
    return request.client.host if request.client else None


def _retry_after(db: Session, where, count: int, limit: int, now: datetime, window: timedelta) -> int:
    ts = db.execute(select(AuthAttempt.ts).where(*where).order_by(AuthAttempt.ts).offset(count - limit).limit(1)).scalar()
    wait = (ts + window - now).total_seconds() if ts else window.total_seconds()
    return max(1, math.ceil(wait))


def check(db: Session, settings: Settings, now: datetime, ip: str | None, email_h: str | None) -> None:
    """429 с Retry-After, если лимит исчерпан. Ничего не записывает."""
    window = timedelta(minutes=settings.AUTH_WINDOW_MINUTES)
    since = now - window
    limits = []
    if ip is not None:
        limits.append(
            ([AuthAttempt.kind == REQUEST, AuthAttempt.ip == ip, AuthAttempt.ts > since], settings.AUTH_IP_MAX_REQUESTS)
        )
    if email_h is not None:
        limits.append(
            (
                [AuthAttempt.kind == LOGIN_FAIL, AuthAttempt.email_hash == email_h, AuthAttempt.ts > since],
                settings.AUTH_LOGIN_MAX_FAILS,
            )
        )
    for where, limit in limits:
        count = db.execute(select(func.count()).select_from(AuthAttempt).where(*where)).scalar_one()
        if count >= limit:
            retry = _retry_after(db, where, count, limit, now, window)
            raise RateLimitedError(details={"retry_after": retry}, headers={"Retry-After": str(retry)})


def record_request(db: Session, ip: str | None, now: datetime) -> None:
    db.execute(delete(AuthAttempt).where(AuthAttempt.ts < now - timedelta(days=1)))  # уборка старого
    db.add(AuthAttempt(kind=REQUEST, ip=ip, ts=now))
    db.commit()


def record_failure(db: Session, email_h: str, ip: str | None, now: datetime) -> None:
    db.add(AuthAttempt(kind=LOGIN_FAIL, email_hash=email_h, ip=ip, ts=now))
    db.commit()


def clear_failures(db: Session, email_h: str) -> None:
    db.execute(delete(AuthAttempt).where(AuthAttempt.kind == LOGIN_FAIL, AuthAttempt.email_hash == email_h))
