"""
Главный роутер API v1 для VK Comments Parser
с DDD архитектурой и enterprise-grade middleware
"""

from typing import Dict, Any
from fastapi import APIRouter, Request
from ..handlers.common import create_success_response

# Импорт роутеров с DDD архитектурой
from app.api.v1.routers.comments import router as comments_router
from app.api.v1.routers.groups import router as groups_router
from app.api.v1.routers.keywords import router as keywords_router
from app.api.v1.routers.parser import router as parser_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.settings import router as settings_router
from app.api.v1.routers.errors import router as errors_router
from app.api.v1.routers.monitoring import router as monitoring_router
from app.api.v1.routers.morphological import router as morphological_router

# Импорт middleware для интеграции
from app.api.v1.middleware.rate_limit import SimpleRateLimitMiddleware
from app.api.v1.middleware.logging import RequestLoggingMiddleware

# Создаем главный роутер с enterprise-grade метаданными
api_router = APIRouter(
    prefix="",
    tags=["API v1"],
    responses={
        400: {
            "model": dict,
            "description": "Bad Request - Invalid input data",
        },
        401: {
            "model": dict,
            "description": "Unauthorized - Authentication required",
        },
        403: {
            "model": dict,
            "description": "Forbidden - Insufficient permissions",
        },
        404: {"model": dict, "description": "Not Found - Resource not found"},
        422: {
            "model": dict,
            "description": "Validation Error - Invalid request data",
        },
        429: {
            "model": dict,
            "description": "Too Many Requests - Rate limit exceeded",
        },
        500: {
            "model": dict,
            "description": "Internal Server Error - Server error occurred",
        },
        503: {
            "model": dict,
            "description": "Service Unavailable - Service temporarily unavailable",
        },
    },
)

# Подключаем улучшенные роутеры
api_router.include_router(comments_router, tags=["Comments"])
api_router.include_router(groups_router, tags=["Groups"])
api_router.include_router(keywords_router, tags=["Keywords"])
api_router.include_router(parser_router, tags=["Parser"])

# Подключаем остальные роутеры (пока без изменений)
api_router.include_router(monitoring_router, tags=["Monitoring"])
api_router.include_router(morphological_router, tags=["Morphological"])
api_router.include_router(errors_router, tags=["Errors"])
api_router.include_router(settings_router, tags=["Settings"])
api_router.include_router(health_router, tags=["Health"])


@api_router.get("/")
async def api_info(request: Request) -> Dict[str, Any]:
    """Информация об API v1.6.0 с DDD архитектурой"""
    try:
        api_data = {
            "service": "VK Comments Parser API",
            "version": "v1.6.0",
            "description": "🚀 Enterprise-grade API с DDD архитектурой и middleware",
            "status": "✅ API улучшен - добавлены middleware, стандартизированные ответы",
            "features": [
                "🏗️ Domain-Driven Design (DDD) архитектура",
                "🛡️ Rate limiting для защиты от перегрузок",
                "📊 Структурированное логирование запросов",
                "🎯 Стандартизированные ответы и ошибки",
                "⚡ Улучшенная производительность",
                "🔍 Детальная информация о запросах",
                "📝 Полная документация API",
                "🏥 Расширенные health checks",
                "⚙️ Управление настройками",
                "📋 Система отчетов об ошибках",
                "📈 Мониторинг VK групп",
                "🔤 Морфологический анализ текста",
            ],
            "improvements": [
                "Domain-Driven Design Architecture",
                "Application Services Layer",
                "Rate Limiting Middleware",
                "Request Logging Middleware",
                "Standardized Response Format",
                "Enhanced Error Handling",
                "Request ID Tracking",
                "Performance Monitoring",
                "Health Check System",
                "Settings Management",
                "Monitoring System",
                "Morphological Analysis",
            ],
            "endpoints": {
                "comments": "/api/v1/comments",
                "groups": "/api/v1/groups",
                "keywords": "/api/v1/keywords",
                "parser": "/api/v1/parser",
                "monitoring": "/api/v1/monitoring",
                "morphological": "/api/v1/morphological",
                "errors": "/api/v1/reports",
                "settings": "/api/v1/settings",
                "health": "/api/v1/health",
            },
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json",
            },
            "changelog": "Полная переработка с DDD архитектурой, middleware и enterprise-grade функциями",
            "architecture": {
                "domain_layer": [
                    "entities",
                    "value_objects",
                    "domain_services",
                ],
                "application_layer": ["application_services", "use_cases"],
                "infrastructure_layer": [
                    "routers",
                    "middleware",
                    "handlers",
                    "dependencies",
                ],
            },
        }

        return await create_success_response(
            request, api_data, {"message": "API информация получена успешно"}
        )
    except Exception as e:
        from ..handlers.common import create_error_response

        return await create_error_response(
            request,
            500,
            "API_INFO_FAILED",
            f"Failed to get API info: {str(e)}",
        )


# Health check теперь обрабатывается через новый роутер health.py
