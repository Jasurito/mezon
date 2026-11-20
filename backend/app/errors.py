from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    code = "INTERNAL_ERROR"
    http_status = 500
    default_message = "Внутренняя ошибка сервера"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
        code: str | None = None,
        http_status: int | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.headers = headers
        self.message = message or self.default_message
        self.details = details or {}
        if code is not None:
            self.code = code
        if http_status is not None:
            self.http_status = http_status
        super().__init__(self.message)


class NotFoundError(AppError):
    code = "NOT_FOUND"
    http_status = 404
    default_message = "Объект не найден"


class IllegalActionError(AppError):
    code = "ILLEGAL_ACTION"
    http_status = 409
    default_message = "Действие недоступно на этом этапе"


class SessionFinishedError(AppError):
    code = "SESSION_FINISHED"
    http_status = 409
    default_message = "Дело уже завершено"


class SessionNotFinishedError(AppError):
    code = "SESSION_NOT_FINISHED"
    http_status = 409
    default_message = "Дело ещё не завершено"


class SessionOutdatedError(AppError):
    """The session's action log no longer replays on the current scenario version."""

    code = "SESSION_OUTDATED"
    http_status = 409
    default_message = "Сценарий обновился, это дело нужно начать заново"


class UnauthorizedError(AppError):
    code = "UNAUTHORIZED"
    http_status = 401
    default_message = "Нужно войти в аккаунт"


class InvalidCredentialsError(AppError):
    code = "INVALID_CREDENTIALS"
    http_status = 401
    default_message = "Неверный email или пароль"


class ForbiddenError(AppError):
    code = "FORBIDDEN"
    http_status = 403
    default_message = "Нет доступа к этому аккаунту"


class CsrfError(AppError):
    code = "CSRF_FAILED"
    http_status = 403
    default_message = "Запрос отклонён: недопустимый источник"


class EmailExistsError(AppError):
    code = "EMAIL_EXISTS"
    http_status = 409
    default_message = "Этот email уже зарегистрирован"


class RateLimitedError(AppError):
    code = "RATE_LIMITED"
    http_status = 429
    default_message = "Слишком много попыток, попробуйте позже"


class AuthProviderDisabledError(AppError):
    code = "AUTH_PROVIDER_DISABLED"
    http_status = 503
    default_message = "Вход через этого провайдера не настроен"


class DbUnavailableError(AppError):
    code = "DB_UNAVAILABLE"
    http_status = 503
    default_message = "Нет соединения с базой данных"


def error_response(
    status: int, code: str, message: str, details: Any = None, headers: dict[str, str] | None = None
) -> JSONResponse:
    body = {"error": {"code": code, "message": message, "details": details if details is not None else {}}}
    return JSONResponse(status_code=status, content=jsonable_encoder(body), headers=headers)


def _safe_error(err: dict[str, Any]) -> dict[str, Any]:
    out = {k: v for k, v in err.items() if k != "ctx"}
    if "ctx" in err:
        out["ctx"] = {k: str(v) for k, v in err["ctx"].items()}
    if "password" in (err.get("loc") or ()):
        out.pop("input", None)  # пароль не возвращается в ответе
    if isinstance(out.get("input"), dict) and "password" in out["input"]:
        out["input"] = {k: v for k, v in out["input"].items() if k != "password"}
    if "input" in out:
        try:
            jsonable_encoder(out["input"])
        except Exception:
            out["input"] = str(out["input"])
    return out


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError):
        return error_response(exc.http_status, exc.code, exc.message, exc.details, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError):
        return error_response(
            422,
            "VALIDATION_ERROR",
            "Неверное тело запроса",
            {"errors": [_safe_error(e) for e in exc.errors()]},
        )

    @app.exception_handler(OperationalError)
    async def _db(_: Request, exc: OperationalError):
        return error_response(503, "DB_UNAVAILABLE", DbUnavailableError.default_message)

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return error_response(404, "NOT_FOUND", "Объект не найден")
        message = exc.detail if isinstance(exc.detail, str) else "Ошибка запроса"
        return error_response(exc.status_code, f"HTTP_{exc.status_code}", message)
