"""
API endpoints для управления ключевыми словами
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.keyword import Keyword
from app.schemas.base import PaginatedResponse, PaginationParams, StatusResponse
from app.schemas.keyword import KeywordCreate, KeywordResponse, KeywordUpdate

router = APIRouter(prefix="/keywords", tags=["Keywords"])


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
    keyword_data: KeywordCreate, db: AsyncSession = Depends(get_async_session)
) -> KeywordResponse:
    """Добавить новое ключевое слово"""

    # Проверяем, что такое ключевое слово ещё не существует
    existing = await db.execute(
        select(Keyword).where(func.lower(Keyword.word) == keyword_data.word.lower())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Ключевое слово уже существует"
        )

    # Создаём новое ключевое слово
    new_keyword = Keyword(**keyword_data.model_dump())

    db.add(new_keyword)
    await db.commit()
    await db.refresh(new_keyword)

    return KeywordResponse.model_validate(new_keyword)


@router.get("/", response_model=PaginatedResponse)
async def get_keywords(
    pagination: PaginationParams = Depends(),
    active_only: bool = True,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
) -> PaginatedResponse:
    """Получить список ключевых слов"""

    query = select(Keyword)

    if active_only:
        query = query.where(Keyword.is_active)

    if category:
        query = query.where(Keyword.category == category)

    # Подсчёт общего количества
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # Получение данных с пагинацией
    paginated_query = query.offset(pagination.skip).limit(pagination.limit)
    result = await db.execute(paginated_query)
    keywords = result.scalars().all()

    return PaginatedResponse(
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
        items=[KeywordResponse.model_validate(keyword) for keyword in keywords],
    )


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
    keyword_id: int, db: AsyncSession = Depends(get_async_session)
) -> KeywordResponse:
    """Получить информацию о конкретном ключевом слове"""

    result = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ключевое слово не найдено"
        )

    return KeywordResponse.model_validate(keyword)


@router.put("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    db: AsyncSession = Depends(get_async_session),
) -> KeywordResponse:
    """Обновить ключевое слово"""

    result = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ключевое слово не найдено"
        )

    # Проверяем уникальность нового слова
    if keyword_update.word and keyword_update.word.lower() != keyword.word.lower():
        existing = await db.execute(
            select(Keyword).where(
                func.lower(Keyword.word) == keyword_update.word.lower()
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ключевое слово с таким названием уже существует",
            )

    # Обновляем только указанные поля
    update_data = keyword_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(keyword, field, value)

    await db.commit()
    await db.refresh(keyword)

    return KeywordResponse.model_validate(keyword)


@router.delete("/{keyword_id}", response_model=StatusResponse)
async def delete_keyword(
    keyword_id: int, db: AsyncSession = Depends(get_async_session)
) -> StatusResponse:
    """Удалить ключевое слово"""

    result = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    keyword = result.scalar_one_or_none()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ключевое слово не найдено"
        )

    await db.delete(keyword)
    await db.commit()

    return StatusResponse(
        success=True, message=f"Ключевое слово '{keyword.word}' удалено"
    )


@router.post("/bulk", response_model=List[KeywordResponse])
async def create_keywords_bulk(
    keywords_data: List[KeywordCreate], db: AsyncSession = Depends(get_async_session)
) -> List[KeywordResponse]:
    """Массовое добавление ключевых слов"""

    created_keywords = []

    for keyword_data in keywords_data:
        # Проверяем уникальность
        existing = await db.execute(
            select(Keyword).where(func.lower(Keyword.word) == keyword_data.word.lower())
        )

        if not existing.scalar_one_or_none():
            new_keyword = Keyword(**keyword_data.model_dump())
            db.add(new_keyword)
            created_keywords.append(new_keyword)

    await db.commit()

    # Обновляем объекты
    for keyword in created_keywords:
        await db.refresh(keyword)

    return [KeywordResponse.model_validate(keyword) for keyword in created_keywords]


@router.get("/categories/", response_model=List[str])
async def get_keyword_categories(
    db: AsyncSession = Depends(get_async_session),
) -> List[str]:
    """Получить список всех категорий ключевых слов"""

    result = await db.execute(
        select(Keyword.category).distinct().where(Keyword.category.isnot(None))
    )
    categories = [cat for cat in result.scalars().all() if cat]

    return sorted(categories)
