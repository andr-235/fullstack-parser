"""
FastAPI роутер для модуля Comments

Определяет API эндпоинты для работы с комментариями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request

from .dependencies import get_comment_service
from .handlers import CommentHandlers
from .schemas import (
    CommentResponse,
    CommentListResponse,
    CommentCreate,
    CommentUpdate,
    CommentFilter,
    CommentStats,
    CommentBulkAction,
    CommentBulkResponse,
)
from ..pagination import (
    PageParam,
    SizeParam,
    SearchParam,
)
from ..infrastructure.celery_service import celery_service

# Схемы для Celery задач
from pydantic import BaseModel
from typing import Any, Dict, Optional


class TaskEnqueueRequest(BaseModel):
    """Схема для запроса постановки задачи в очередь"""

    function_name: str
    args: Optional[list] = None
    kwargs: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """Схема для ответа со статусом задачи"""

    job_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


from ..responses import APIResponse

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
    responses={
        404: {"description": "Комментарий не найден"},
        422: {"description": "Ошибка валидации данных"},
        500: {"description": "Внутренняя ошибка сервера"},
    },
)


@router.get(
    "/",
    response_model=CommentListResponse,
    summary="Получить список комментариев",
    description="Получить список комментариев с фильтрацией и пагинацией",
)
async def get_comments(
    # Параметры пагинации
    page: PageParam = 1,
    size: SizeParam = 20,
    # Параметры фильтрации
    group_id: Optional[str] = Query(
        None, description="ID группы VK для фильтрации"
    ),
    post_id: Optional[str] = Query(
        None, description="ID поста для фильтрации"
    ),
    is_viewed: Optional[bool] = Query(
        None, description="Фильтр по статусу просмотра"
    ),
    is_archived: Optional[bool] = Query(
        None, description="Фильтр по статусу архивирования"
    ),
    search: SearchParam = None,
    # Сервисы
    service=Depends(get_comment_service),
) -> CommentListResponse:
    """Получить список комментариев с фильтрацией и пагинацией"""
    handlers = CommentHandlers(service)
    return await handlers.get_comments(
        page=page,
        size=size,
        group_id=group_id,
        post_id=post_id,
        is_viewed=is_viewed,
        is_archived=is_archived,
        search=search,
    )


@router.get(
    "/search",
    response_model=CommentListResponse,
    summary="Поиск комментариев",
    description="Поиск комментариев по тексту с фильтрацией",
)
async def search_comments(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    group_id: Optional[str] = Query(
        None, description="Ограничить поиск группой"
    ),
    is_viewed: Optional[bool] = Query(
        None, description="Фильтр по статусу просмотра"
    ),
    is_archived: Optional[bool] = Query(
        None, description="Фильтр по статусу архивирования"
    ),
    has_keywords: Optional[bool] = Query(
        None, description="Фильтр по наличию ключевых слов"
    ),
    page: PageParam = 1,
    size: SizeParam = 20,
    service=Depends(get_comment_service),
) -> CommentListResponse:
    """Поиск комментариев по тексту"""
    handlers = CommentHandlers(service)
    return await handlers.search_comments(
        q=q,
        group_id=group_id,
        is_viewed=is_viewed,
        is_archived=is_archived,
        has_keywords=has_keywords,
        page=page,
        size=size,
    )


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Получить комментарий по ID",
    description="Получить детальную информацию о комментарии",
)
async def get_comment(
    comment_id: int,
    service=Depends(get_comment_service),
) -> CommentResponse:
    """Получить комментарий по ID"""
    handlers = CommentHandlers(service)
    return await handlers.get_comment(comment_id)


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=201,
    summary="Создать новый комментарий",
    description="Создать новый комментарий в системе",
)
async def create_comment(
    comment_data: CommentCreate,
    service=Depends(get_comment_service),
) -> CommentResponse:
    """Создать новый комментарий"""
    handlers = CommentHandlers(service)
    return await handlers.create_comment(comment_data)


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Обновить комментарий",
    description="Обновить информацию о комментарии",
)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    service=Depends(get_comment_service),
) -> CommentResponse:
    """Обновить комментарий"""
    handlers = CommentHandlers(service)
    return await handlers.update_comment(comment_id, comment_data)


@router.delete(
    "/{comment_id}",
    status_code=204,
    summary="Удалить комментарий",
    description="Удалить комментарий из системы",
)
async def delete_comment(
    comment_id: int,
    service=Depends(get_comment_service),
):
    """Удалить комментарий"""
    handlers = CommentHandlers(service)
    await handlers.delete_comment(comment_id)


@router.post(
    "/{comment_id}/view",
    response_model=CommentResponse,
    summary="Отметить комментарий как просмотренный",
    description="Отметить комментарий как просмотренный и обновить время обработки",
)
async def mark_comment_as_viewed(
    comment_id: int,
    service=Depends(get_comment_service),
) -> CommentResponse:
    """Отметить комментарий как просмотренный"""
    handlers = CommentHandlers(service)
    return await handlers.mark_comment_as_viewed(comment_id)


@router.post(
    "/bulk/view",
    response_model=CommentBulkResponse,
    summary="Массовое отмечание комментариев",
    description="Отметить несколько комментариев как просмотренные",
)
async def bulk_mark_as_viewed(
    action_data: CommentBulkAction,
    service=Depends(get_comment_service),
) -> CommentBulkResponse:
    """Массовое отмечание комментариев как просмотренные"""
    handlers = CommentHandlers(service)
    return await handlers.bulk_mark_as_viewed(action_data)


@router.get(
    "/stats/{group_id}",
    response_model=CommentStats,
    summary="Получить статистику комментариев группы",
    description="Получить статистику комментариев для указанной группы",
)
async def get_group_stats(
    group_id: str,
    service=Depends(get_comment_service),
) -> CommentStats:
    """Получить статистику комментариев группы"""
    handlers = CommentHandlers(service)
    return await handlers.get_group_stats(group_id)


# Celery интеграция - асинхронные задачи для комментариев


@router.post(
    "/parse/vk/async",
    summary="Асинхронный парсинг комментариев VK",
    description="""
    Запускает асинхронный парсинг комментариев VK через Celery.

    **Пример использования:**
    ```json
    {
        "function_name": "parse_vk_comments",
        "args": [12345, null, 100],
        "kwargs": {"limit": 100}
    }
    ```

    **Доступные функции:**
    - `parse_vk_comments` - парсинг комментариев VK
    - `analyze_text_morphology` - морфологический анализ
    - `extract_keywords` - извлечение ключевых слов
    """,
)
async def parse_comments_async(
    group_id: int = Query(..., description="ID группы VK"),
    post_id: Optional[int] = Query(None, description="ID поста (опционально)"),
    limit: int = Query(
        100, description="Максимальное количество комментариев"
    ),
) -> APIResponse:
    """
    Асинхронный парсинг комментариев VK

    Добавляет задачу парсинга в очередь Celery и возвращает ID задачи.
    """
    try:
        # Добавляем задачу в очередь
        job_id = celery_service.enqueue_job(
            "celery_tasks.parse_vk_comments",
            group_id=group_id,
            post_id=post_id,
            limit=limit,
        )

        if not job_id:
            raise HTTPException(
                status_code=500, detail="Не удалось добавить задачу в очередь"
            )

        return APIResponse(
            success=True,
            message="Задача парсинга добавлена в очередь",
            data={
                "job_id": job_id,
                "function": "parse_vk_comments",
                "group_id": group_id,
                "post_id": post_id,
                "limit": limit,
                "job_id": job_id,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка запуска парсинга: {str(e)}"
        )


@router.post(
    "/analyze/async",
    summary="Асинхронный анализ комментариев",
    description="Запускает пакетный анализ комментариев через Celery",
)
async def analyze_comments_async(
    comment_ids: List[int] = Query(
        ..., description="Список ID комментариев для анализа"
    ),
    analysis_type: str = Query(
        "morphology",
        description="Тип анализа: morphology, keywords, sentiment",
    ),
) -> APIResponse:
    """
    Асинхронный анализ комментариев

    Добавляет задачу анализа в очередь Celery.
    """
    try:
        if analysis_type == "morphology":
            function_name = "process_batch_comments"
            operation = "analyze"
        elif analysis_type == "keywords":
            function_name = "extract_keywords"
            operation = "keywords"
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый тип анализа: {analysis_type}",
            )

        # Добавляем задачу в очередь
        job_id = celery_service.enqueue_job(
            "celery_tasks.process_batch_comments",
            comment_ids=comment_ids,
            operation=operation,
        )

        if not job_id:
            raise HTTPException(
                status_code=500, detail="Не удалось добавить задачу в очередь"
            )

        return APIResponse(
            success=True,
            message=f"Задача {analysis_type} анализа добавлена в очередь",
            data={
                "job_id": job_id,
                "function": function_name,
                "comment_count": len(comment_ids),
                "analysis_type": analysis_type,
                "job_id": job_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка запуска анализа: {str(e)}"
        )


@router.post(
    "/report/async",
    summary="Асинхронная генерация отчета",
    description="Запускает генерацию отчета по комментариям через Celery",
)
async def generate_report_async(
    report_type: str = Query(
        ..., description="Тип отчета: comments, keywords, groups"
    ),
    group_id: Optional[str] = Query(
        None, description="ID группы для фильтрации"
    ),
    date_from: str = Query(
        ..., description="Дата начала периода (YYYY-MM-DD)"
    ),
    date_to: str = Query(
        ..., description="Дата окончания периода (YYYY-MM-DD)"
    ),
) -> APIResponse:
    """
    Асинхронная генерация отчета

    Добавляет задачу генерации отчета в очередь Celery.
    """
    try:
        # Валидация дат
        from datetime import datetime

        try:
            datetime.fromisoformat(date_from)
            datetime.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный формат даты. Используйте YYYY-MM-DD",
            )

        # Добавляем задачу в очередь
        job_id = celery_service.enqueue_job(
            "celery_tasks.generate_report",
            report_type=report_type,
            date_from=date_from,
            date_to=date_to,
            filters={"group_id": group_id} if group_id else {},
        )

        if not job_id:
            raise HTTPException(
                status_code=500, detail="Не удалось добавить задачу в очередь"
            )

        return APIResponse(
            success=True,
            message="Задача генерации отчета добавлена в очередь",
            data={
                "job_id": job_id,
                "function": "generate_report",
                "report_type": report_type,
                "date_from": date_from,
                "date_to": date_to,
                "group_id": group_id,
                "job_id": job_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запуска генерации отчета: {str(e)}",
        )


@router.post(
    "/cleanup/async",
    summary="Асинхронная очистка старых данных",
    description="Запускает очистку старых комментариев через Celery",
)
async def cleanup_comments_async(
    days_old: int = Query(30, description="Удалить данные старше N дней"),
    data_types: List[str] = Query(
        ["comments", "logs"], description="Типы данных для очистки"
    ),
) -> APIResponse:
    """
    Асинхронная очистка старых данных

    Добавляет задачу очистки в очередь Celery.
    """
    try:
        # Добавляем задачу в очередь
        job_id = celery_service.enqueue_job(
            "celery_tasks.cleanup_old_data",
            days_old=days_old,
            data_types=data_types,
        )

        if not job_id:
            raise HTTPException(
                status_code=500, detail="Не удалось добавить задачу в очередь"
            )

        return APIResponse(
            success=True,
            message="Задача очистки данных добавлена в очередь",
            data={
                "job_id": job_id,
                "function": "cleanup_old_data",
                "days_old": days_old,
                "data_types": data_types,
                "job_id": job_id,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка запуска очистки: {str(e)}"
        )


@router.get(
    "/task/{job_id}/status",
    summary="Получить статус задачи",
    description="Получить текущий статус выполнения задачи по ID",
)
async def get_task_status(job_id: str) -> TaskStatusResponse:
    """
    Получить статус задачи по ID

    Возвращает информацию о выполнении задачи Celery.
    """
    try:
        status_info = celery_service.get_job_status(job_id)

        if not status_info:
            raise HTTPException(status_code=404, detail="Задача не найдена")

        return TaskStatusResponse(**status_info)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения статуса задачи: {str(e)}",
        )


# Экспорт роутера
__all__ = ["router"]
