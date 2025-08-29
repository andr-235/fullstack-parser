"""
Главный роутер API v1 для VK Comments Parser
"""

from typing import Dict, Any
from fastapi import APIRouter

from app.api.v1.comments import router as comments_router

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
