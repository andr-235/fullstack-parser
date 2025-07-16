"""
Главный роутер API v1 для VK Comments Parser
"""

from fastapi import APIRouter

from app.api.v1 import (
    comments,
    groups,
    health,
    keywords,
    monitoring,
    morphological,
    parser,
    stats,
)

api_router = APIRouter()

# Подключение всех роутеров
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
api_router.include_router(
    monitoring.router, prefix="/monitoring", tags=["Monitoring"]
)
api_router.include_router(
    morphological.router,
    prefix="/morphological",
    tags=["Morphological Analysis"],
)


@api_router.get("/")
async def api_info() -> dict[str, str | dict[str, str]]:
    """Информация об API"""
    return {
        "service": "VK Comments Parser API",
        "version": "1.0.0",
        "endpoints": {
            "comments": "/comments - Найденные комментарии",
            "groups": "/groups - Управление VK группами",
            "keywords": "/keywords - Управление ключевыми словами",
            "parser": "/parser - Парсинг и поиск комментариев",
            "stats": "/stats - Статистика системы",
            "monitoring": "/monitoring - Автоматический мониторинг групп",
            "morphological": "/morphological - Морфологический анализ слов",
            "health": "/health - Состояние сервиса",
        },
    }
