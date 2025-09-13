"""
SQLAlchemy модели для модуля Keywords
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from shared.infrastructure.database.base import Base


class Keyword(Base):
    """Модель ключевого слова"""
    
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    category_name = Column(String(100), nullable=True, index=True)
    category_description = Column(Text, nullable=True)
    priority = Column(Integer, default=5, nullable=False)
    match_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    group_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует модель в словарь"""
        return {
            "id": self.id,
            "word": self.word,
            "description": self.description,
            "priority": self.priority,
            "match_count": self.match_count,
            "group_id": self.group_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": {
                "is_active": self.is_active,
                "is_archived": self.is_archived,
            },
            "category": {
                "name": self.category_name,
                "description": self.category_description,
            } if self.category_name else None,
        }


class KeywordsRepository:
    """Репозиторий для работы с ключевыми словами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Keyword:
        """Создать ключевое слово"""
        keyword = Keyword(
            word=data["word"],
            description=data.get("description"),
            category_name=data.get("category_name"),
            category_description=data.get("category_description"),
            priority=data.get("priority", 5),
            match_count=data.get("match_count", 0),
            is_active=data.get("is_active", True),
            is_archived=data.get("is_archived", False),
            group_id=data.get("group_id"),
        )
        
        self.db.add(keyword)
        await self.db.commit()
        await self.db.refresh(keyword)
        return keyword
    
    async def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        result = await self.db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_word(self, word: str) -> Optional[Keyword]:
        """Получить ключевое слово по слову"""
        result = await self.db.execute(
            select(Keyword).where(Keyword.word == word)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Keyword]:
        """Получить список ключевых слов с фильтрами"""
        query = select(Keyword)
        
        # Фильтры
        conditions = []
        if active_only:
            conditions.append(and_(Keyword.is_active == True, Keyword.is_archived == False))
        if category:
            conditions.append(Keyword.category_name == category)
        if search:
            search_condition = or_(
                Keyword.word.ilike(f"%{search}%"),
                Keyword.description.ilike(f"%{search}%"),
                Keyword.category_name.ilike(f"%{search}%"),
            )
            conditions.append(search_condition)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Сортировка и пагинация
        query = query.order_by(Keyword.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update(self, keyword_id: int, data: Dict[str, Any]) -> bool:
        """Обновить ключевое слово"""
        keyword = await self.get_by_id(keyword_id)
        if not keyword:
            return False
        
        # Обновляем поля
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
    
    async def count(self) -> int:
        """Подсчитать количество ключевых слов"""
        result = await self.db.execute(select(func.count(Keyword.id)))
        return result.scalar() or 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        # Общая статистика
        total_result = await self.db.execute(select(func.count(Keyword.id)))
        total = total_result.scalar() or 0
        
        # Активные
        active_result = await self.db.execute(
            select(func.count(Keyword.id)).where(Keyword.is_active == True)
        )
        active = active_result.scalar() or 0
        
        # Архивированные
        archived_result = await self.db.execute(
            select(func.count(Keyword.id)).where(Keyword.is_archived == True)
        )
        archived = archived_result.scalar() or 0
        
        # Общее количество совпадений
        matches_result = await self.db.execute(select(func.sum(Keyword.match_count)))
        total_matches = matches_result.scalar() or 0
        
        # Категории
        categories_result = await self.db.execute(
            select(func.count(func.distinct(Keyword.category_name)))
            .where(Keyword.category_name.isnot(None))
        )
        categories = categories_result.scalar() or 0
        
        return {
            "total_keywords": total,
            "active_keywords": active,
            "archived_keywords": archived,
            "total_categories": categories,
            "total_matches": total_matches,
            "avg_matches_per_keyword": total_matches / total if total > 0 else 0,
        }
    
    async def get_categories(self) -> list[str]:
        """Получить список категорий"""
        result = await self.db.execute(
            select(func.distinct(Keyword.category_name))
            .where(Keyword.category_name.isnot(None))
        )
        return sorted([cat for cat in result.scalars().all() if cat])
    
    async def bulk_create(self, keywords_data: list[Dict[str, Any]]) -> list[Keyword]:
        """Массовое создание ключевых слов"""
        keywords = []
        for data in keywords_data:
            keyword = Keyword(
                word=data["word"],
                description=data.get("description"),
                category_name=data.get("category_name"),
                category_description=data.get("category_description"),
                priority=data.get("priority", 5),
                match_count=data.get("match_count", 0),
                is_active=data.get("is_active", True),
                is_archived=data.get("is_archived", False),
                group_id=data.get("group_id"),
            )
            keywords.append(keyword)
        
        self.db.add_all(keywords)
        await self.db.commit()
        
        for keyword in keywords:
            await self.db.refresh(keyword)
        
        return keywords
    
    async def create_or_update_keyword(self, data: Dict[str, Any]) -> Keyword:
        """Создать или обновить ключевое слово"""
        word = data["word"].lower().strip()
        
        # Ищем существующее ключевое слово
        existing = await self.get_by_word(word)
        
        if existing:
            # Обновляем существующее
            update_data = {
                "match_count": existing.match_count + 1,
                "updated_at": datetime.utcnow()
            }
            
            # Обновляем описание, если оно пустое
            if not existing.description and data.get("description"):
                update_data["description"] = data["description"]
            
            # Обновляем категорию, если она не задана
            if not existing.category_name and data.get("category_name"):
                update_data["category_name"] = data["category_name"]
                update_data["category_description"] = data.get("category_description")
            
            await self.update(existing.id, update_data)
            await self.db.refresh(existing)
            return existing
        else:
            # Создаем новое
            return await self.create(data)