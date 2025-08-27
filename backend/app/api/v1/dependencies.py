"""
Общие зависимости для API v1

Этот модуль содержит общие зависимости, используемые
в различных API эндпоинтах.
"""

from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)


# Типизированные аннотации для общих параметров
PageParam = Annotated[
    int,
    Query(default=1, ge=1, description="Номер страницы", examples=[1, 2, 3]),
]

SizeParam = Annotated[
    int,
    Query(
        default=20,
        ge=1,
        le=100,
        description="Размер страницы",
        examples=[10, 20, 50],
    ),
]

SearchParam = Annotated[
    Optional[str],
    Query(
        default=None,
        description="Поисковый запрос",
        examples=["поиск", "test"],
    ),
]

SortByParam = Annotated[
    Optional[str],
    Query(
        default=None,
        description="Поле для сортировки",
        examples=["created_at", "updated_at"],
    ),
]

SortOrderParam = Annotated[
    str,
    Query(
        default="desc",
        description="Порядок сортировки (asc/desc)",
        examples=["asc", "desc"],
    ),
]


def validate_sort_order(sort_order: str) -> str:
    """
    Валидирует параметр сортировки.

    Args:
        sort_order: Параметр сортировки

    Returns:
        str: Валидный параметр сортировки

    Raises:
        HTTPException: При невалидном параметре сортировки
    """
    if sort_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Параметр sort_order должен быть 'asc' или 'desc'",
        )
    return sort_order


def validate_pagination_params(page: int, size: int) -> tuple[int, int]:
    """
    Валидирует параметры пагинации.

    Args:
        page: Номер страницы
        size: Размер страницы

    Returns:
        tuple[int, int]: Валидные параметры пагинации

    Raises:
        HTTPException: При невалидных параметрах пагинации
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Номер страницы должен быть больше 0",
        )

    if size < 1 or size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер страницы должен быть от 1 до 100",
        )

    return page, size


async def get_db_session() -> AsyncSession:
    """
    Получить сессию базы данных.

    Returns:
        AsyncSession: Сессия базы данных
    """
    return await get_db()


# Общие зависимости для использования в эндпоинтах
CommonDB = Annotated[AsyncSession, Depends(get_db_session)]
CommonPage = Annotated[int, Depends(lambda: PageParam)]
CommonSize = Annotated[int, Depends(lambda: SizeParam)]
CommonSearch = Annotated[Optional[str], Depends(lambda: SearchParam)]
CommonSortBy = Annotated[Optional[str], Depends(lambda: SortByParam)]
CommonSortOrder = Annotated[str, Depends(lambda: SortOrderParam)]
