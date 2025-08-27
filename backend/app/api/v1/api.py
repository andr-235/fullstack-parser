"""
Главный роутер API v1 для VK Comments Parser

Этот модуль объединяет все API эндпоинты версии 1.0
и предоставляет общую информацию об API.
"""

from typing import Dict, Any
from fastapi import APIRouter

from app.api.v1 import (
    background_tasks,
    comments,
    errors,
    groups,
    health,
    keywords,
    monitoring,
    morphological,
    parser,
    settings,
    stats,
)

# Создаем главный роутер с метаданными
api_router = APIRouter(
    prefix="",
    tags=["API v1"],
    responses={
        404: {"description": "Endpoint not found"},
        500: {"description": "Internal server error"},
    },
)

# Подключение всех роутеров с консистентным форматированием
# Подключаем health роутер
api_router.include_router(health.router, tags=["Health"])

api_router.include_router(
    background_tasks.router,
    prefix="/background-tasks",
    tags=["Background Tasks"],
)

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

api_router.include_router(
    settings.router, prefix="/settings", tags=["Settings"]
)

api_router.include_router(
    errors.router, prefix="/errors", tags=["Error Reports"]
)


@api_router.get(
    "/",
    summary="API Information",
    description="Получить информацию об API и доступных эндпоинтах",
    response_description="Информация об API сервисе",
)
async def api_info() -> Dict[str, Any]:
    """
    Предоставляет информацию об API сервисе.

    Returns:
        Dict[str, Any]: Словарь с информацией об API, включая:
            - service: Название сервиса
            - version: Версия API
            - endpoints: Описание доступных эндпоинтов
    """
    return {
        "service": "VK Comments Parser API",
        "version": "1.0.0",
        "description": "API для парсинга и анализа комментариев VK",
        "endpoints": {
            "background_tasks": {
                "path": "/background-tasks",
                "description": "Управление фоновыми задачами",
                "methods": ["GET", "POST", "DELETE"],
            },
            "comments": {
                "path": "/comments",
                "description": "Найденные комментарии",
                "methods": ["GET", "PUT", "DELETE"],
            },
            "groups": {
                "path": "/groups",
                "description": "Управление VK группами",
                "methods": ["GET", "POST", "PUT", "DELETE"],
            },
            "keywords": {
                "path": "/keywords",
                "description": "Управление ключевыми словами",
                "methods": ["GET", "POST", "PUT", "DELETE"],
            },
            "parser": {
                "path": "/parser",
                "description": "Парсинг и поиск комментариев",
                "methods": ["GET", "POST"],
            },
            "stats": {
                "path": "/stats",
                "description": "Статистика системы",
                "methods": ["GET"],
            },
            "monitoring": {
                "path": "/monitoring",
                "description": "Автоматический мониторинг групп",
                "methods": ["GET", "POST", "PUT", "DELETE"],
            },
            "morphological": {
                "path": "/morphological",
                "description": "Морфологический анализ слов",
                "methods": ["GET", "POST"],
            },
            "settings": {
                "path": "/settings",
                "description": "Управление настройками приложения",
                "methods": ["GET", "PUT"],
            },
            "errors": {
                "path": "/errors",
                "description": "Отчеты об ошибках",
                "methods": ["GET", "POST", "PUT"],
            },
            "health": {
                "path": "/health",
                "description": "Состояние сервиса",
                "methods": ["GET"],
            },
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
        },
    }
