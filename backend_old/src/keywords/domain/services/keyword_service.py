"""
Сервис для работы с ключевыми словами
"""

from typing import List, Optional

from src.keywords.domain.entities.keyword import Keyword
from src.keywords.domain.interfaces.keyword_repository_interface import KeywordRepositoryInterface
from src.keywords.domain.interfaces.keyword_service_interface import KeywordServiceInterface
from src.keywords.shared.exceptions import (
    KeywordNotFoundError,
    KeywordAlreadyExistsError,
    CannotActivateArchivedKeywordError,
    InvalidKeywordDataError,
)


class KeywordService(KeywordServiceInterface):
    """Сервис для работы с ключевыми словами"""

    def __init__(self, repository: KeywordRepositoryInterface):
        self.repository = repository

    async def create_keyword(
        self,
        word: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> Keyword:
        """Создать ключевое слово"""
        # Проверяем, существует ли уже такое слово
        existing = await self.repository.find_by_word(word)
        if existing:
            raise KeywordAlreadyExistsError(word)

        try:
            keyword = Keyword.create(
                word=word,
                description=description,
                category=category,
                priority=priority,
                group_id=group_id,
            )
            return await self.repository.save(keyword)
        except ValueError as e:
            raise InvalidKeywordDataError(str(e))

    async def get_keyword(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        keyword = await self.repository.find_by_id(keyword_id)
        if not keyword:
            raise KeywordNotFoundError(keyword_id)
        return keyword

    async def get_keywords(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Keyword]:
        """Получить список ключевых слов"""
        return await self.repository.find_all(
            active_only=active_only,
            category=category,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def update_keyword(
        self,
        keyword_id: int,
        word: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        group_id: Optional[int] = None,
    ) -> bool:
        """Обновить ключевое слово"""
        keyword = await self.get_keyword(keyword_id)

        # Если меняем слово, проверяем, не существует ли уже такое
        if word and word != str(keyword.word):
            existing = await self.repository.find_by_word(word)
            if existing:
                raise KeywordAlreadyExistsError(word)

        try:
            keyword.update(
                word=word,
                description=description,
                category=category,
                priority=priority,
                group_id=group_id,
            )
            return await self.repository.update(keyword)
        except ValueError as e:
            raise InvalidKeywordDataError(str(e))

    async def delete_keyword(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        keyword = await self.get_keyword(keyword_id)
        return await self.repository.delete(keyword_id)

    async def activate_keyword(self, keyword_id: int) -> bool:
        """Активировать ключевое слово"""
        keyword = await self.get_keyword(keyword_id)

        try:
            keyword.activate()
            return await self.repository.update(keyword)
        except CannotActivateArchivedKeywordError:
            raise

    async def deactivate_keyword(self, keyword_id: int) -> bool:
        """Деактивировать ключевое слово"""
        keyword = await self.get_keyword(keyword_id)
        keyword.deactivate()
        return await self.repository.update(keyword)

    async def archive_keyword(self, keyword_id: int) -> bool:
        """Архивировать ключевое слово"""
        keyword = await self.get_keyword(keyword_id)
        keyword.archive()
        return await self.repository.update(keyword)

    async def get_keyword_stats(self) -> dict:
        """Получить статистику по ключевым словам"""
        total_count = await self.repository.count_total()
        active_count = await self.repository.count_active()
        recent_count = await self.repository.count_by_period(7)  # за неделю

        return {
            "total_keywords": total_count,
            "active_keywords": active_count,
            "archived_keywords": total_count - active_count,
            "recent_keywords": recent_count,
        }