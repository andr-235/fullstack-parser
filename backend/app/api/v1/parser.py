"""
API endpoints для парсинга комментариев VK
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_session
from app.models.keyword import Keyword
from app.models.vk_comment import VKComment
from app.models.vk_group import VKGroup
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
from app.services.parser_manager import get_parser_manager
from app.services.parser_service import ParserService

router = APIRouter(tags=["Parser"])


@router.post("/parse", response_model=ParseTaskResponse)
async def start_parsing(
    task_data: ParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
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
        started_at=datetime.now(),
        completed_at=None,
        stats=None,
        error_message=None,
    )

    parser_manager = get_parser_manager()
    parser_manager.start_task(task_response)

    # Запускаем парсинг в фоне
    background_tasks.add_task(
        run_parsing_task,
        task_id=task_id,
        group_id=task_data.group_id,
        max_posts=task_data.max_posts,
    )

    return task_response


async def run_parsing_task(
    task_id: str, group_id: int, max_posts: Optional[int] = None
) -> None:
    """Background задача для парсинга"""
    from app.core.database import AsyncSessionLocal

    manager = get_parser_manager()

    async with AsyncSessionLocal() as db:
        parser = ParserService(db)
        try:
            stats_dict = await parser.parse_group_comments(group_id, max_posts)

            # Обновляем задачу в менеджере
            manager.complete_task(task_id, stats_dict)

        except Exception as exc:
            manager.fail_task(task_id, str(exc))


@router.get("/comments", response_model=PaginatedResponse)
async def get_comments(
    search_params: CommentSearchParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse:
    """Получить список найденных комментариев с фильтрацией"""

    query = select(VKComment)

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
    paginated_query = query.offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(paginated_query)
    comments = result.scalars().all()

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=[VKCommentResponse.model_validate(comment) for comment in comments],
    )


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_async_session)
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
    db: AsyncSession = Depends(get_async_session),
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
async def get_parser_state() -> ParserState:
    """Получить текущее состояние парсера."""

    return get_parser_manager().get_state()


@router.get("/stats", response_model=ParserStats)
async def get_parser_stats() -> ParserStats:
    """Получить агрегированную статистику парсера."""

    return get_parser_manager().get_stats()


@router.get("/tasks", response_model=PaginatedResponse)
async def get_parse_tasks(
    pagination: PaginationParams = Depends(),
) -> PaginatedResponse:
    """Получить список последних задач парсинга."""

    manager = get_parser_manager()
    tasks = manager.list_tasks(skip=pagination.skip, limit=pagination.limit)

    return PaginatedResponse(
        total=len(manager.list_tasks()),
        skip=pagination.skip,
        limit=pagination.limit,
        items=tasks,
    )


@router.post("/stop", response_model=StatusResponse)
async def stop_parser() -> StatusResponse:
    """Остановить текущий парсинг (best-effort)."""

    get_parser_manager().stop_current_task()
    return StatusResponse(success=True, message="Парсер остановлен")
