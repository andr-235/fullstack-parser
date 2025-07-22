"""
API endpoints для парсинга комментариев VK
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    vk_service = VKBottleService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    service = ParserService(db, vk_service)
    return await service.start_parsing_task(task_data, parser_manager)


@router.get("/comments", response_model=PaginatedResponse[VKCommentResponse])
async def get_comments(
    group_id: Optional[int] = None,
    keyword_id: Optional[int] = None,
    author_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VKCommentResponse]:
    """Получить отфильтрованные комментарии"""
    vk_service = VKAPIService(
        token=settings.vk.access_token, api_version=settings.vk.api_version
    )
    service = ParserService(db, vk_service)

    # Создаем объект параметров поиска
    search_params = CommentSearchParams(
        group_id=group_id,
        keyword_id=keyword_id,
        author_id=author_id,
        date_from=date_from,
        date_to=date_to,
    )

    # Получаем отфильтрованные комментарии
    result = await service.filter_comments(search_params, pagination)

    # Загружаем связанные ключевые слова для каждого комментария
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    import structlog

    from app.models.comment_keyword_match import CommentKeywordMatch
    from app.models.vk_comment import VKComment

    logger = structlog.get_logger()
    logger.info("Начинаем загрузку ключевых слов для комментариев")

    try:
        # Получаем комментарии с ключевыми словами
        comment_ids = [item.id for item in result.items]
        logger.info(
            "Загружаем ключевые слова для комментариев",
            comment_ids=comment_ids,
        )

        # Загружаем комментарии с ключевыми словами одним запросом
        query = (
            select(VKComment)
            .options(
                selectinload(VKComment.keyword_matches).selectinload(
                    CommentKeywordMatch.keyword
                )
            )
            .where(VKComment.id.in_(comment_ids))
        )
        comments_result = await db.execute(query)
        comments = comments_result.scalars().all()

        logger.info(
            "Загружены комментарии с ключевыми словами",
            total_comments=len(comments),
            comment_ids=comment_ids,
        )

        # Создаем словарь комментариев с ключевыми словами
        comments_dict = {}
        for comment in comments:
            matched_keywords = []
            logger.info(
                "Обрабатываем комментарий",
                comment_id=comment.id,
                has_keyword_matches=bool(comment.keyword_matches),
                matches_count=(
                    len(comment.keyword_matches)
                    if comment.keyword_matches
                    else 0
                ),
            )
            if comment.keyword_matches:
                logger.info(
                    "Найдены ключевые слова для комментария",
                    comment_id=comment.id,
                    matches_count=len(comment.keyword_matches),
                )
                for match in comment.keyword_matches:
                    logger.info(
                        "Обрабатываем совпадение",
                        comment_id=comment.id,
                        match_id=match.id,
                        has_keyword=bool(match.keyword),
                        keyword_word=(
                            match.keyword.word if match.keyword else None
                        ),
                    )
                    if match.keyword:
                        # Добавляем только слово ключевого слова как строку
                        matched_keywords.append(match.keyword.word)
            comments_dict[comment.id] = matched_keywords

        logger.info(
            "Создан словарь ключевых слов",
            comments_with_keywords=len(comments_dict),
            total_keywords=sum(len(kw) for kw in comments_dict.values()),
        )

        # Обновляем ответы с ключевыми словами
        updated_items = []
        for item in result.items:
            item_dict = item.model_dump()
            matched_keywords = comments_dict.get(item.id, [])
            item_dict["matched_keywords"] = matched_keywords
            updated_items.append(VKCommentResponse(**item_dict))

        logger.info("Комментарии обновлены с ключевыми словами")

        return PaginatedResponse(
            total=result.total,
            page=result.page,
            size=result.size,
            items=updated_items,
        )
    except Exception as e:
        logger.error(f"Ошибка при загрузке ключевых слов: {e}")
        # Возвращаем результат без ключевых слов в случае ошибки
        return PaginatedResponse(
            total=result.total,
            page=result.page,
            size=result.size,
            items=result.items,
        )


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> CommentWithKeywords:
    vk_service = VKAPIService(token="stub", api_version="5.131")
    service = ParserService(db, vk_service)
    return await service.get_comment_with_keywords(comment_id)


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
