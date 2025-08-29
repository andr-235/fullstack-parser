"""
Главный роутер API v1 для VK Comments Parser
с улучшенной архитектурой и middleware
"""

from typing import Dict, Any
from fastapi import APIRouter

# Импорт улучшенных роутеров
from app.api.v1.routers.comments import router as comments_router
from app.api.v1.routers.groups import router as groups_router
from app.api.v1.routers.keywords import router as keywords_router
from app.api.v1.routers.parser import router as parser_router

# Импорт старых роутеров (пока оставляем для совместимости)
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.morphological import router as morphological_router
from app.api.v1.errors import router as errors_router
from app.api.v1.settings import router as settings_router
from app.api.v1.health import router as health_router

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
    """Информация об API v1.5.0 с улучшениями"""
    return {
        "service": "VK Comments Parser API",
        "version": "v1.5.0",
        "description": "🚀 Улучшенная версия API v1 с middleware и стандартизацией",
        "status": "✅ API улучшен - добавлены middleware, стандартизированные ответы",
        "features": [
            "🛡️ Rate limiting для защиты от перегрузок",
            "📊 Структурированное логирование запросов",
            "🎯 Стандартизированные ответы и ошибки",
            "⚡ Улучшенная производительность",
            "🔍 Детальная информация о запросах",
            "📝 Полная документация API",
        ],
        "improvements": [
            "Rate Limiting Middleware",
            "Request Logging Middleware",
            "Standardized Response Format",
            "Enhanced Error Handling",
            "Request ID Tracking",
            "Performance Monitoring",
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
        "health_check": "/api/v1/health",
        "changelog": "Улучшена обработка ошибок, добавлены middleware",
    }


@api_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка здоровья системы"""
    from datetime import datetime
    from app.core.database import get_db_session

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {},
    }

    try:
        # Проверяем подключение к базе данных
        async with get_db_session() as db:
            await db.execute("SELECT 1")
            health_status["services"]["database"] = "✅ connected"
    except Exception as e:
        health_status["services"]["database"] = f"❌ error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Проверяем основные сервисы
    try:
        from app.services.comment_service import comment_service

        health_status["services"]["comment_service"] = "✅ loaded"
    except Exception as e:
        health_status["services"]["comment_service"] = f"❌ error: {str(e)}"

    try:
        from app.services.group_manager import group_manager

        health_status["services"]["group_manager"] = "✅ loaded"
    except Exception as e:
        health_status["services"]["group_manager"] = f"❌ error: {str(e)}"

    try:
        from app.services.vk_api_service import VKAPIService

        health_status["services"]["vk_api_service"] = "✅ loaded"
    except Exception as e:
        health_status["services"]["vk_api_service"] = f"❌ error: {str(e)}"

    # Определяем общий статус
    if any("❌" in status for status in health_status["services"].values()):
        health_status["status"] = "degraded"

    return health_status
