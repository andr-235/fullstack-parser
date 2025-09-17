"""
API роутеры для модуля авторов - рефакторинг с паттернами

Предоставляет REST API для управления авторами с улучшенной валидацией,
обработкой ошибок и документацией.
"""

"""
API роутеры для модуля авторов - рефакторинг с паттернами

Предоставляет REST API для управления авторами с улучшенной валидацией,
обработкой ошибок и документацией.
"""

import logging
import time
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.database import get_db_session

from .exceptions import (
    AuthorAlreadyExistsError,
    AuthorNotFoundError,
    AuthorValidationError,
)
from .schemas import (
    AuthorCreate,
    AuthorResponse,
    AuthorStatus,
    AuthorUpdate,
    MAX_SCREEN_NAME_LENGTH,
)
from .services import AuthorService

# Константы для кодов ошибок
ERROR_AUTHOR_NOT_FOUND = "AUTHOR_NOT_FOUND"
ERROR_AUTHOR_ALREADY_EXISTS = "AUTHOR_ALREADY_EXISTS"
ERROR_VALIDATION_ERROR = "VALIDATION_ERROR"
ERROR_INTERNAL_SERVER = "INTERNAL_SERVER_ERROR"
ERROR_RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

# Константы для rate limiting
RATE_LIMIT_REQUESTS = 100  # запросов
RATE_LIMIT_WINDOW = 60  # секунд
RATE_LIMIT_STORAGE = defaultdict(list)  # простое in-memory хранилище

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/authors", tags=["authors"])


def rate_limit_dependency(request: Request) -> None:
    """
    Простая защита от rate limiting.

    Ограничивает количество запросов от одного IP адреса.
    """
    client_ip = request.client.host if request.client else "unknown"
    current_time = time.time()

    # Очистка старых запросов
    RATE_LIMIT_STORAGE[client_ip] = [
        timestamp for timestamp in RATE_LIMIT_STORAGE[client_ip]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]

    # Проверка лимита
    if len(RATE_LIMIT_STORAGE[client_ip]) >= RATE_LIMIT_REQUESTS:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": ERROR_RATE_LIMIT_EXCEEDED,
                "message": "Превышен лимит запросов. Попробуйте позже."
            }
        )

    # Добавление текущего запроса
    RATE_LIMIT_STORAGE[client_ip].append(current_time)


def get_author_service(db: AsyncSession = Depends(get_db_session)) -> AuthorService:
    """Получает сервис авторов"""
    return AuthorService(db)


@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit_dependency)])
async def create_author(
    request: Request,
    data: AuthorCreate,
    service: AuthorService = Depends(get_author_service)
):
    """
    Создает нового автора.

    Этот эндпоинт позволяет создать нового автора в системе.
    Все поля валидируются согласно схеме AuthorCreate.

    Args:
        request: Объект запроса для логирования контекста.
        data: Данные для создания автора.
        service: Сервис для работы с авторами.

    Returns:
        AuthorResponse: Созданный автор.

    Raises:
        HTTPException: С ошибками валидации или бизнес-логики.

    Примеры:
        POST /authors/
        {
            "vk_id": 123456,
            "first_name": "Иван",
            "last_name": "Иванов",
            "screen_name": "ivanov"
        }

    Возможные ошибки:
        - 400: Ошибка валидации данных
        - 409: Автор с таким VK ID уже существует
        - 422: Ошибка валидации Pydantic
        - 500: Внутренняя ошибка сервера
    """
    try:
        return await service.create_author(data)
    except ValidationError as e:
        logger.error(f"Pydantic validation error creating author: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ERROR_VALIDATION_ERROR,
                "message": "Ошибка валидации данных",
                "details": str(e)
            }
        )
    except AuthorAlreadyExistsError as e:
        logger.warning(f"Author already exists: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": ERROR_AUTHOR_ALREADY_EXISTS,
                "message": str(e)
            }
        )
    except AuthorValidationError as e:
        logger.warning(f"Author validation error: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ERROR_VALIDATION_ERROR,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error creating author: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ERROR_INTERNAL_SERVER,
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.get("/{author_id}", response_model=AuthorResponse, dependencies=[Depends(rate_limit_dependency)])
async def get_author(
    request: Request,
    author_id: int = Path(..., gt=0, description="ID автора для получения"),
    service: AuthorService = Depends(get_author_service)
):
    """
    Получает автора по его ID.

    Возвращает полную информацию об авторе по указанному ID.

    Args:
        request: Объект запроса для логирования контекста.
        author_id: Уникальный идентификатор автора (должен быть > 0).
        service: Сервис для работы с авторами.

    Returns:
        AuthorResponse: Информация об авторе.

    Raises:
        HTTPException: Если автор не найден или произошла ошибка.

    Примеры:
        GET /authors/123

    Возможные ошибки:
        - 404: Автор с указанным ID не найден
        - 500: Внутренняя ошибка сервера
    """
    try:
        author = await service.get_by_id(author_id)
        if author is None:
            raise AuthorNotFoundError(author_id=author_id)
        return author
    except AuthorNotFoundError as e:
        logger.warning(f"Author not found: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ERROR_AUTHOR_NOT_FOUND,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error getting author {author_id}: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ERROR_INTERNAL_SERVER,
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.get("/vk/{vk_id}", response_model=AuthorResponse, dependencies=[Depends(rate_limit_dependency)])
async def get_author_by_vk_id(
    request: Request,
    vk_id: int = Path(..., gt=0, description="VK ID автора для получения"),
    service: AuthorService = Depends(get_author_service)
):
    """
    Получает автора по его VK ID.

    Возвращает полную информацию об авторе по указанному VK ID.

    Args:
        request: Объект запроса для логирования контекста.
        vk_id: VK ID автора (должен быть > 0).
        service: Сервис для работы с авторами.

    Returns:
        AuthorResponse: Информация об авторе.

    Raises:
        HTTPException: Если автор не найден или произошла ошибка.

    Примеры:
        GET /authors/vk/123456

    Возможные ошибки:
        - 404: Автор с указанным VK ID не найден
        - 500: Внутренняя ошибка сервера
    """
    try:
        author = await service.get_by_vk_id(vk_id)
        if author is None:
            raise AuthorNotFoundError(vk_id=vk_id)
        return author
    except AuthorNotFoundError as e:
        logger.warning(f"Author not found by VK ID: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ERROR_AUTHOR_NOT_FOUND,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error getting author by VK ID {vk_id}: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ERROR_INTERNAL_SERVER,
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.get("/screen/{screen_name}", response_model=AuthorResponse, dependencies=[Depends(rate_limit_dependency)])
async def get_author_by_screen_name(
    request: Request,
    screen_name: str = Path(..., min_length=1, max_length=MAX_SCREEN_NAME_LENGTH, description="Screen name автора для получения"),
    service: AuthorService = Depends(get_author_service)
):
    """
    Получает автора по его screen name.

    Возвращает полную информацию об авторе по указанному screen name.

    Args:
        request: Объект запроса для логирования контекста.
        screen_name: Screen name автора (длина от 1 до 100 символов).
        service: Сервис для работы с авторами.

    Returns:
        AuthorResponse: Информация об авторе.

    Raises:
        HTTPException: Если автор не найден или произошла ошибка.

    Примеры:
        GET /authors/screen/ivanov

    Возможные ошибки:
        - 404: Автор с указанным screen name не найден
        - 422: Неверная длина screen name
        - 500: Внутренняя ошибка сервера
    """
    try:
        author = await service.get_by_screen_name(screen_name)
        if author is None:
            raise AuthorNotFoundError()
        return author
    except AuthorNotFoundError as e:
        logger.warning(f"Author not found by screen name: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ERROR_AUTHOR_NOT_FOUND,
                "message": f"Автор с screen name '{screen_name}' не найден"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error getting author by screen name {screen_name}: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ERROR_INTERNAL_SERVER,
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.put("/{author_id}", response_model=AuthorResponse, dependencies=[Depends(rate_limit_dependency)])
async def update_author(
    request: Request,
    author_id: int = Path(..., gt=0, description="ID автора для обновления"),
    data: Optional[AuthorUpdate] = None,
    service: AuthorService = Depends(get_author_service)
):
    """
    Обновляет данные автора.

    Позволяет частично обновить информацию об авторе. Все поля опциональны.
    Если data=None, возвращается текущая версия автора без изменений.

    Args:
        request: Объект запроса для логирования контекста.
        author_id: Уникальный идентификатор автора (должен быть > 0).
        data: Данные для обновления (опционально).
        service: Сервис для работы с авторами.

    Returns:
        AuthorResponse: Обновленная информация об авторе.

    Raises:
        HTTPException: С ошибками валидации или бизнес-логики.

    Примеры:
        PUT /authors/123
        {
            "first_name": "Иван",
            "status": "active"
        }

    Возможные ошибки:
        - 404: Автор с указанным ID не найден
        - 400: Ошибка валидации данных
        - 422: Ошибка валидации Pydantic
        - 500: Внутренняя ошибка сервера
    """
    try:
        return await service.update_author(author_id, data)
    except ValidationError as e:
        logger.error(f"Pydantic validation error updating author {author_id}: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": ERROR_VALIDATION_ERROR,
                "message": "Ошибка валидации данных",
                "details": str(e)
            }
        )
    except AuthorNotFoundError as e:
        logger.warning(f"Author not found for update: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error_code": ERROR_AUTHOR_NOT_FOUND,
                "message": str(e)
            }
        )
    except AuthorValidationError as e:
        logger.warning(f"Author validation error on update: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": ERROR_VALIDATION_ERROR,
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error updating author {author_id}: {e} | Request: {request.method} {request.url}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": ERROR_INTERNAL_SERVER,
                "message": "Внутренняя ошибка сервера"
            }
        )


@router.delete("/{author_id}", status_code=204, dependencies=[Depends(rate_limit_dependency)])
async def delete_author(
    request: Request,
    author_id: int = Path(..., gt=0, description="ID автора для удаления"),
    service: AuthorService = Depends(get_author_service)
):
    """Удаляет автора"""
    try:
        await service.delete_author(author_id)
    except AuthorNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error deleting author {author_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/", dependencies=[Depends(rate_limit_dependency)])
async def get_stats(
    request: Request,
    service: AuthorService = Depends(get_author_service)
):
    """Получает статистику авторов"""
    try:
        return await service.get_stats()
    except Exception as e:
        logger.error(f"Unexpected error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health/", dependencies=[Depends(rate_limit_dependency)])
async def health_check(
    request: Request
):
    """Health check для модуля авторов"""
    return {"status": "healthy", "module": "authors"}