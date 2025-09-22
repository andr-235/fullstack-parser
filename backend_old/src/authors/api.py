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
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
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
    AuthorUpdate,
)
from .services import AuthorService

# Константы для кодов ошибок
ERROR_AUTHOR_NOT_FOUND = "AUTHOR_NOT_FOUND"
ERROR_AUTHOR_ALREADY_EXISTS = "AUTHOR_ALREADY_EXISTS"
ERROR_VALIDATION_ERROR = "VALIDATION_ERROR"
ERROR_INTERNAL_SERVER = "INTERNAL_SERVER_ERROR"

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/authors", tags=["authors"])


@router.post("/", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def create_author(
    data: AuthorCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Создает нового автора"""
    service = AuthorService(db)
    try:
        return await service.create_author(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int = Path(..., gt=0),
    data: Optional[AuthorUpdate] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """Обновляет данные автора"""
    service = AuthorService(db)
    try:
        return await service.update_author(author_id, data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{author_id}", status_code=204)
async def delete_author(
    author_id: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db_session)
):
    """Удаляет автора"""
    service = AuthorService(db)
    try:
        await service.delete_author(author_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))