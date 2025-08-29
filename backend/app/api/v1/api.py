"""
Главный роутер API v1 для VK Comments Parser
"""

from typing import Dict, Any
from fastapi import APIRouter

from app.api.v1.comments import router as comments_router
from app.api.v1.groups import router as groups_router
from app.api.v1.keywords import router as keywords_router
from app.api.v1.parser import router as parser_router
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

# Подключаем роутеры
api_router.include_router(comments_router, tags=["Comments"])
api_router.include_router(groups_router, tags=["Groups"])
api_router.include_router(keywords_router, tags=["Keywords"])
api_router.include_router(parser_router, tags=["Parser"])
api_router.include_router(monitoring_router, tags=["Monitoring"])
api_router.include_router(morphological_router, tags=["Morphological"])
api_router.include_router(errors_router, tags=["Errors"])
api_router.include_router(settings_router, tags=["Settings"])
api_router.include_router(health_router, tags=["Health"])


@api_router.get("/")
async def api_info() -> Dict[str, Any]:
    """Информация об API"""
    return {
        "service": "VK Comments Parser API",
        "version": "1.0.0",
        "description": "API для парсинга комментариев VK",
        "status": "✅ CommentService добавлен - рефакторинг по SOLID принципам",
        "documentation": {"swagger": "/docs", "redoc": "/redoc"},
    }
