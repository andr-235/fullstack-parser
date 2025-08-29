"""
Application Service для ключевых слов (DDD)
"""

from typing import List, Optional, Dict, Any
from ..domain.keyword import Keyword, KeywordCategory, KeywordStatus
from .base import ApplicationService


class KeywordApplicationService(ApplicationService):
    """Application Service для работы с ключевыми словами"""

    def __init__(self, keyword_repository):
        self.keyword_repository = keyword_repository

    async def get_keyword_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Получить ключевое слово по ID"""
        return await self.keyword_repository.find_by_id(keyword_id)

    async def get_keywords(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Keyword]:
        """Получить список ключевых слов с фильтрами"""
        keywords = await self.keyword_repository.find_all()

        # Фильтрация по активности
        if active_only:
            keywords = [k for k in keywords if k.is_active]

        # Фильтрация по категории
        if category:
            keywords = [k for k in keywords if k.category_name == category]

        # Фильтрация по поисковому запросу
        if search:
            search_lower = search.lower()
            keywords = [k for k in keywords if search_lower in k.word.lower()]

        return keywords[offset : offset + limit]

    async def create_keyword(
        self,
        word: str,
        category_name: Optional[str] = None,
        category_description: Optional[str] = None,
    ) -> Keyword:
        """Создать новое ключевое слово"""
        category = None
        if category_name:
            category = KeywordCategory(
                name=category_name, description=category_description
            )

        keyword = Keyword(word=word, category=category)

        await self.keyword_repository.save(keyword)
        return keyword

    async def update_keyword(
        self,
        keyword_id: int,
        word: Optional[str] = None,
        category_name: Optional[str] = None,
        category_description: Optional[str] = None,
    ) -> bool:
        """Обновить ключевое слово"""
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return False

        if word:
            keyword.word = word

        if category_name:
            keyword.category = KeywordCategory(
                name=category_name, description=category_description
            )

        keyword.update()
        await self.keyword_repository.save(keyword)
        return True

    async def activate_keyword(self, keyword_id: int) -> bool:
        """Активировать ключевое слово"""
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return False

        keyword.activate()
        await self.keyword_repository.save(keyword)
        return True

    async def deactivate_keyword(self, keyword_id: int) -> bool:
        """Деактивировать ключевое слово"""
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return False

        keyword.deactivate()
        await self.keyword_repository.save(keyword)
        return True

    async def archive_keyword(self, keyword_id: int) -> bool:
        """Архивировать ключевое слово"""
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return False

        keyword.archive()
        await self.keyword_repository.save(keyword)
        return True

    async def delete_keyword(self, keyword_id: int) -> bool:
        """Удалить ключевое слово"""
        return await self.keyword_repository.delete(keyword_id)

    async def get_keywords_by_category(
        self, category_name: str
    ) -> List[Keyword]:
        """Получить ключевые слова по категории"""
        keywords = await self.keyword_repository.find_all()
        return [k for k in keywords if k.category_name == category_name]

    async def get_available_categories(self) -> List[str]:
        """Получить список доступных категорий"""
        keywords = await self.keyword_repository.find_all()

        categories = set()
        for keyword in keywords:
            if keyword.category_name:
                categories.add(keyword.category_name)

        return sorted(list(categories))

    async def search_keywords(self, query: str) -> List[Keyword]:
        """Поиск ключевых слов"""
        keywords = await self.keyword_repository.find_all()

        query_lower = query.lower()
        return [
            k
            for k in keywords
            if query_lower in k.word.lower()
            or (k.category_name and query_lower in k.category_name.lower())
        ]

    async def get_keywords_statistics(self) -> Dict[str, Any]:
        """Получить статистику по ключевым словам"""
        keywords = await self.keyword_repository.find_all()

        total_keywords = len(keywords)
        active_keywords = len([k for k in keywords if k.is_active])
        archived_keywords = len([k for k in keywords if k.is_archived])

        # Статистика по категориям
        categories_stats = {}
        for keyword in keywords:
            if keyword.category_name:
                if keyword.category_name not in categories_stats:
                    categories_stats[keyword.category_name] = {
                        "total": 0,
                        "active": 0,
                        "archived": 0,
                    }
                categories_stats[keyword.category_name]["total"] += 1
                if keyword.is_active:
                    categories_stats[keyword.category_name]["active"] += 1
                if keyword.is_archived:
                    categories_stats[keyword.category_name]["archived"] += 1

        return {
            "total_keywords": total_keywords,
            "active_keywords": active_keywords,
            "inactive_keywords": total_keywords
            - active_keywords
            - archived_keywords,
            "archived_keywords": archived_keywords,
            "categories_count": len(categories_stats),
            "categories_stats": categories_stats,
        }
