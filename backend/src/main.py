"""
Основной файл приложения VK Comments Parser

Мигрировано из app/main.py
в соответствии с fastapi-best-practices
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from shared.config import settings

# Sentry integration
if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(auto_enabling_instrumentations=False),
            SqlalchemyIntegration(),
            RedisIntegration(),
            CeleryIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )

from shared.infrastructure.database.session import DatabaseSession
from shared.presentation.exceptions import APIException
from shared.presentation.responses import BaseResponse

# Импорт роутеров (будут добавлены по мере миграции модулей)
# Auth module - полная интеграция
from auth import (
    get_current_user, 
    get_current_active_user,
    auth_router,
)
from auth.infrastructure.factory import setup_auth_infrastructure

# User module - полная интеграция
from user import user_router
from user.infrastructure.factory import setup_user_infrastructure
from comments.presentation.router import router as comments_router

from groups.router import router as groups_router

from parser.router import router as parser_router

from morphological.router import router as morphological_router
from keywords.router import router as keywords_router

from settings.router import router as settings_router
from health.router import router as health_router
from error_reporting.router import router as error_reporting_router

# Authors module - полная интеграция
from authors import router as authors_router

# Импорт middleware
from infrastructure.middleware.logging import RequestLoggingMiddleware
from infrastructure.middleware.rate_limit import SimpleRateLimitMiddleware

# Импорт handlers из shared
from shared.presentation.exceptions import (
    base_exception_handler,
    cache_exception_handler,
    database_exception_handler,
    generic_exception_handler,
    rate_limit_exception_handler,
    validation_exception_handler,
    vk_api_exception_handler,
)

# Импорт Celery модуля
from infrastructure.celery_service import celery_service

# Инициализация логгера
from infrastructure.logging import get_loguru_logger

logger = get_loguru_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan с полной инициализацией"""
    logger.info(
        "🚀 Запуск VK Comments Parser v1.7.0 (FastAPI Best Practices)..."
    )

    # Инициализируем базу данных
    try:
        db_session = DatabaseSession()
        db_session.initialize(settings.database_url)
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

    # Инициализируем кэш
    try:
        from .shared.infrastructure.cache.redis_cache import cache
        await cache.initialize()
        logger.info("🗄️ Redis кэш инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации кэша: {e}")
        raise

    # Инициализируем Celery сервис
    try:
        from .shared.infrastructure.task_queue.celery_app import celery_app

        await celery_service.initialize(celery_app)
        logger.info("⚡ Celery сервис инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Celery: {e}")
        raise

    # Инициализируем модуль Auth
    try:
        from .shared.infrastructure.database.session import get_async_session
        
        # Получаем сессию базы данных
        async_session = get_async_session()
        
        # Настраиваем модуль Auth
        auth_container = setup_auth_infrastructure(
            session=async_session(),
            secret_key=settings.secret_key or "default-secret-key-change-in-production",
            redis_url=settings.redis_cache_url,
            use_cache=True,
            cache_ttl=300,
            password_rounds=12,
            access_token_expire_minutes=30,
            refresh_token_expire_days=7
        )
        logger.info("🔐 Модуль Auth инициализирован")
        
        # Настраиваем модуль User
        user_container = setup_user_infrastructure(
            session=async_session(),
            password_service=auth_container.get_password_service(),
            cache=auth_container.get_cache() if hasattr(auth_container, 'get_cache') else None,
            use_cache=True
        )
        logger.info("👤 Модуль User инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации модулей Auth/User: {e}")
        raise

    logger.info("✅ Система готова к работе!")
    logger.info("📋 API v1.7.0 доступен: /api/v1")
    logger.info("📚 Документация: /docs")

    yield

    logger.info("🛑 Остановка VK Comments Parser...")

    # Закрываем кэш
    try:
        from .shared.infrastructure.cache.redis_cache import cache
        await cache.close()
        logger.info("🗄️ Redis кэш закрыт")
    except Exception as e:
        logger.error(f"❌ Ошибка закрытия кэша: {e}")

    # Закрываем Celery сервис
    try:
        await celery_service.close()
        logger.info("⚡ Celery сервис закрыт")
    except Exception as e:
        logger.error(f"❌ Ошибка закрытия Celery: {e}")


# Создание FastAPI приложения
app = FastAPI(
    title="VK Comments Parser API",
    version="1.7.0",
    description="""
    🚀 **Enterprise-grade VK Comments Parser API v1.7.0**

    ## 🏗️ **FastAPI Best Practices Architecture**
    Полностью переработанная версия с архитектурой fastapi-best-practices

    ## ✨ Новые возможности v1.7.0:
    - 🏗️ **FastAPI Best Practices** - рекомендуемая структура проекта
    - 📦 **Модульная архитектура** - каждый домен в отдельном модуле
    - 🎯 **Стандартизированные ответы** - унифицированные ответы и ошибки
    - ⚡ **Улучшенная производительность** - оптимизированная структура
    - 🔍 **Детальная документация** - полная API документация
    - 🏥 **Расширенные health checks** - readiness/liveness проверки

    ## 📚 API Endpoints:
    - **Auth**: `/api/v1/auth` - аутентификация и авторизация ✅
    - **Users**: `/api/v1/users` - управление пользователями ✅
    - **Authors**: `/api/v1/authors` - управление авторами VK ✅ (Clean Architecture)
    - **Comments**: `/api/v1/comments` - работа с комментариями ✅
    - **Groups**: `/api/v1/groups` - управление группами VK ✅
    - **Keywords**: `/api/v1/keywords` - ключевые слова ✅
    - **Parser**: `/api/v1/parser` - парсинг данных ✅
    - **Health**: `/api/v1/health` - расширенные проверки здоровья ✅
    - **Settings**: `/api/v1/settings` - управление настройками ✅
    - **Errors**: `/api/v1/reports` - отчеты об ошибках ✅
    - **Morphological**: `/api/v1/morphological` - морфологический анализ ✅

    ## 🔧 Enterprise-grade Улучшения:
    - **FastAPI Best Practices** - следование рекомендациям сообщества
    - **Модульная структура** - чистое разделение ответственности
    - **Стандартизированные ответы** - унифицированные ответы и ошибки
    - **Production Monitoring** - health checks, метрики, логи
    - **Error Handling** - комплексная обработка ошибок
    - **Request Tracking** - полная трассировка запросов

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


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Добавляем кастомное middleware
app.add_middleware(RequestLoggingMiddleware, log_request_body=True)
app.add_middleware(SimpleRateLimitMiddleware)


# Обработчики исключений
@app.exception_handler(APIException)
async def handle_api_exception(request: Request, exc: APIException):
    """Обработчик кастомных API исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code or "UNKNOWN_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
            },
            "extra_data": getattr(exc, "details", None),
        },
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(
    request: Request, exc: RequestValidationError
):
    """Обработчик ошибок валидации FastAPI/Pydantic"""
    # Логируем детали ошибки валидации
    logger.error(f"Validation error on {request.url}: {exc.errors()}")

    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "type": error.get("type", "validation_error"),
                "loc": error.get("loc", []),
                "msg": error.get("msg", "Validation error"),
                "input": error.get("input", None),
            }
        )

    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
            "message": "Validation error",
        },
    )


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
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Внутренняя ошибка сервера",
                "status_code": 500,
            }
        },
    )


# Дополнительные обработчики исключений
# Порядок важен - более специфичные обработчики должны быть добавлены первыми
app.add_exception_handler(BaseResponse, base_exception_handler)
app.add_exception_handler(ValueError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Базовый роутер для информации о API
@app.get("/api/v1/")
async def api_info(request: Request):
    """Информация об API v1.7.0"""
    return {
        "service": "VK Comments Parser API",
        "version": "v1.7.0",
        "description": "🚀 Enterprise-grade API с FastAPI Best Practices архитектурой",
        "status": "✅ API готов к работе - модули в процессе миграции",
        "features": [
            "🏗️ FastAPI Best Practices архитектура",
            "📦 Модульная структура",
            "🎯 Стандартизированные ответы",
            "⚡ Улучшенная производительность",
            "🔍 Детальная документация",
            "🏥 Расширенные health checks",
        ],
        "modules_status": {
            "auth": "✅ Готов к работе",
            "user": "✅ Готов к работе (отдельный модуль)",
            "authors": "✅ Готов к работе (Clean Architecture + исправлены критические проблемы)",
            "comments": "✅ Готов к работе",
            "groups": "✅ Готов к работе",
            "parser": "✅ Готов к работе",
            "morphological": "✅ Готов к работе",
            "keywords": "✅ Готов к работе",
            "vk_api": "✅ Готов к работе",
            "settings": "✅ Готов к работе",
            "health": "✅ Готов к работе",
            "error_reporting": "✅ Готов к работе",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "changelog": "Полная миграция на FastAPI Best Practices структуру",
        "architecture": {
            "structure": "src/{module}/",
            "modules": [
                "auth",
                "user",
                "authors",
                "comments",
                "groups",
                "parser",
                "morphological",
            ],
            "global_components": [
                "config",
                "database",
                "exceptions",
                "pagination",
                "main",
            ],
        },
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Простая проверка здоровья"""
    return {"status": "healthy", "version": "1.7.0"}


# Подключаем роутеры модулей
# Auth module - полная интеграция
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(comments_router, prefix="/api/v1", tags=["Comments"])
app.include_router(groups_router, prefix="/api/v1", tags=["Groups"])
app.include_router(parser_router, prefix="/api/v1", tags=["Parser"])
app.include_router(
    morphological_router, prefix="/api/v1", tags=["Morphological Analysis"]
)
app.include_router(
    keywords_router, prefix="/api/v1", tags=["Keywords Management"]
)

app.include_router(
    settings_router, prefix="/api/v1", tags=["Settings Management"]
)
app.include_router(health_router, prefix="/api/v1", tags=["Health Monitoring"])
app.include_router(
    error_reporting_router, prefix="/api/v1", tags=["Error Reports"]
)

# Authors module - полная интеграция
app.include_router(authors_router, prefix="/api/v1", tags=["Authors"])


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
