"""
Репозиторий для работы с ключевыми словами
"""

from typing import List, Optional
from datetime import datetime, timedelta

from sqlalchemy import func, select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.keywords.domain.entities.keyword import Keyword
from src.keywords.domain.interfaces.keyword_repository_interface import KeywordRepositoryInterface
from src.keywords.infrastructure.base_repository import BaseRepository
from src.keywords.infrastructure.models.keyword_model import KeywordModel
from src.keywords.shared.constants import DEFAULT_LIMIT


class KeywordRepository(BaseRepository[Keyword, KeywordModel], KeywordRepositoryInterface):
    """Репозиторий для работы с ключевыми словами"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, KeywordModel)

    async def save(self, keyword: Keyword) -> Keyword:
        """Сохранить ключевое слово"""
        model = KeywordModel.from_domain(keyword)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_domain()

    async def find_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Найти ключевое слово по ID"""
        result = await self.db.execute(
            select(KeywordModel).where(KeywordModel.id == keyword_id)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_word(self, word: str) -> Optional[Keyword]:
        """Найти ключевое слово по слову"""
        result = await self.db.execute(
            select(KeywordModel).where(KeywordModel.word == word)
        )
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_all(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
    ) -> List[Keyword]:
        """Найти все ключевые слова с фильтрами"""
        query = select(KeywordModel)

        conditions = []
        if active_only:
            conditions.append(
                and_(
                    KeywordModel.is_active == True,
                    KeywordModel.is_archived == False
                )
            )
        if category:
            conditions.append(KeywordModel.category_name == category)
        if search:
            conditions.append(
                or_(
                    KeywordModel.word.ilike(f"%{search}%"),
                    KeywordModel.description.ilike(f"%{search}%")
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(KeywordModel.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        models = result.scalars().all()
        return [model.to_domain() for model in models]

    async def update(self, keyword: Keyword) -> bool:
        """Обновить ключевое слово"""
        model = KeywordModel.from_domain(keyword)
        # Обновляем только измененные поля
        update_data = {}
        if model.word:
            update_data["word"] = model.word
        if model.description is not None:
            update_data["description"] = model.description
        if model.category_name is not None:
            update_data["category_name"] = model.category_name
        if model.priority is not None:
            update_data["priority"] = model.priority
        if model.group_id is not None:
            update_data["group_id"] = model.group_id
        if model.is_active is not None:
            update_data["is_active"] = model.is_active
        if model.is_archived is not None:
            update_data["is_archived"] = model.is_archived
        if model.match_count is not None:
            update_data["match_count"] = model.match_count

        update_data["updated_at"] = datetime.utcnow()

        if update_data:
            result = await self.db.execute(
                select(KeywordModel)
                .where(KeywordModel.id == keyword.id)
                .with_for_update()
            )
            existing_model = result.scalar_one_or_none()
            if existing_model:
                for field, value in update_data.items():
                    setattr(existing_model, field, value)
                await self.db.commit()
                return True
        return False

    async def delete(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        result = await self.db.execute(
            select(KeywordModel).where(KeywordModel.id == keyword_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self.db.delete(model)
            await self.db.commit()
            return True
        return False

    async def exists_by_word(self, word: str) -> bool:
        """Проверить существование ключевого слова по слову"""
        result = await self.db.execute(
            select(func.count(KeywordModel.id)).where(KeywordModel.word == word)
        )
        count = result.scalar() or 0
        return count > 0

    async def count_total(self) -> int:
        """Получить общее количество ключевых слов"""
        result = await self.db.execute(
            select(func.count(KeywordModel.id))
        )
        return result.scalar() or 0

    async def count_active(self) -> int:
        """Получить количество активных ключевых слов"""
        result = await self.db.execute(
            select(func.count(KeywordModel.id)).where(
                and_(
                    KeywordModel.is_active == True,
                    KeywordModel.is_archived == False
                )
            )
        )
        return result.scalar() or 0

    async def count_by_period(self, days: int) -> int:
        """Получить количество ключевых слов за период"""
        since_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(KeywordModel.id)).where(
                KeywordModel.created_at >= since_date
            )
        )
        return result.scalar() or 0