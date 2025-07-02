"""
Главный роутер API v1 для VK Comments Parser
"""

from fastapi import APIRouter

from app.api.v1 import groups, keywords, parser, stats

api_router = APIRouter()

# Подключение всех роутеров
api_router.include_router(groups.router)
api_router.include_router(keywords.router)
api_router.include_router(parser.router)
api_router.include_router(stats.router)


@api_router.get("/")
async def api_info() -> dict[str, str | dict[str, str]]:
    """Информация об API"""
    return {
        "service": "VK Comments Parser API",
        "version": "1.0.0",
        "endpoints": {
            "groups": "/groups - Управление VK группами",
            "keywords": "/keywords - Управление ключевыми словами",
            "parser": "/parser - Парсинг и поиск комментариев",
            "stats": "/stats - Статистика системы",
        },
    }
