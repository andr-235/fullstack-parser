"""
FastAPI приложение для VK Comments Parser
"""

import asyncio

import structlog
from fastapi import FastAPI
from fastapi.exception_handlers import RequestValidationError
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
from app.middleware.request_logging import RequestLoggingMiddleware
from app.services.scheduler_service import get_scheduler_service

# Настройка структурированного логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def lifespan(app: FastAPI):
    """Lifespan context manager для startup/shutdown событий с оптимизацией"""
    # Startup - асинхронная инициализация
    logger.info("🚀 Запуск VK Comments Parser...")

    # Инициализируем БД в фоне, не блокируя запуск
    try:
        await init_db()
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка инициализации БД: {e}")

    # Инициализируем планировщик мониторинга
    scheduler_task = None
    try:
        if settings.monitoring.auto_start_scheduler:
            logger.info("⏰ Инициализация планировщика мониторинга...")
            scheduler = await get_scheduler_service()

            # Запускаем планировщик в фоновом режиме
            scheduler_task = asyncio.create_task(
                scheduler.start_monitoring_scheduler(
                    settings.monitoring.scheduler_interval_seconds
                )
            )
            logger.info(
                "✅ Планировщик мониторинга запущен",
                interval_seconds=settings.monitoring.scheduler_interval_seconds,
            )
        else:
            logger.info("⏸️ Автоматический запуск планировщика отключен")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка инициализации планировщика: {e}")

    yield

    # Shutdown
    logger.info("🛑 Остановка VK Comments Parser...")

    # Останавливаем планировщик
    if scheduler_task:
        try:
            scheduler = await get_scheduler_service()
            await scheduler.stop_monitoring_scheduler()
            scheduler_task.cancel()
            logger.info("⏹️ Планировщик мониторинга остановлен")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка остановки планировщика: {e}")


# Создание FastAPI приложения с оптимизациями
app = FastAPI(
    title="VK Comments Parser",
    version="1.0.0",
    description="API для парсинга комментариев ВКонтакте",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan,
    redirect_slashes=False,  # Отключаем автоматическое добавление trailing slash
)


# Централизованный exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=True, path=request.url.path)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": str(exc),
            "path": str(request.url.path),
        },
    )


@app.exception_handler(FastAPIHTTPException)
async def http_exception_handler(request: Request, exc: FastAPIHTTPException):
    logger.warning(
        "HTTPException",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_exception",
            "message": exc.detail,
            "path": str(request.url.path),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logger.warning(
        "Validation error", errors=exc.errors(), path=request.url.path
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": exc.errors(),
            "path": str(request.url.path),
        },
    )


# Добавляем middleware для обработки заголовков прокси
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки заголовков прокси (X-Forwarded-*)"""

    async def dispatch(self, request: Request, call_next):
        # Обрабатываем заголовки прокси
        forwarded_proto = request.headers.get("x-forwarded-proto")
        forwarded_host = request.headers.get("x-forwarded-host")

        # Если запрос пришел через HTTPS прокси, обновляем URL
        if forwarded_proto == "https":
            # Создаем новый URL с HTTPS схемой
            url = request.url.replace(scheme="https")
            if forwarded_host:
                url = url.replace(netloc=forwarded_host)
            request._url = url

            # Также обновляем заголовки для правильной обработки
            request.scope["scheme"] = "https"
            if forwarded_host:
                request.scope["headers"] = [
                    (name, value)
                    for name, value in request.scope["headers"]
                    if name != b"host"
                ] + [(b"host", forwarded_host.encode())]

        response = await call_next(request)

        # Принудительно устанавливаем HTTPS заголовки для редиректов
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("location")
            if location and location.startswith("http://"):
                # Заменяем HTTP на HTTPS в Location заголовке
                https_location = location.replace("http://", "https://")
                response.headers["location"] = https_location

        return response


# Добавляем TrustedHostMiddleware для безопасности
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # В production замените на конкретные домены
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),  # Используем только разрешённые домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Добавляем middleware для обработки заголовков прокси (должен быть первым)
app.add_middleware(ProxyHeadersMiddleware)

# Добавляем middleware для логирования запросов
app.add_middleware(RequestLoggingMiddleware)

# Подключаем роутеры (lazy loading)
app.include_router(api_router, prefix="/api/v1")
