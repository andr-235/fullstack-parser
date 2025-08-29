"""
Главный роутер API v1 для VK Comments Parser
с улучшенной архитектурой и middleware
"""

from typing import Dict, Any
from fastapi import APIRouter

# Импорт улучшенных роутеров (DDD + Middleware)
from app.api.v1.routers.comments import router as comments_router
from app.api.v1.routers.groups import router as groups_router
from app.api.v1.routers.keywords import router as keywords_router
from app.api.v1.routers.parser import router as parser_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.settings import router as settings_router
from app.api.v1.routers.errors import router as errors_router
from app.api.v1.routers.monitoring import router as monitoring_router
from app.api.v1.routers.morphological import router as morphological_router

# Создаем главный роутер с метаданными
api_router = APIRouter(
    prefix="",
    tags=["API v1"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"},
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
async def api_info() -> Dict[str, Any]:
    """Информация об API v1.6.0 с DDD архитектурой"""
    return {
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
        ],
        "endpoints": {
            "comments": "/api/v1/comments",
            "groups": "/api/v1/groups",
            "keywords": "/api/v1/keywords",
            "parser": "/api/v1/parser",
            "monitoring": "/api/v1/monitoring",
            "morphological": "/api/v1/morphological",
            "errors": "/api/v1/errors",
            "settings": "/api/v1/settings",
            "health": "/api/v1/health",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
        "changelog": "Полная переработка с DDD архитектурой, middleware и enterprise-grade функциями",
    }


# Health check теперь обрабатывается через новый роутер health.py
