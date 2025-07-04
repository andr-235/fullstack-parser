"""
API endpoints для управления комментариями
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_async_session
from app.models.vk_comment import VKComment
from app.schemas.base import PaginatedResponse, PaginationParams
from app.schemas.vk_comment import VKCommentResponse

router = APIRouter(tags=["Comments"])


@router.get("/", response_model=PaginatedResponse)
async def get_comments(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse:
    """Получить список всех найденных комментариев"""

    query = select(VKComment).order_by(VKComment.created_at.desc())

    # Подсчёт общего количества
    total_result = await db.execute(select(VKComment))
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
