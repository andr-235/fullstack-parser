"""
Production-ready FastAPI приложение для VK Comments Parser
с централизованной обработкой ошибок и мониторингом
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.error_handlers import (
    base_exception_handler,
    cache_exception_handler,
    database_exception_handler,
    generic_exception_handler,
    rate_limit_exception_handler,
    validation_exception_handler,
    vk_api_exception_handler,
)
from app.core.exceptions import (
    BaseAPIException,
    CacheError,
    DatabaseError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
    VKAPIError,
)

# Простое логирование вместо structlog
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production-ready lifespan с полной инициализацией"""
    logger.info("🚀 Запуск VK Comments Parser...")

    # Инициализируем базу данных
    try:
        await init_db()
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

    logger.info("✅ Система готова к работе!")
    yield

    logger.info("🛑 Остановка VK Comments Parser...")


async def request_logging_middleware(request: Request, call_next):
    """
    Middleware для логирования HTTP запросов.
    Логирует время выполнения, статус код и ошибки.
    """
    start_time = time.time()

    # Логируем входящий запрос
    logger.info(
        f"➡️  {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        query_params=dict(request.query_params),
        client_ip=get_client_ip(request),
    )

    try:
        # Выполняем запрос
        response = await call_next(request)

        # Вычисляем время выполнения
        process_time = time.time() - start_time

        # Логируем успешный ответ
        logger.info(
            f"✅ {request.method} {request.url.path} - {response.status_code}",
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s",
        )

        # Добавляем заголовок с временем выполнения
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        # Логируем ошибку
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - Error",
            error=str(e),
            process_time=f"{process_time:.3f}s",
            exc_info=True,
        )
        raise


def get_client_ip(request: Request) -> str:
    """Получить IP адрес клиента с учетом прокси"""
    # Проверяем заголовки прокси
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback к стандартному client
    return request.client.host if request.client else "unknown"


# Создание production-ready FastAPI приложения
app = FastAPI(
    title="VK Comments Parser API",
    version="2.0.0",
    description="""
    🚀 **Production-ready API для парсинга комментариев ВКонтакте**

    ## ✨ Возможности:
    - 📊 Полный анализ комментариев VK групп
    - 🔍 Продвинутый поиск по ключевым словам
    - 📈 Детальная статистика и аналитика
    - ⚡ Асинхронная обработка через ARQ
    - 🛡️ Централизованная обработка ошибок
    - 📝 Полная документация API

    ## 🔧 Архитектура:
    - **SOLID принципы** - модульная и поддерживаемая кодовая база
    - **Clean Architecture** - четкое разделение ответственности
    - **Async/Await** - высокая производительность
    - **Type Hints** - типизированный код

    ## 📚 Документация:
    - **Swagger UI**: `/docs`
    - **ReDoc**: `/redoc`
    - **OpenAPI**: `/openapi.json`
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# 🎯 Продвинутые обработчики исключений
@app.exception_handler(BaseAPIException)
async def handle_base_api_exception(request: Request, exc: BaseAPIException):
    """Обработчик кастомных API исключений"""
    return await base_exception_handler(request, exc)


@app.exception_handler(ValidationError)
async def handle_validation_error(request: Request, exc: ValidationError):
    """Обработчик ошибок валидации"""
    return await validation_exception_handler(request, exc)


@app.exception_handler(VKAPIError)
async def handle_vk_api_error(request: Request, exc: VKAPIError):
    """Обработчик ошибок VK API"""
    return await vk_api_exception_handler(request, exc)


@app.exception_handler(DatabaseError)
async def handle_database_error(request: Request, exc: DatabaseError):
    """Обработчик ошибок базы данных"""
    return await database_exception_handler(request, exc)


@app.exception_handler(CacheError)
async def handle_cache_error(request: Request, exc: CacheError):
    """Обработчик ошибок кэша"""
    return await cache_exception_handler(request, exc)


@app.exception_handler(RateLimitError)
async def handle_rate_limit_error(request: Request, exc: RateLimitError):
    """Обработчик ошибок ограничения скорости"""
    return await rate_limit_exception_handler(request, exc)


@app.exception_handler(ServiceUnavailableError)
async def handle_service_unavailable(
    request: Request, exc: ServiceUnavailableError
):
    """Обработчик ошибок недоступности сервиса"""
    return await base_exception_handler(request, exc)


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException):
    """Обработчик стандартных HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_EXCEPTION",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    """Обработчик непредвиденных ошибок"""
    return await generic_exception_handler(request, exc)


# 🛡️ Middleware для безопасности и мониторинга
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
)

# 📊 Middleware для логирования запросов
app.middleware("http")(request_logging_middleware)

# Подключаем роутеры
app.include_router(api_router, prefix="/api/v1")

# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
