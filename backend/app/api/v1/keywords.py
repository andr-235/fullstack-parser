"""
API endpoints для управления ключевыми словами
"""

from typing import Optional

from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
)
from app.schemas.keyword import (
    KeywordCreate,
    KeywordResponse,
    KeywordUpdate,
    KeywordUploadResponse,
)
from app.services.keyword_service import keyword_service

router = APIRouter(tags=["Keywords"])


@router.post(
    "/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED
)
async def create_keyword(
    keyword_data: KeywordCreate, db: AsyncSession = Depends(get_db)
) -> KeywordResponse:
    keyword = await keyword_service.create_keyword(db, keyword_data)
    return KeywordResponse.model_validate(keyword)


@router.get("/", response_model=PaginatedResponse[KeywordResponse])
async def get_keywords(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    category: Optional[str] = None,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[KeywordResponse]:
    return await keyword_service.get_keywords(
        db, pagination, active_only, category, q
    )


@router.get("/categories", response_model=list[str])
async def get_keyword_categories(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    return await keyword_service.get_categories(db)


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int, db: AsyncSession = Depends(get_db)
) -> KeywordResponse:
    keyword = await keyword_service.get_keyword(db, keyword_id)
    return KeywordResponse.model_validate(keyword)


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    db: AsyncSession = Depends(get_db),
) -> KeywordResponse:
    keyword = await keyword_service.update_keyword(
        db, keyword_id, keyword_update
    )
    return KeywordResponse.model_validate(keyword)


@router.delete("/{keyword_id}", response_model=StatusResponse)
async def delete_keyword(
    keyword_id: int, db: AsyncSession = Depends(get_db)
) -> StatusResponse:
    return await keyword_service.delete_keyword(db, keyword_id)


@router.post("/bulk", response_model=list[KeywordResponse])
async def create_keywords_bulk(
    keywords_data: list[KeywordCreate], db: AsyncSession = Depends(get_db)
) -> list[KeywordResponse]:
    keywords = await keyword_service.create_keywords_bulk(db, keywords_data)
    return [KeywordResponse.model_validate(keyword) for keyword in keywords]


@router.post("/upload", response_model=KeywordUploadResponse)
async def upload_keywords_from_file(
    file: UploadFile,
    default_category: Optional[str] = Form(
        None, description="Категория по умолчанию"
    ),
    is_active: bool = Form(True, description="Активны ли ключевые слова"),
    is_case_sensitive: bool = Form(False, description="Учитывать регистр"),
    is_whole_word: bool = Form(False, description="Искать только целые слова"),
    db: AsyncSession = Depends(get_db),
) -> KeywordUploadResponse:
    """
    Загружает ключевые слова из файла

    Поддерживаемые форматы:
    - CSV: word,category,description
    - TXT: одно слово на строку

    Параметры:
    - file: Файл с ключевыми словами (CSV или TXT)
    - default_category: Категория по умолчанию для ключевых слов
    - is_active: Активны ли загружаемые ключевые слова
    - is_case_sensitive: Учитывать регистр при поиске
    - is_whole_word: Искать только целые слова
    """
    return await keyword_service.upload_keywords_from_file(
        db=db,
        file=file,
        default_category=default_category,
        is_active=is_active,
        is_case_sensitive=is_case_sensitive,
        is_whole_word=is_whole_word,
    )
