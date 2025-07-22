"""
API endpoints для управления комментариями
"""

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.comment_keyword_match import CommentKeywordMatch
from app.models.vk_comment import VKComment
from app.models.vk_post import VKPost
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_comment import VKCommentResponse

router = APIRouter(tags=["Comments"])
logger = structlog.get_logger(__name__)


async def get_comments_by_keyword(
    keyword: str,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Получение комментариев по ключевому слову.
    """
    # Implementation of get_comments_by_keyword method
    pass


async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Получение комментария по ID.
    """
    # Implementation of get_comment method
    pass
