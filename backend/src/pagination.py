"""
Глобальные утилиты пагинации VK Comments Parser

Мигрировано из app/api/v1/dependencies.py
в соответствии с fastapi-best-practices
"""

from typing import Annotated, Optional, Any, Dict, List, TypeVar, Generic
from math import ceil
from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Стандартизированный ответ с пагинацией."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True


class PaginationParams:
    """Параметры пагинации"""

    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
    ):
        self.page = page
        self.size = size
        self.search = search
        self.sort_by = sort_by
        self.sort_order = sort_order

    @property
    def offset(self) -> int:
        """Вычислить offset для SQL запроса"""
        return (self.page - 1) * self.size

    @property
    def limit(self) -> int:
        """Получить limit для SQL запроса"""
        return self.size

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "page": self.page,
            "size": self.size,
            "search": self.search,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "offset": self.offset,
            "limit": self.limit,
        }


def create_paginated_response(
    items: List[T],
    total: int,
    params: PaginationParams,
) -> PaginatedResponse[T]:
    """Создать стандартизированный ответ с пагинацией"""
    pages = ceil(total / params.size) if params.size > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
        pages=pages,
    )


# Типизированные аннотации для FastAPI зависимостей
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
        regex="^(asc|desc)$",
        description="Порядок сортировки",
        examples=["asc", "desc"],
    ),
]


def get_pagination_params(
    page: PageParam,
    size: SizeParam,
    search: SearchParam,
    sort_by: SortByParam,
    sort_order: SortOrderParam,
) -> PaginationParams:
    """Создать объект параметров пагинации из FastAPI зависимостей"""
    return PaginationParams(
        page=page,
        size=size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# Утилиты для работы с пагинацией
def calculate_pages(total: int, size: int) -> int:
    """Вычислить общее количество страниц"""
    return ceil(total / size) if size > 0 else 0


def validate_page(page: int, total_pages: int) -> int:
    """Валидировать номер страницы"""
    if page < 1:
        return 1
    if page > total_pages:
        return total_pages
    return page


def get_page_info(page: int, size: int, total: int) -> Dict[str, Any]:
    """Получить информацию о странице"""
    total_pages = calculate_pages(total, size)

    return {
        "page": page,
        "size": size,
        "total": total,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None,
    }


# Экспорт всех компонентов
__all__ = [
    "PaginatedResponse",
    "PaginationParams",
    "create_paginated_response",
    "PageParam",
    "SizeParam",
    "SearchParam",
    "SortByParam",
    "SortOrderParam",
    "get_pagination_params",
    "calculate_pages",
    "validate_page",
    "get_page_info",
]
