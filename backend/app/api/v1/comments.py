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
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_comment import VKCommentResponse

router = APIRouter(tags=["Comments"])
logger = structlog.get_logger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def get_comments(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse:
    """Получить список всех найденных комментариев"""

    # Загружаем комментарии с связанными ключевыми словами
    query = (
        select(VKComment)
        .options(
            selectinload(VKComment.keyword_matches).selectinload(
                CommentKeywordMatch.keyword
            )
        )
        .order_by(VKComment.created_at.desc())
    )

    # Подсчёт общего количества
    total_result = await db.execute(select(VKComment))
    total = len(total_result.scalars().all())

    # Получение данных с пагинацией
    paginated_query = query.offset(pagination.skip).limit(pagination.size)
    result = await db.execute(paginated_query)
    comments = result.scalars().all()

    # Преобразуем в ответы с ключевыми словами
    comment_responses = []
    for comment in comments:
        comment_data = VKCommentResponse.model_validate(comment)

        # Добавляем найденные ключевые слова
        matched_keywords = []
        if comment.keyword_matches:
            logger.info(
                f"Comment {comment.id} has {len(comment.keyword_matches)} keyword matches"
            )
            for match in comment.keyword_matches:
                if match.keyword:
                    # Добавляем только слово ключевого слова
                    matched_keywords.append(match.keyword.word)
                    logger.info(f"Found keyword: {match.keyword.word}")
                else:
                    logger.warning(f"Match {match.id} has no keyword")
        else:
            logger.info(f"Comment {comment.id} has no keyword matches")

        # Добавляем поле matched_keywords к ответу
        comment_dict = comment_data.model_dump()
        comment_dict["matched_keywords"] = matched_keywords

        comment_responses.append(comment_dict)

    return PaginatedResponse(
        total=total,
        page=pagination.page,
        size=pagination.size,
        items=comment_responses,
    )


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
