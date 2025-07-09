"""
API endpoints для парсинга комментариев VK
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.keyword import Keyword
from app.models.user import User
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
from app.models.vk_post import VKPost
from app.schemas.base import PaginatedResponse, PaginationParams, StatusResponse
from app.schemas.parser import (
    GlobalStats,
    ParserState,
    ParserStats,
    ParseTaskCreate,
    ParseTaskResponse,
)
from app.schemas.vk_comment import (
    CommentSearchParams,
    CommentWithKeywords,
    VKCommentResponse,
)
from app.services.arq_enqueue import enqueue_run_parsing_task
from app.services.group_service import GroupService
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import (
    RedisParserManager,
    get_redis_parser_manager,
)
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["Parser"])


@router.post("/parse", response_model=ParseTaskResponse)
async def start_parsing(
    task_data: ParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user),
    parser_manager: RedisParserManager = Depends(get_redis_parser_manager),
) -> ParseTaskResponse:
    """Запустить парсинг комментариев для группы"""

    # Проверяем, что группа существует
    result = await db.execute(select(VKGroup).where(VKGroup.id == task_data.group_id))
    group = result.scalar_one_or_none()

    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Группа не найдена"
        )

    if not group.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Группа неактивна"
        )

    # Создаём ID задачи
    task_id = f"parse_{group.id}_{int(datetime.now().timestamp())}"

    # Создаём базовый объект задачи и регистрируем его в менеджере
    task_response = ParseTaskResponse(
        task_id=task_id,
        group_id=task_data.group_id,
        group_name=group.name,
        status="running",
        progress=0.0,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        stats=None,
        error_message=None,
    )

    await parser_manager.start_task(task_response)

    # Запускаем парсинг в фоне через Arq
    # Запускаем парсинг в фоне через Arq
    await enqueue_run_parsing_task(
        group_id=task_data.group_id,
        max_posts=task_data.max_posts,
        force_reparse=task_data.force_reparse,
        job_id=task_id,
    )

    return task_response


@router.get("/comments", response_model=PaginatedResponse)
async def get_comments(
    search_params: CommentSearchParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Получить список найденных комментариев с фильтрацией"""

    query = select(VKComment).options(
        selectinload(VKComment.post).selectinload(VKPost.group)
    )

    # Применяем фильтры
    if search_params.group_id:
        query = query.join(VKComment.post).where(
            VKComment.post.has(group_id=search_params.group_id)
        )

    if search_params.keyword_id:
        query = query.join(VKComment.keyword_matches).where(
            VKComment.keyword_matches.any(keyword_id=search_params.keyword_id)
        )

    if search_params.author_id:
        query = query.where(VKComment.author_id == search_params.author_id)

    if search_params.date_from:
        query = query.where(VKComment.published_at >= search_params.date_from)

    if search_params.date_to:
        query = query.where(VKComment.published_at <= search_params.date_to)

    # Только обработанные комментарии с найденными ключевыми словами
    query = query.where(
        and_(VKComment.is_processed, VKComment.matched_keywords_count > 0)
    )

    # Сортировка по дате
    query = query.order_by(desc(VKComment.published_at))

    # Подсчёт общего количества
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # Получение данных с пагинацией
    paginated_query = query.offset(pagination.skip).limit(pagination.size)
    result = await db.execute(paginated_query)
    comments = result.scalars().all()

    items = []
    for comment in comments:
        group = None
        post_vk_id = None
        if comment.post and comment.post.group:
            from app.schemas.vk_group import VKGroupResponse

            group = VKGroupResponse.model_validate(comment.post.group)
            post_vk_id = comment.post.vk_id
        comment_data = VKCommentResponse.model_validate(comment)
        comment_data.group = group
        comment_data.post_vk_id = post_vk_id
        items.append(comment_data)

    return PaginatedResponse(
        total=total,
        page=pagination.page,
        size=pagination.size,
        items=items,
    )


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> CommentWithKeywords:
    """Получить комментарий с детальной информацией о найденных ключевых словах"""

    result = await db.execute(
        select(VKComment)
        .where(VKComment.id == comment_id)
        .options(selectinload(VKComment.keyword_matches))
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден"
        )

    # Формируем список найденных ключевых слов
    matched_keywords = []
    keyword_matches = []

    for match in comment.keyword_matches:
        matched_keywords.append(match.keyword.word)
        keyword_matches.append(
            {
                "keyword": match.keyword.word,
                "matched_text": match.matched_text,
                "position": match.match_position,
                "context": match.match_context,
            }
        )

    comment_data = VKCommentResponse.model_validate(comment)

    return CommentWithKeywords(
        **comment_data.model_dump(),
        matched_keywords=matched_keywords,
        keyword_matches=keyword_matches,
    )


@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(
    db: AsyncSession = Depends(get_db),
) -> GlobalStats:
    """Получить общую статистику системы"""

    # Количество групп
    groups_result = await db.execute(select(func.count(VKGroup.id)))
    total_groups = groups_result.scalar()

    active_groups_result = await db.execute(
        select(func.count(VKGroup.id)).where(VKGroup.is_active)
    )
    active_groups = active_groups_result.scalar()

    # Количество ключевых слов
    keywords_result = await db.execute(select(func.count(Keyword.id)))
    total_keywords = keywords_result.scalar()

    active_keywords_result = await db.execute(
        select(func.count(Keyword.id)).where(Keyword.is_active)
    )
    active_keywords = active_keywords_result.scalar()

    # Количество комментариев
    comments_result = await db.execute(select(func.count(VKComment.id)))
    total_comments = comments_result.scalar()

    comments_with_keywords_result = await db.execute(
        select(func.count(VKComment.id)).where(VKComment.matched_keywords_count > 0)
    )
    comments_with_keywords = comments_with_keywords_result.scalar()

    # Последнее время парсинга
    last_parse_result = await db.execute(
        select(func.max(VKGroup.last_parsed_at)).where(
            VKGroup.last_parsed_at.isnot(None)
        )
    )
    last_parse_time = last_parse_result.scalar()

    return GlobalStats(
        total_groups=total_groups or 0,
        active_groups=active_groups or 0,
        total_keywords=total_keywords or 0,
        active_keywords=active_keywords or 0,
        total_comments=total_comments or 0,
        comments_with_keywords=comments_with_keywords or 0,
        last_parse_time=last_parse_time,
    )


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
    tasks, total = await manager.list_tasks(skip=pagination.skip, limit=pagination.size)

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
        status="stopped" if stopped else "not_stopped", message="Парсер остановлен"
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
