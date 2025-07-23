"""
API endpoints для парсинга комментариев VK
"""

from datetime import datetime
from typing import List, Optional

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
)
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentUpdateRequest,
    CommentWithKeywords,
    VKCommentResponse,
)
from app.services.parser_service import ParserService
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
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    service = ParserService(db, vk_service)
    return await service.start_parsing_task(task_data, parser_manager)


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
    )

    vk_service = VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    parser_service = ParserService(db, vk_service)

    return await parser_service.filter_comments(search_params, pagination)


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> CommentWithKeywords:
    vk_service = VKAPIService(token="stub", api_version="5.131")
    service = ParserService(db, vk_service)
    return await service.get_comment_with_keywords(comment_id)


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
            comment.viewed_at = datetime.now(timezone.utc).replace(tzinfo=None)
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
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    service = ParserService(db, vk_service)
    return service._convert_comment_to_response(comment)


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
    vk_service = VKAPIService(token="stub", api_version="5.131")
    service = ParserService(db, vk_service)
    return await service.get_global_stats()


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
