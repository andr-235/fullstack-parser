"""
FastAPI роутер для модуля Parser

Определяет API эндпоинты для управления парсингом VK данных
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request

from .dependencies import get_parser_service
from .config import ParserConfig
from .schemas import (
    ParseRequest,
    ParseResponse,
    ParseStatus,
    ParserState,
    StopParseRequest,
    StopParseResponse,
    ParseTaskListResponse,
    ParseStats,
    ParseTask,
)
from .service import ParserService
from ..pagination import (
    get_pagination_params,
    PaginationParams,
    create_paginated_response,
    PageParam,
    SizeParam,
)

router = APIRouter(
    prefix="/parser",
    tags=["Parser"],
    responses={
        404: {"description": "Задача не найдена"},
        422: {"description": "Ошибка валидации данных"},
        500: {"description": "Внутренняя ошибка сервера"},
        503: {"description": "Сервис недоступен"},
    },
)


@router.post(
    "/parse",
    response_model=ParseResponse,
    status_code=201,
    summary="Запустить парсинг групп",
    description="Запустить парсинг комментариев из указанных групп VK",
)
async def start_parsing(
    request: ParseRequest,
    service: ParserService = Depends(get_parser_service),
) -> ParseResponse:
    """Запустить парсинг комментариев из групп VK"""
    try:
        result = await service.start_parsing(
            group_ids=request.group_ids,
            max_posts=(
                request.max_posts if request.max_posts is not None else 100
            ),
            max_comments_per_post=(
                request.max_comments_per_post
                if request.max_comments_per_post is not None
                else 100
            ),
            force_reparse=request.force_reparse,
            priority=request.priority,
        )
        return ParseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/stop",
    response_model=StopParseResponse,
    summary="Остановить парсинг",
    description="Остановить выполнение задач парсинга",
)
async def stop_parsing(
    request: StopParseRequest,
    service: ParserService = Depends(get_parser_service),
) -> StopParseResponse:
    """Остановить парсинг задач"""
    try:
        result = await service.stop_parsing(request.task_id)
        return StopParseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/state",
    response_model=ParserState,
    summary="Получить состояние парсера",
    description="Получить текущее состояние системы парсинга",
)
async def get_parser_state(
    service: ParserService = Depends(get_parser_service),
) -> ParserState:
    """Получить состояние парсера"""
    try:
        state = await service.get_parser_state()
        return ParserState(**state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tasks/{task_id}",
    response_model=ParseStatus,
    summary="Получить статус задачи",
    description="Получить детальную информацию о задаче парсинга",
)
async def get_task_status(
    task_id: str,
    service: ParserService = Depends(get_parser_service),
) -> ParseStatus:
    """Получить статус задачи парсинга"""
    try:
        status = await service.get_task_status(task_id)
        if not status:
            raise HTTPException(
                status_code=404, detail=f"Задача {task_id} не найдена"
            )
        return ParseStatus(**status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/tasks",
    response_model=ParseTaskListResponse,
    summary="Получить список задач",
    description="Получить список задач парсинга с фильтрацией и пагинацией",
)
async def get_tasks_list(
    # Параметры пагинации
    page: PageParam = 1,
    size: SizeParam = 20,
    # Параметры фильтрации
    status: Optional[str] = Query(
        None, description="Фильтр по статусу задачи"
    ),
    # Сервисы
    service: ParserService = Depends(get_parser_service),
) -> ParseTaskListResponse:
    """Получить список задач парсинга"""

    pagination = PaginationParams(
        page=page,
        size=size,
    )

    # Получаем задачи
    tasks_data = await service.get_tasks_list(
        limit=pagination.limit,
        offset=pagination.offset,
        status_filter=status,
    )

    # Преобразуем словари в объекты ParseTask
    tasks = [ParseTask(**task) for task in tasks_data]

    # В реальности нужно получить total из БД
    total = len(tasks)  # Заглушка

    return ParseTaskListResponse(
        items=tasks,
        total=total,
        page=pagination.page,
        size=pagination.size,
        pages=(
            (total + pagination.size - 1) // pagination.size
            if pagination.size > 0
            else 0
        ),
    )


@router.get(
    "/stats",
    response_model=ParseStats,
    summary="Получить статистику парсинга",
    description="Получить общую статистику работы парсера",
)
async def get_parsing_stats(
    service: ParserService = Depends(get_parser_service),
) -> ParseStats:
    """Получить статистику парсинга"""
    try:
        stats = await service.get_parsing_stats()
        return ParseStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/global",
    response_model=ParseStats,
    summary="Получить глобальную статистику парсинга",
    description="Получить глобальную статистику работы парсера (алиас для /stats)",
)
async def get_global_parsing_stats(
    service: ParserService = Depends(get_parser_service),
) -> ParseStats:
    """Получить глобальную статистику парсинга"""
    try:
        stats = await service.get_parsing_stats()
        return ParseStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/test/{group_id}",
    summary="Тестовый парсинг группы",
    description="Тестовый запуск парсинга одной группы (без сохранения в БД)",
)
async def test_parse_group(
    group_id: int,
    max_posts: int = Query(10, description="Максимум постов для теста"),
    max_comments_per_post: int = Query(
        10, description="Максимум комментариев на пост"
    ),
    service: ParserService = Depends(get_parser_service),
):
    """Тестовый парсинг группы"""
    try:
        result = await service.parse_group(
            group_id=group_id,
            max_posts=max_posts,
            max_comments_per_post=max_comments_per_post,
        )
        return {
            "message": "Тестовый парсинг завершен",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/health",
    summary="Проверка здоровья парсера",
    description="Проверить доступность VK API и работоспособность парсера",
)
async def parser_health_check(
    service: ParserService = Depends(get_parser_service),
):
    """Проверка здоровья парсера"""
    try:
        # Проверяем подключение к VK API
        is_token_valid = await service.client.validate_token()

        return {
            "status": "healthy" if is_token_valid else "unhealthy",
            "vk_api_available": is_token_valid,
            "parser_active_tasks": (await service.get_parser_state())[
                "active_tasks"
            ],
            "timestamp": "2024-01-01T00:00:00Z",  # В реальности datetime.utcnow()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z",
        }


# Экспорт роутера
__all__ = ["router"]
