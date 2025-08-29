"""
Общие зависимости и утилиты для API v1

Этот модуль содержит:
- Общие зависимости для API эндпоинтов
- Утилиты для работы с данными
- Стандартизированные классы ответов
- Вспомогательные функции

Объединен из dependencies.py и utils.py для лучшей организации кода.
"""

from typing import Annotated, Optional, Any, Dict, List, TypeVar, Generic
from datetime import datetime
from fastapi import Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.api.v1.exceptions import create_error_response, APIException

logger = get_logger(__name__)

T = TypeVar("T")


# Классы для стандартизированных ответов
class PaginatedResponse(BaseModel, Generic[T]):
    """Стандартизированный ответ с пагинацией."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    class Config:
        from_attributes = True


class APIResponse(BaseModel, Generic[T]):
    """Стандартизированный ответ API."""

    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


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


# Утилиты из utils.py (объединенные)
def create_paginated_response(
    items: List[Any], total: int, page: int, size: int
) -> Dict[str, Any]:
    """
    Создает стандартизированный ответ с пагинацией.

    Args:
        items: Список элементов
        total: Общее количество элементов
        page: Номер страницы
        size: Размер страницы

    Returns:
        Dict[str, Any]: Стандартизированный ответ с пагинацией
    """
    pages = (total + size - 1) // size if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1,
    }


def create_error_json_response(
    error: APIException, status_code: Optional[int] = None
) -> JSONResponse:
    """
    Создает JSONResponse с ошибкой.

    Args:
        error: Исключение API
        status_code: HTTP статус код (если не указан, берется из исключения)

    Returns:
        JSONResponse: JSON ответ с ошибкой
    """
    error_data = create_error_response(error)
    return JSONResponse(
        status_code=status_code or error.status_code, content=error_data
    )


def validate_enum_value(value: Any, enum_class: Any, field_name: str) -> Any:
    """
    Валидирует значение enum.

    Args:
        value: Значение для валидации
        enum_class: Класс enum
        field_name: Название поля

    Returns:
        Any: Валидное значение

    Raises:
        ValueError: При невалидном значении
    """
    if value is not None and value not in enum_class:
        valid_values = [e.value for e in enum_class]
        raise ValueError(
            f"Поле {field_name} должно быть одним из: {valid_values}"
        )
    return value


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """
    Очищает строку от потенциально опасных символов.

    Args:
        value: Исходная строка
        max_length: Максимальная длина строки

    Returns:
        str: Очищенная строка
    """
    if not isinstance(value, str):
        raise ValueError("Значение должно быть строкой")

    # Убираем лишние пробелы
    sanitized = " ".join(value.split())

    # Ограничиваем длину
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip()

    return sanitized


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """
    Форматирует datetime в ISO формат.

    Args:
        dt: Дата и время

    Returns:
        Optional[str]: Отформатированная строка или None
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        return dt

    return dt.isoformat()


def parse_datetime(date_string: str) -> Optional[datetime]:
    """
    Парсит строку в datetime.

    Args:
        date_string: Строка с датой

    Returns:
        Optional[datetime]: Объект datetime или None
    """
    if not date_string:
        return None

    try:
        # Пробуем разные форматы
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue

        # Если ничего не подошло, пробуем ISO формат
        return datetime.fromisoformat(date_string.replace("Z", "+00:00"))

    except (ValueError, TypeError):
        return None


def build_filter_query(
    base_query: Any, filters: Dict[str, Any], allowed_fields: List[str]
) -> Any:
    """
    Строит запрос с фильтрами.

    Args:
        base_query: Базовый запрос
        filters: Словарь фильтров
        allowed_fields: Список разрешенных полей для фильтрации

    Returns:
        Any: Запрос с примененными фильтрами
    """
    from sqlalchemy import and_

    filter_conditions = []

    for field, value in filters.items():
        if field in allowed_fields and value is not None:
            # Здесь можно добавить логику для разных типов фильтров
            # Пока просто добавляем условие равенства
            filter_conditions.append(getattr(base_query, field) == value)

    if filter_conditions:
        return base_query.where(and_(*filter_conditions))

    return base_query
