from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import Keyword
from app.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
)
from app.schemas.keyword import KeywordCreate, KeywordResponse, KeywordUpdate


class KeywordService:
    async def create_keyword(
        self, db: AsyncSession, keyword_data: KeywordCreate
    ) -> Keyword:
        existing = await db.execute(
            select(Keyword).where(
                func.lower(Keyword.word) == keyword_data.word.lower()
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ключевое слово уже существует",
            )
        new_keyword = Keyword(**keyword_data.model_dump())
        db.add(new_keyword)
        await db.commit()
        await db.refresh(new_keyword)
        return new_keyword

    async def get_keywords(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        active_only: bool = True,
        category: Optional[str] = None,
        q: Optional[str] = None,
    ) -> PaginatedResponse:
        query = select(Keyword)
        if active_only:
            query = query.where(Keyword.is_active)
        if category:
            query = query.where(Keyword.category == category)
        if q:
            search_pattern = f"%{q.lower()}%"
            query = query.where(
                func.lower(Keyword.word).like(search_pattern)
                | func.lower(Keyword.category).like(search_pattern)
            )
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        paginated_query = query.offset(pagination.skip).limit(pagination.size)
        result = await db.execute(paginated_query)
        keywords = result.scalars().all()
        return PaginatedResponse(
            total=total or 0,
            page=pagination.page,
            size=pagination.size,
            items=[
                KeywordResponse.model_validate(keyword) for keyword in keywords
            ],
        )

    async def get_keyword(self, db: AsyncSession, keyword_id: int) -> Keyword:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        return keyword

    async def update_keyword(
        self, db: AsyncSession, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Keyword:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        if (
            keyword_update.word
            and keyword_update.word.lower() != keyword.word.lower()
        ):
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
        update_data = keyword_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(keyword, field, value)
        await db.commit()
        await db.refresh(keyword)
        return keyword

    async def delete_keyword(
        self, db: AsyncSession, keyword_id: int
    ) -> StatusResponse:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        await db.delete(keyword)
        await db.commit()
        return StatusResponse(
            status="success",
            message=f"Ключевое слово '{keyword.word}' удалено",
        )

    async def create_keywords_bulk(
        self, db: AsyncSession, keywords_data: List[KeywordCreate]
    ) -> List[Keyword]:
        created_keywords = []
        for keyword_data in keywords_data:
            existing = await db.execute(
                select(Keyword).where(
                    func.lower(Keyword.word) == keyword_data.word.lower()
                )
            )
            if not existing.scalar_one_or_none():
                new_keyword = Keyword(**keyword_data.model_dump())
                db.add(new_keyword)
                created_keywords.append(new_keyword)
        await db.commit()
        for keyword in created_keywords:
            await db.refresh(keyword)
        return created_keywords

    async def get_categories(self, db: AsyncSession) -> List[str]:
        result = await db.execute(
            select(Keyword.category)
            .distinct()
            .where(Keyword.category.isnot(None))
        )
        categories = [cat for cat in result.scalars().all() if cat]
        return sorted(categories)


keyword_service = KeywordService()
