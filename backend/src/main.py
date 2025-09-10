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

from .config import settings
from .database import database_service
from .exceptions import APIError
from .responses import BaseAPIException

# Импорт роутеров (будут добавлены по мере миграции модулей)
from .auth.router import router as auth_router
from .comments.router import router as comments_router

from .groups.router import router as groups_router

from .parser.router import router as parser_router

from .morphological.router import router as morphological_router
from .keywords.router import router as keywords_router

from .settings.router import router as settings_router
from .health.router import router as health_router
from .error_reporting.router import router as error_reporting_router

# Импорт middleware
from .infrastructure.middleware.logging import RequestLoggingMiddleware
from .infrastructure.middleware.rate_limit import SimpleRateLimitMiddleware

# Импорт handlers
from .handlers import (
    base_exception_handler,
    cache_exception_handler,
    database_exception_handler,
    generic_exception_handler,
    rate_limit_exception_handler,
    validation_exception_handler,
    vk_api_exception_handler,
)

# Импорт Celery модуля
from .infrastructure.celery_service import celery_service

# Инициализация логгера
from .infrastructure.logging import get_loguru_logger

logger = get_loguru_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan с полной инициализацией"""
    logger.info(
        "🚀 Запуск VK Comments Parser v1.7.0 (FastAPI Best Practices)..."
    )

    # Инициализируем базу данных
    try:
        await database_service.init_database()
        logger.info("📊 База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise

    # Инициализируем Celery сервис
    try:
        from .celery_app import app as celery_app

        await celery_service.initialize(celery_app)
        logger.info("⚡ Celery сервис инициализирован")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации Celery: {e}")
        raise

    logger.info("✅ Система готова к работе!")
    logger.info("📋 API v1.7.0 доступен: /api/v1")
    logger.info("📚 Документация: /docs")

    yield

    logger.info("🛑 Остановка VK Comments Parser...")

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
    - **Comments**: `/api/v1/comments` - работа с комментариями (в разработке)
    - **Groups**: `/api/v1/groups` - управление группами VK (в разработке)
    - **Keywords**: `/api/v1/keywords` - ключевые слова (в разработке)
    - **Parser**: `/api/v1/parser` - парсинг данных (в разработке)
    - **Health**: `/api/v1/health` - расширенные проверки здоровья (в разработке)
    - **Settings**: `/api/v1/settings` - управление настройками (в разработке)
    - **Errors**: `/api/v1/reports` - отчеты об ошибках (в разработке)

    - **Morphological**: `/api/v1/morphological` - морфологический анализ (в разработке)

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
@app.exception_handler(APIError)
async def handle_api_exception(request: Request, exc: APIError):
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
app.add_exception_handler(BaseAPIException, base_exception_handler)
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
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
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


# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
