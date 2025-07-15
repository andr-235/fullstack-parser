"""
API endpoints для парсинга комментариев VK
"""

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.schemas.vk_comment import CommentSearchParams, CommentWithKeywords
from app.services.parser_service import ParserService
from app.services.redis_parser_manager import (
    RedisParserManager,
    get_redis_parser_manager,
)
from app.services.vkbottle_service import VKBottleService

router = APIRouter(tags=["Parser"])


@router.post("/parse", response_model=ParseTaskResponse)
async def start_parsing(
    task_data: ParseTaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    parser_manager=Depends(get_redis_parser_manager),
) -> ParseTaskResponse:
    vk_service = VKBottleService(
        token="stub", api_version="5.131"
    )  # TODO: заменить на settings
    service = ParserService(db, vk_service)
    return await service.start_parsing_task(task_data, parser_manager)


@router.get("/comments", response_model=PaginatedResponse)
async def get_comments(
    search_params: CommentSearchParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    vk_service = VKBottleService(token="stub", api_version="5.131")
    service = ParserService(db, vk_service)
    return await service.filter_comments(search_params, pagination)


@router.get("/comments/{comment_id}", response_model=CommentWithKeywords)
async def get_comment_with_keywords(
    comment_id: int, db: AsyncSession = Depends(get_db)
) -> CommentWithKeywords:
    vk_service = VKBottleService(token="stub", api_version="5.131")
    service = ParserService(db, vk_service)
    return await service.get_comment_with_keywords(comment_id)


@router.get("/stats/global", response_model=GlobalStats)
async def get_global_stats(
    db: AsyncSession = Depends(get_db),
) -> GlobalStats:
    vk_service = VKBottleService(token="stub", api_version="5.131")
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
