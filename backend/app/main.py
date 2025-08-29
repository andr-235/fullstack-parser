"""
Production-ready FastAPI приложение для VK Comments Parser
с улучшенной архитектурой и middleware
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db

# Импорт нового middleware
from app.api.v1.middleware.rate_limit import SimpleRateLimitMiddleware
from app.api.v1.middleware.logging import RequestLoggingMiddleware
from app.core.error_handlers import (
    base_exception_handler,
    cache_exception_handler,
    database_exception_handler,
    generic_exception_handler,
    rate_limit_exception_handler,
    validation_exception_handler,
    vk_api_exception_handler,
)
from app.api.v1.exceptions import (
    APIException as BaseAPIException,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    VKAPIError,
)

# Простое логирование вместо structlog
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Production-ready lifespan с полной инициализацией"""
    logger.info("🚀 Запуск VK Comments Parser v1.6.0 (DDD + Middleware)...")

    # Инициализируем базу данных
    try:
        await init_db()
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

    logger.info("✅ Система готова к работе!")
    logger.info("📋 API v1.5.0 доступен: /api/v1")
    logger.info("📚 Документация: /docs")

    yield

    logger.info("🛑 Остановка VK Comments Parser...")


# Создание production-ready FastAPI приложения
app = FastAPI(
    title="VK Comments Parser API",
    version="1.6.0",
    description="""
    🚀 **Enterprise-grade VK Comments Parser API v1.6.0**

    ## 🏗️ **DDD Architecture + Middleware**
    Полностью переработанная версия с **Domain-Driven Design** и enterprise-grade middleware

    ## ✨ Новые возможности v1.6.0:
    - 🏗️ **Domain-Driven Design** - чистая архитектура с Domain + Application слоями
    - 🛡️ **Rate Limiting** - защита от перегрузок (60 запросов/минуту)
    - 📊 **Request Logging** - структурированное логирование всех запросов
    - 🎯 **Standardized Responses** - унифицированные ответы с метаданными
    - ⚡ **Performance Monitoring** - отслеживание производительности
    - 🔍 **Request ID Tracking** - полное отслеживание запросов
    - 🏥 **Advanced Health Checks** - readiness/liveness проверки
    - ⚙️ **Settings Management** - управление конфигурацией
    - 📋 **Error Reporting** - система отчетов об ошибках
    - 📈 **Monitoring System** - мониторинг VK групп
    - 🔤 **Morphological Analysis** - морфологический анализ текста

    ## 📚 API Endpoints:
    - **Comments**: `/api/v1/comments` - работа с комментариями
    - **Groups**: `/api/v1/groups` - управление группами VK
    - **Keywords**: `/api/v1/keywords` - ключевые слова
    - **Parser**: `/api/v1/parser` - парсинг данных
    - **Health**: `/api/v1/health` - расширенные проверки здоровья
    - **Settings**: `/api/v1/settings` - управление настройками
    - **Errors**: `/api/v1/reports` - отчеты об ошибках
    - **Monitoring**: `/api/v1/monitoring` - мониторинг групп
    - **Morphological**: `/api/v1/morphological` - морфологический анализ

    ## 🔧 Enterprise-grade Улучшения:
    - **DDD Architecture** - Domain + Application слои для чистоты кода
    - **Middleware Stack** - rate limiting, logging, caching
    - **Standardized API** - унифицированные ответы и ошибки
    - **Production Monitoring** - health checks, метрики, логи
    - **Error Handling** - комплексная обработка ошибок
    - **Request Tracking** - полная трассировка запросов
    - **Performance Headers** - время обработки в каждом ответе

    ## 📖 Документация:
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


# 🛡️ Middleware (добавляем в правильном порядке)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Добавляем наше middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, requests_per_minute=60)

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
