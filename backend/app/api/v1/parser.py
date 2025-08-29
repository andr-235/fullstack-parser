"""
API endpoints для парсинга комментариев VK
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Union, Any, cast

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
)
from app.schemas.parser import (
    GlobalStats,
    ParserState,
    ParserStats,
    ParseTaskCreate,
    ParseTaskResponse,
    BulkParseTaskCreate,
    BulkParseResponse,
)
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentUpdateRequest,
    CommentWithKeywords,
    VKCommentResponse,
)
from app.services.parsing_manager import ParsingManager
from app.services.comment_search_service import CommentSearchService
from app.services.comment_service import CommentService
from app.services.redis_parser_manager import (
    RedisParserManager,
    get_redis_parser_manager,
)
from app.services.vk_api_service import VKAPIService

router = APIRouter(tags=["Parser"])


@router.post("/parse", response_model=ParseTaskResponse)
async def start_parsing(
    task_data: ParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    parser_manager=Depends(get_redis_parser_manager),
) -> ParseTaskResponse:
    """Запустить парсинг группы"""
    vk_service = VKAPIService(
        token=settings.vk_access_token, api_version=settings.vk_api_version
    )
    parsing_manager = ParsingManager(db, parser_manager)
    return await parsing_manager.start_parsing_task(
        group_id=task_data.group_id,
        max_posts=task_data.max_posts,
        keywords=task_data.keywords,
    )


@router.post("/parse/bulk", response_model=BulkParseResponse)
async def start_bulk_parsing(
    bulk_data: BulkParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    parser_manager=Depends(get_redis_parser_manager),
) -> BulkParseResponse:
    """Запустить парсинг всех активных групп"""
    from sqlalchemy import select
    from app.models.vk_group import VKGroup

    # Получаем все активные группы
    result = await db.execute(select(VKGroup).where(VKGroup.is_active == True))
    active_groups = result.scalars().all()

    if not active_groups:
        return BulkParseResponse(
            total_groups=0, started_tasks=0, failed_groups=[], tasks=[]
        )

    parsing_manager = ParsingManager(db, parser_manager)

    tasks: List[ParseTaskResponse] = []
    failed_groups: List[dict] = []

    # Ограничиваем количество одновременных задач
    max_concurrent = bulk_data.max_concurrent or 3
    semaphore = asyncio.Semaphore(max_concurrent)

    async def start_single_group_parsing(group):
        async with semaphore:
            try:
                task_data = ParseTaskCreate(
                    group_id=group.id,
                    max_posts=bulk_data.max_posts,
                    force_reparse=bulk_data.force_reparse,
                )
                task = await parsing_manager.start_parsing_task(
                    group_id=group.id,
                    max_posts=bulk_data.max_posts or 100,
                    keywords=bulk_data.keywords or [],
                )
                return task
            except Exception as e:
                failed_groups.append(
                    {
                        "group_id": group.id,
                        "group_name": group.name,
                        "error": str(e),
                    }
                )
                return None

    # Запускаем задачи для всех групп
    task_coroutines = [
        start_single_group_parsing(group) for group in active_groups
    ]
    task_results = await asyncio.gather(
        *task_coroutines, return_exceptions=True
    )

    # Обрабатываем результаты
    for i, task_result in enumerate(task_results):
        if isinstance(task_result, Exception):
            group = active_groups[i]
            failed_groups.append(
                {
                    "group_id": group.id,
                    "group_name": group.name,
                    "error": str(task_result),
                }
            )
        elif task_result is not None and not isinstance(
            task_result, Exception
        ):
            # Type cast to ensure linter understands this is ParseTaskResponse
            task_response = cast(ParseTaskResponse, task_result)
            tasks.append(task_response)

    return BulkParseResponse(
        total_groups=len(active_groups),
        started_tasks=len(tasks),
        failed_groups=failed_groups,
        tasks=tasks,
    )


@router.get("/comments", response_model=PaginatedResponse[VKCommentResponse])
async def get_comments(
    text: Optional[str] = None,
    group_id: Optional[int] = None,
    keyword_id: Optional[int] = None,
    author_id: Optional[int] = None,
    author_screen_name: Optional[List[str]] = Query(None),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    is_viewed: Optional[bool] = None,
    is_archived: Optional[bool] = None,
    order_by: Optional[str] = Query(
        "published_at", description="Поле для сортировки"
    ),
    order_dir: Optional[str] = Query(
        "desc", description="Направление сортировки (asc/desc)"
    ),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VKCommentResponse]:
    """Получает отфильтрованные комментарии с пагинацией"""
    search_params = CommentSearchParams(
        text=text,
        group_id=group_id,
        keyword_id=keyword_id,
        author_id=author_id,
        author_screen_name=author_screen_name,
        date_from=date_from,
        date_to=date_to,
        is_viewed=is_viewed,
        is_archived=is_archived,
        order_by=order_by,
        order_dir=order_dir,
    )

    search_service = CommentSearchService(db)

    return await search_service.search_comments(search_params)


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> CommentWithKeywords:
    comment_service = CommentService(db)
    return await comment_service.get_comment_with_keywords(comment_id)


@router.put("/comments/{comment_id}/status", response_model=VKCommentResponse)
async def update_comment_status(
    comment_id: int,
    status_update: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> VKCommentResponse:
    """Обновить статус комментария (просмотрен/архивирован)"""
    from datetime import datetime, timezone

    from sqlalchemy import select

    from app.models.vk_comment import VKComment

    # Получаем комментарий
    result = await db.execute(
        select(VKComment).where(VKComment.id == comment_id)
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден",
        )

    # Обновляем статус
    if status_update.is_viewed is not None:
        comment.is_viewed = status_update.is_viewed
        if status_update.is_viewed:
            comment.viewed_at = datetime.now(timezone.utc)
        else:
            comment.viewed_at = None

    if status_update.is_archived is not None:
        comment.is_archived = status_update.is_archived
        if status_update.is_archived:
            comment.archived_at = datetime.now(timezone.utc).replace(
                tzinfo=None
            )
        else:
            comment.archived_at = None

    await db.commit()
    await db.refresh(comment)

    # Конвертируем в ответ
    vk_service = VKAPIService(
        token=settings.vk_access_token, api_version=settings.vk_api_version
    )
    comment_service = CommentService(db)
    return await comment_service._convert_comment_to_response(comment)


@router.post("/comments/{comment_id}/view", response_model=VKCommentResponse)
async def mark_comment_as_viewed(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKCommentResponse:
    """Отметить комментарий как просмотренный"""
    return await update_comment_status(
        comment_id, CommentUpdateRequest(is_viewed=True), db
    )


@router.post(
    "/comments/{comment_id}/archive", response_model=VKCommentResponse
)
async def archive_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKCommentResponse:
    """Архивировать комментарий (отметить как просмотренный и архивированный)"""
    return await update_comment_status(
        comment_id, CommentUpdateRequest(is_viewed=True, is_archived=True), db
    )


@router.post(
    "/comments/{comment_id}/unarchive", response_model=VKCommentResponse
)
async def unarchive_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
) -> VKCommentResponse:
    """Разархивировать комментарий"""
    return await update_comment_status(
        comment_id, CommentUpdateRequest(is_archived=False), db
    )


@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(
    db: AsyncSession = Depends(get_db),
) -> GlobalStats:
    comment_service = CommentService(db)
    return await comment_service.get_global_stats()


# ---------------------------------------------------------------------------
# New management endpoints
# ---------------------------------------------------------------------------


@router.get("/state", response_model=ParserState)
async def get_parser_state(
    # current_user: User = Depends(get_current_user),
    parser_manager: RedisParserManager = Depends(get_redis_parser_manager),
) -> ParserState:
    """Получить текущее состояние парсера"""
    return await parser_manager.get_state()


@router.get("/stats", response_model=ParserStats)
async def get_parser_stats(
    # current_user: User = Depends(get_current_user),
    parser_manager: RedisParserManager = Depends(get_redis_parser_manager),
) -> ParserStats:
    """Получить статистику по последним задачам парсера"""
    stats = await parser_manager.get_stats()
    return stats


@router.get("/tasks", response_model=PaginatedResponse)
async def get_parse_tasks(
    pagination: PaginationParams = Depends(),
    manager: RedisParserManager = Depends(get_redis_parser_manager),
) -> PaginatedResponse:
    """Получить список задач парсинга с пагинацией."""
    tasks, total = await manager.list_tasks(
        skip=pagination.skip, limit=pagination.size
    )

    return PaginatedResponse(
        total=total,
        page=pagination.page,
        size=pagination.size,
        items=tasks,
    )


@router.post("/stop", response_model=StatusResponse)
async def stop_parser(
    # current_user: User = Depends(get_current_user),
    parser_manager: RedisParserManager = Depends(get_redis_parser_manager),
) -> StatusResponse:
    """Остановить текущую задачу парсинга"""
    stopped = parser_manager.stop_current_task()
    return StatusResponse(
        status="stopped" if stopped else "not_stopped",
        message="Парсер остановлен",
    )


@router.get("/history", response_model=List[ParseTaskResponse])
async def get_parsing_history(
    skip: int = 0,
    limit: int = 10,
    # current_user: User = Depends(get_current_user),
    parser_manager: RedisParserManager = Depends(get_redis_parser_manager),
):
    """Получить историю последних N запусков"""
    history = await parser_manager.list_tasks(skip=skip, limit=limit)
    return history
