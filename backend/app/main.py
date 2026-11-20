import inspect
from collections.abc import Iterator
from contextlib import asynccontextmanager, contextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, legal, scenarios, sessions, users
from app.api import history as history_api
from app.api import analytics as analytics_api
from app.api import dashboard as dashboard_api
from app.api import mentor as mentor_api
from app.api import npc as npc_api
from app.api import quiz as quiz_api
from app.config import get_settings
from app.db import get_db
from app.errors import install_error_handlers
from app.history import build_store
from app.scenarios.registry import load_registry


def _db_opener(app: FastAPI):
    """Сессия БД для проверок при старте. Берётся через dependency_overrides[get_db],
    чтобы тесты могли подставить свою сессию (с данными из незакоммиченной транзакции)."""
    provider = app.dependency_overrides.get(get_db, get_db)

    @contextmanager
    def open_db() -> Iterator:
        res = provider()
        if inspect.isgenerator(res):
            try:
                yield next(res)
            finally:
                res.close()
        else:
            yield res

    return open_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.dependency_overrides.get(get_settings, get_settings)()
    # Ошибки схемы и отсутствующие ссылки на закон: исключение, сервер не стартует.
    app.state.scenarios = load_registry(settings, _db_opener(app))
    history = build_store(settings)
    history.ensure_indexes()  # create_index идемпотентен; недоступная Mongo только логируется
    app.state.history = history
    try:
        yield
    finally:
        history.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="ADOLAT API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,  # фронт шлёт fetch(..., credentials: "include")
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(legal.router)
    api.include_router(mentor_api.router)
    api.include_router(npc_api.router)
    api.include_router(users.router)
    api.include_router(history_api.router)
    api.include_router(scenarios.router)
    api.include_router(sessions.router)
    api.include_router(quiz_api.router)
    api.include_router(dashboard_api.router)
    api.include_router(analytics_api.router)
    app.include_router(api)
    return app


app = create_app()
