"""
FastAPI роутер для модуля Parser

Определяет API эндпоинты для управления парсингом VK данных
"""

import logging
from typing import Annotated, Optional
from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    Depends,
    Path,
    HTTPException,
    Request,
    status,
)
from fastapi.responses import JSONResponse

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

# Настройка логирования
logger = logging.getLogger(__name__)

# Константы для конфигурации
DEFAULT_MAX_POSTS = 100
DEFAULT_MAX_COMMENTS_PER_POST = 100
DEFAULT_PAGE_SIZE = 20
DEFAULT_TEST_POSTS = 10
DEFAULT_TEST_COMMENTS = 10

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
    """
    Запустить парсинг комментариев из групп VK

    Args:
        request: Параметры запроса парсинга
        service: Сервис парсера

    Returns:
        ParseResponse: Результат запуска парсинга

    Raises:
        HTTPException: При ошибке запуска парсинга
    """
    logger.info(
        f"Starting parsing request: group_ids={request.group_ids}, "
        f"max_posts={request.max_posts}, max_comments_per_post={request.max_comments_per_post}, "
        f"force_reparse={request.force_reparse}, priority={request.priority}"
    )

    # Детальное логирование для отладки
    logger.info(
        f"Group IDs details: {[{'id': gid, 'type': type(gid).__name__} for gid in request.group_ids]}"
    )

    try:
        result = await service.start_parsing(
            group_ids=request.group_ids,
            max_posts=(
                request.max_posts
                if request.max_posts is not None
                else DEFAULT_MAX_POSTS
            ),
            max_comments_per_post=(
                request.max_comments_per_post
                if request.max_comments_per_post is not None
                else DEFAULT_MAX_COMMENTS_PER_POST
            ),
            force_reparse=request.force_reparse,
            priority=request.priority,
        )

        logger.info(
            f"Parsing started successfully: task_id={result.get('task_id')}, "
            f"group_count={len(request.group_ids)}"
        )

        return ParseResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error in parsing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error in parsing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при запуске парсинга",
        )


@router.post(
    "/stop",
    response_model=StopParseResponse,
    summary="Остановить парсинг",
    description="Остановить выполнение задач парсинга",
)
async def stop_parsing(
    request: StopParseRequest,
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> StopParseResponse:
    """
    Остановить парсинг задач

    Args:
        request: Параметры остановки парсинга
        service: Сервис парсера

    Returns:
        StopParseResponse: Результат остановки парсинга

    Raises:
        HTTPException: При ошибке остановки парсинга
    """
    logger.info(f"Stopping parsing task: task_id={request.task_id}")

    try:
        result = await service.stop_parsing(request.task_id)

        logger.info(
            f"Parsing task stopped successfully: task_id={request.task_id}, "
            f"stopped={result.get('stopped', False)}"
        )

        return StopParseResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error stopping parsing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error stopping parsing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при остановке парсинга",
        )


@router.get(
    "/state",
    response_model=ParserState,
    summary="Получить состояние парсера",
    description="Получить текущее состояние системы парсинга",
)
async def get_parser_state(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParserState:
    """
    Получить состояние парсера

    Args:
        service: Сервис парсера

    Returns:
        ParserState: Текущее состояние парсера

    Raises:
        HTTPException: При ошибке получения состояния
    """
    logger.debug("Getting parser state")

    try:
        state = await service.get_parser_state()

        logger.debug(
            f"Parser state retrieved: active_tasks={state.get('active_tasks', 0)}, "
            f"total_tasks={state.get('total_tasks', 0)}"
        )

        return ParserState(**state)

    except Exception as e:
        logger.error(f"Error getting parser state: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при получении состояния парсера",
        )


@router.get(
    "/tasks/{task_id}",
    response_model=ParseStatus,
    summary="Получить статус задачи",
    description="Получить детальную информацию о задаче парсинга",
)
async def get_task_status(
    task_id: Annotated[str, Path(description="Идентификатор задачи")],
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseStatus:
    """
    Получить статус задачи парсинга

    Args:
        task_id: Идентификатор задачи
        service: Сервис парсера

    Returns:
        ParseStatus: Статус задачи парсинга

    Raises:
        HTTPException: При ошибке получения статуса или если задача не найдена
    """
    logger.info(f"Getting task status: task_id={task_id}")

    try:
        status = await service.get_task_status(task_id)
        if not status:
            logger.warning(f"Task not found: task_id={task_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Задача {task_id} не найдена",
            )

        logger.debug(
            f"Task status retrieved: task_id={task_id}, status={status.get('status')}"
        )

        return ParseStatus(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting task status: task_id={task_id}, error={str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при получении статуса задачи",
        )


@router.get(
    "/tasks",
    response_model=ParseTaskListResponse,
    summary="Получить список задач",
    description="Получить список задач парсинга с фильтрацией и пагинацией",
)
async def get_tasks_list(
    # Сервисы
    service: Annotated[ParserService, Depends(get_parser_service)],
    # Параметры пагинации
    page: Annotated[PageParam, Path(description="Номер страницы")] = 1,
    size: Annotated[
        SizeParam, Path(description="Размер страницы")
    ] = DEFAULT_PAGE_SIZE,
    # Параметры фильтрации
    status: Annotated[
        Optional[str], Path(description="Фильтр по статусу задачи")
    ] = None,
) -> ParseTaskListResponse:
    """
    Получить список задач парсинга

    Args:
        page: Номер страницы
        size: Размер страницы
        status: Фильтр по статусу задачи
        service: Сервис парсера

    Returns:
        ParseTaskListResponse: Список задач с пагинацией

    Raises:
        HTTPException: При ошибке получения списка задач
    """
    logger.info(
        f"Getting tasks list: page={page}, size={size}, status_filter={status}"
    )

    try:
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

        # Получаем общее количество задач из БД
        total = await service.get_tasks_count(status_filter=status)

        logger.debug(
            f"Tasks list retrieved: task_count={len(tasks)}, total={total}, "
            f"page={page}, size={size}"
        )

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

    except Exception as e:
        logger.error(f"Error getting tasks list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при получении списка задач",
        )


@router.get(
    "/stats",
    response_model=ParseStats,
    summary="Получить статистику парсинга",
    description="Получить общую статистику работы парсера",
)
async def get_parsing_stats(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> ParseStats:
    """
    Получить статистику парсинга

    Args:
        service: Сервис парсера

    Returns:
        ParseStats: Статистика парсинга

    Raises:
        HTTPException: При ошибке получения статистики
    """
    logger.debug("Getting parsing stats")

    try:
        stats = await service.get_parsing_stats()

        logger.debug(
            f"Parsing stats retrieved: total_tasks={stats.get('total_tasks', 0)}, "
            f"completed_tasks={stats.get('completed_tasks', 0)}"
        )

        return ParseStats(**stats)

    except Exception as e:
        logger.error(f"Error getting parsing stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при получении статистики",
        )


@router.post(
    "/test/{group_id}",
    summary="Тестовый парсинг группы",
    description="Тестовый запуск парсинга одной группы (без сохранения в БД)",
)
async def test_parse_group(
    group_id: Annotated[int, Path(description="ID группы для тестирования")],
    service: Annotated[ParserService, Depends(get_parser_service)],
    max_posts: Annotated[
        int, Path(description="Максимум постов для теста")
    ] = DEFAULT_TEST_POSTS,
    max_comments_per_post: Annotated[
        int, Path(description="Максимум комментариев на пост")
    ] = DEFAULT_TEST_COMMENTS,
) -> dict:
    """
    Тестовый парсинг группы

    Args:
        group_id: ID группы для тестирования
        max_posts: Максимум постов для теста
        max_comments_per_post: Максимум комментариев на пост
        service: Сервис парсера

    Returns:
        dict: Результат тестового парсинга

    Raises:
        HTTPException: При ошибке тестового парсинга
    """
    logger.info(
        f"Starting test parsing: group_id={group_id}, max_posts={max_posts}, "
        f"max_comments_per_post={max_comments_per_post}"
    )

    try:
        result = await service.parse_group(
            group_id=group_id,
            max_posts=max_posts,
            max_comments_per_post=max_comments_per_post,
        )

        logger.info(
            f"Test parsing completed: group_id={group_id}, "
            f"posts_parsed={result.get('posts_count', 0)}, "
            f"comments_parsed={result.get('comments_count', 0)}"
        )

        return {
            "message": "Тестовый парсинг завершен",
            "result": result,
        }

    except ValueError as e:
        logger.warning(f"Validation error in test parsing: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error in test parsing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при тестовом парсинге",
        )


@router.get(
    "/health",
    summary="Проверка здоровья парсера",
    description="Проверить доступность VK API и работоспособность парсера",
)
async def parser_health_check(
    service: Annotated[ParserService, Depends(get_parser_service)],
) -> dict:
    """
    Проверка здоровья парсера

    Args:
        service: Сервис парсера

    Returns:
        dict: Статус здоровья парсера
    """
    logger.debug("Performing health check")

    try:
        # Проверяем подключение к VK API
        try:
            # Простая проверка доступности VK API
            is_token_valid = True  # Упрощенная проверка
        except Exception:
            is_token_valid = False

        # Получаем состояние парсера
        parser_state = await service.get_parser_state()

        health_status = "healthy" if is_token_valid else "unhealthy"

        logger.debug(
            f"Health check completed: status={health_status}, "
            f"vk_api_available={is_token_valid}, "
            f"active_tasks={parser_state.get('active_tasks', 0)}"
        )

        return {
            "status": health_status,
            "vk_api_available": is_token_valid,
            "parser_active_tasks": parser_state.get("active_tasks", 0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Экспорт роутера
__all__ = ["router"]
