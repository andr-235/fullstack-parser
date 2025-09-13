"""
Сервис для работы с ключевыми словами
"""

from typing import List, Optional

from common.exceptions import ValidationError
from keywords.models import Keyword, KeywordsRepository


class KeywordsService:
    """Сервис для работы с ключевыми словами"""

    def __init__(self, repository: KeywordsRepository):
        self.repository = repository

    async def create_keyword(self, word: str, description: str = None, 
                           category_name: str = None, priority: int = 5, 
                           group_id: int = None) -> Keyword:
        """Создать ключевое слово"""
        if not word or len(word.strip()) < 2:
            raise ValidationError("Ключевое слово должно содержать минимум 2 символа")

        existing = await self.repository.get_by_word(word)
        if existing:
            raise ValidationError("Ключевое слово уже существует")

        return await self.repository.create(
            word=word.strip(),
            description=description,
            category_name=category_name,
            priority=priority,
            group_id=group_id
        )

    async def get_keyword(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        return await self.repository.get_by_id(keyword_id)

    async def get_keywords(self, active_only: bool = True, category: str = None, 
                          search: str = None, limit: int = 50, offset: int = 0) -> List[Keyword]:
        """Получить список ключевых слов"""
        return await self.repository.get_all(
            active_only=active_only,
            category=category,
            search=search,
            limit=limit,
            offset=offset
        )

    async def update_keyword(self, keyword_id: int, **data) -> bool:
        """Обновить ключевое слово"""
        if "word" in data:
            if not data["word"] or len(data["word"].strip()) < 2:
                raise ValidationError("Ключевое слово должно содержать минимум 2 символа")
            
            existing = await self.repository.get_by_word(data["word"])
            if existing and existing.id != keyword_id:
                raise ValidationError("Ключевое слово уже существует")

        return await self.repository.update(keyword_id, **data)

    async def delete_keyword(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        return await self.repository.delete(keyword_id)

    async def activate_keyword(self, keyword_id: int) -> bool:
        """Активировать ключевое слово"""
        keyword = await self.repository.get_by_id(keyword_id)
        if not keyword:
            return False

        if keyword.is_archived:
            raise ValidationError("Нельзя активировать архивированное ключевое слово")

        return await self.repository.update(keyword_id, is_active=True, is_archived=False)

    async def deactivate_keyword(self, keyword_id: int) -> bool:
        """Деактивировать ключевое слово"""
        return await self.repository.update(keyword_id, is_active=False)

    async def archive_keyword(self, keyword_id: int) -> bool:
        """Архивировать ключевое слово"""
        return await self.repository.update(keyword_id, is_active=False, is_archived=True)
