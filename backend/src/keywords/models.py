"""
SQLAlchemy модели для модуля Keywords
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from common.database import Base


class Keyword(Base):
    """Модель ключевого слова"""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category_name = Column(String(100), nullable=True, index=True)
    priority = Column(Integer, default=5, nullable=False)
    match_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    group_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class KeywordsRepository:
    """Репозиторий для работы с ключевыми словами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, word: str, description: str = None, category_name: str = None, 
                    priority: int = 5, group_id: int = None) -> Keyword:
        """Создать ключевое слово"""
        keyword = Keyword(
            word=word,
            description=description,
            category_name=category_name,
            priority=priority,
            group_id=group_id
        )
        self.db.add(keyword)
        await self.db.commit()
        await self.db.refresh(keyword)
        return keyword

    async def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        from sqlalchemy import select
        result = await self.db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        return result.scalar_one_or_none()

    async def get_by_word(self, word: str) -> Optional[Keyword]:
        """Получить ключевое слово по слову"""
        from sqlalchemy import select
        result = await self.db.execute(
            select(Keyword).where(Keyword.word == word)
        )
        return result.scalar_one_or_none()

    async def get_all(self, active_only: bool = True, category: str = None, 
                     search: str = None, limit: int = 50, offset: int = 0) -> list[Keyword]:
        """Получить список ключевых слов"""
        from sqlalchemy import select, and_, or_
        query = select(Keyword)

        conditions = []
        if active_only:
            conditions.append(and_(Keyword.is_active == True, Keyword.is_archived == False))
        if category:
            conditions.append(Keyword.category_name == category)
        if search:
            conditions.append(or_(
                Keyword.word.ilike(f"%{search}%"),
                Keyword.description.ilike(f"%{search}%")
            ))

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Keyword.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, keyword_id: int, **data) -> bool:
        """Обновить ключевое слово"""
        keyword = await self.get_by_id(keyword_id)
        if not keyword:
            return False

        for field, value in data.items():
            if hasattr(keyword, field) and field not in ["id", "created_at"]:
                setattr(keyword, field, value)

        keyword.updated_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def delete(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        keyword = await self.get_by_id(keyword_id)
        if not keyword:
            return False

        await self.db.delete(keyword)
        await self.db.commit()
        return True
