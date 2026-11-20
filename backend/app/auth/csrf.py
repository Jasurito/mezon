"""CSRF: проверка Origin (или Referer) для небезопасных методов.

Cookie сессии SameSite=Lax уже не уходит на кросс-сайтовые POST; Origin-проверка — вторая линия.
Для /api/auth/* проверка обязательна всегда, для остальных — когда в запросе есть cookie сессии.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import Depends, Request

from app.auth.sessions import COOKIE_NAME
from app.config import Settings, get_settings
from app.errors import CsrfError

UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def origin_of(url: str | None) -> str | None:
    if not url:
        return None
    try:
        p = urlsplit(url.strip())
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.netloc:
        return None
    return f"{p.scheme}://{p.netloc}".lower()


def allowed_origins(settings: Settings) -> set[str]:
    origins = {o for o in (origin_of(x) for x in settings.CORS_ORIGINS) if o}
    base = origin_of(settings.PUBLIC_BASE_URL)
    if base:
        origins.add(base)
    return origins


def csrf_guard(request: Request, settings: Settings = Depends(get_settings)) -> None:
    if request.method not in UNSAFE_METHODS:
        return
    is_auth = request.url.path.startswith("/api/auth/")
    if not is_auth and COOKIE_NAME not in request.cookies:
        return
    origin = request.headers.get("origin")
    candidate = origin_of(origin) if origin is not None else origin_of(request.headers.get("referer"))
    if candidate is None or candidate not in allowed_origins(settings):
        raise CsrfError()
