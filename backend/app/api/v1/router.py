"""
Агрегирующий роутер для API v1 (экспортируется как api_router)
"""

from fastapi import APIRouter

from app.api.v1 import comments, groups, health, keywords, parser, stats

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(
    comments.router, prefix="/comments", tags=["Comments"]
)
api_router.include_router(groups.router, prefix="/groups", tags=["Groups"])
api_router.include_router(
    keywords.router, prefix="/keywords", tags=["Keywords"]
)
api_router.include_router(parser.router, prefix="/parser", tags=["Parser"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])


@api_router.get("/", tags=["Info"])
async def api_info() -> dict[str, str | dict[str, str]]:
    """Информация об API v1"""
    return {
        "service": "VK Comments Parser API",
        "version": "1.0.0",
        "endpoints": {
            "comments": "/comments - Найденные комментарии",
            "groups": "/groups - Управление VK группами",
            "keywords": "/keywords - Управление ключевыми словами",
            "parser": "/parser - Парсинг и поиск комментариев",
            "stats": "/stats - Статистика системы",
            "health": "/health - Состояние сервиса",
        },
    }
