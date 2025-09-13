"""
FastAPI роутер для модуля Parser

Определяет API эндпоинты для управления парсингом VK данных
"""

import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from parser.dependencies import get_parser_service
from parser.schemas import (
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
from parser.service import ParserService
from parser.models import TaskStatus

# Настройка логирования
logger = logging.getLogger(__name__)

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
    status_code=status.HTTP_201_CREATED,
    summary="Запустить парсинг групп",
    description="Запустить парсинг комментариев из указанных групп VK",
)
async def start_parsing(
    request: ParseRequest,
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseResponse:
    """Запустить парсинг комментариев из групп VK"""
    logger.info(
        f"Starting parsing request: group_ids={request.group_ids}, "
        f"max_posts={request.max_posts}, max_comments_per_post={request.max_comments_per_post}"
    )

    try:
        task_id = await service.start_parsing(
            group_ids=request.group_ids,
            max_posts=request.max_posts,
            max_comments_per_post=request.max_comments_per_post,
            force_reparse=request.force_reparse,
            priority=request.priority,
        )

        return ParseResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            group_ids=request.group_ids,
            created_at=service.tasks[task_id].created_at,
            priority=request.priority,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Failed to start parsing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@router.get(
    "/status/{task_id}",
    response_model=ParseStatus,
    summary="Получить статус задачи",
    description="Получить текущий статус и прогресс задачи парсинга",
)
async def get_task_status(
    task_id: str,
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseStatus:
    """Получить статус задачи парсинга"""
    task = await service.get_task_status(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача {task_id} не найдена",
        )

    return ParseStatus(
        task_id=task.task_id,
        status=task.status,
        progress=task.progress,
        current_group=task.current_group,
        groups_completed=task.groups_completed,
        groups_total=task.groups_total,
        posts_found=task.posts_found,
        comments_found=task.comments_found,
        errors=task.errors,
        started_at=task.started_at,
        completed_at=task.completed_at,
        duration=task.duration,
        priority=task.priority,
    )


@router.get(
    "/tasks",
    response_model=ParseTaskListResponse,
    summary="Получить список задач",
    description="Получить список всех задач парсинга",
)
async def get_tasks(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseTaskListResponse:
    """Получить список всех задач"""
    tasks = await service.get_all_tasks()
    
    task_list = [
        ParseTask(
            task_id=task.task_id,
            group_ids=task.group_ids,
            status=task.status,
            priority=task.priority,
            progress=task.progress,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )
        for task in tasks
    ]

    return ParseTaskListResponse(tasks=task_list, total=len(task_list))


@router.post(
    "/stop",
    response_model=StopParseResponse,
    summary="Остановить парсинг",
    description="Остановить выполнение задачи парсинга",
)
async def stop_parsing(
    request: StopParseRequest,
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> StopParseResponse:
    """Остановить парсинг"""
    if request.task_id:
        # Остановить конкретную задачу
        success = await service.stop_parsing(request.task_id)
        if success:
            return StopParseResponse(
                stopped_tasks=[request.task_id],
                message=f"Задача {request.task_id} остановлена",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача {request.task_id} не найдена или уже завершена",
            )
    else:
        # Остановить все задачи (не реализовано в упрощенной версии)
        return StopParseResponse(
            stopped_tasks=[],
            message="Остановка всех задач не поддерживается",
        )


@router.get(
    "/stats",
    response_model=ParseStats,
    summary="Получить статистику",
    description="Получить статистику работы парсера",
)
async def get_stats(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseStats:
    """Получить статистику парсера"""
    stats = await service.get_stats()
    
    return ParseStats(
        total_tasks=stats["total_tasks"],
        completed_tasks=stats["completed_tasks"],
        failed_tasks=stats["failed_tasks"],
        running_tasks=stats["running_tasks"],
        success_rate=stats["success_rate"],
    )


@router.get(
    "/state",
    response_model=ParserState,
    summary="Получить состояние парсера",
    description="Получить общее состояние парсера",
)
async def get_parser_state(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParserState:
    """Получить состояние парсера"""
    stats = await service.get_stats()
    
    return ParserState(
        is_running=stats["running_tasks"] > 0,
        active_tasks=stats["running_tasks"],
        total_tasks_processed=stats["total_tasks"],
        total_posts_found=0,  # Не реализовано в упрощенной версии
        total_comments_found=0,  # Не реализовано в упрощенной версии
        last_activity=None,  # Не реализовано в упрощенной версии
    )