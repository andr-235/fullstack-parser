"""
Модели для модуля Keywords

Определяет репозиторий для работы с ключевыми словами
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db_session


class KeywordsRepository:
    """
    Репозиторий для работы с данными ключевых слов

    Предоставляет интерфейс для хранения результатов анализа
    """

    def __init__(self, db=None):
        self.db = db
        # В памяти для простоты (в продакшене использовать Redis/DB)
        self._keywords = {}
        self._next_id = 1

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def create(self, keyword_data: Dict[str, Any]) -> int:
        """
        Создать новое ключевое слово

        Args:
            keyword_data: Данные ключевого слова

        Returns:
            int: ID созданного ключевого слова
        """
        keyword_id = self._next_id
        self._next_id += 1

        keyword_data["id"] = keyword_id
        keyword_data["created_at"] = datetime.utcnow()
        keyword_data["updated_at"] = datetime.utcnow()

        self._keywords[keyword_id] = keyword_data
        return keyword_id

    async def find_by_id(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """
        Найти ключевое слово по ID

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Ключевое слово или None
        """
        return self._keywords.get(keyword_id)

    async def find_by_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Найти ключевое слово по слову

        Args:
            word: Ключевое слово

        Returns:
            Optional[Dict[str, Any]]: Ключевое слово или None
        """
        word_lower = word.lower()
        for keyword in self._keywords.values():
            if keyword["word"].lower() == word_lower:
                return keyword
        return None

    async def find_all(self) -> List[Dict[str, Any]]:
        """
        Найти все ключевые слова

        Returns:
            List[Dict[str, Any]]: Список всех ключевых слов
        """
        return list(self._keywords.values())

    async def update(
        self, keyword_id: int, update_data: Dict[str, Any]
    ) -> bool:
        """
        Обновить ключевое слово

        Args:
            keyword_id: ID ключевого слова
            update_data: Данные для обновления

        Returns:
            bool: Успешно ли обновлено
        """
        if keyword_id not in self._keywords:
            return False

        # Обновляем данные
        self._keywords[keyword_id].update(update_data)
        self._keywords[keyword_id]["updated_at"] = datetime.utcnow()

        return True

    async def delete(self, keyword_id: int) -> bool:
        """
        Удалить ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            bool: Успешно ли удалено
        """
        if keyword_id not in self._keywords:
            return False

        del self._keywords[keyword_id]
        return True

    async def count(self) -> int:
        """
        Подсчитать количество ключевых слов

        Returns:
            int: Количество ключевых слов
        """
        return len(self._keywords)

    async def exists(self, keyword_id: int) -> bool:
        """
        Проверить существование ключевого слова

        Args:
            keyword_id: ID ключевого слова

        Returns:
            bool: Существует ли ключевое слово
        """
        return keyword_id in self._keywords

    async def find_by_category(
        self, category_name: str
    ) -> List[Dict[str, Any]]:
        """
        Найти ключевые слова по категории

        Args:
            category_name: Название категории

        Returns:
            List[Dict[str, Any]]: Ключевые слова в категории
        """
        result = []
        for keyword in self._keywords.values():
            category = keyword.get("category")
            if (
                category
                and isinstance(category, dict)
                and category.get("name") == category_name
            ):
                result.append(keyword)
        return result

    async def find_active(self) -> List[Dict[str, Any]]:
        """
        Найти активные ключевые слова

        Returns:
            List[Dict[str, Any]]: Активные ключевые слова
        """
        result = []
        for keyword in self._keywords.values():
            status = keyword.get("status", {})
            if status.get("is_active", True) and not status.get(
                "is_archived", False
            ):
                result.append(keyword)
        return result

    async def bulk_create(
        self, keywords_data: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Массовая загрузка ключевых слов

        Args:
            keywords_data: Список данных ключевых слов

        Returns:
            List[int]: ID созданных ключевых слов
        """
        created_ids = []
        for keyword_data in keywords_data:
            keyword_id = await self.create(keyword_data)
            created_ids.append(keyword_id)
        return created_ids

    async def bulk_update(self, updates: List[Dict[str, Any]]) -> List[bool]:
        """
        Массовая загрузка обновлений ключевых слов

        Args:
            updates: Список обновлений (id + update_data)

        Returns:
            List[bool]: Результаты обновлений
        """
        results = []
        for update_item in updates:
            keyword_id = update_item.get("id")
            update_data = update_item.get("data", {})
            success = await self.update(keyword_id, update_data)
            results.append(success)
        return results

    async def bulk_delete(self, keyword_ids: List[int]) -> List[bool]:
        """
        Массовая загрузка удалений ключевых слов

        Args:
            keyword_ids: Список ID для удаления

        Returns:
            List[bool]: Результаты удалений
        """
        results = []
        for keyword_id in keyword_ids:
            success = await self.delete(keyword_id)
            results.append(success)
        return results

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику репозитория

        Returns:
            Dict[str, Any]: Статистика
        """
        total = len(self._keywords)
        active = 0
        archived = 0
        total_matches = 0
        categories = set()

        for keyword in self._keywords.values():
            # Считаем активные/архивированные
            status = keyword.get("status", {})
            if status.get("is_active", True):
                active += 1
            if status.get("is_archived", False):
                archived += 1

            # Считаем совпадения
            total_matches += keyword.get("match_count", 0)

            # Собираем категории
            category = keyword.get("category")
            if category and isinstance(category, dict):
                categories.add(category.get("name"))

        return {
            "total_keywords": total,
            "active_keywords": active,
            "archived_keywords": archived,
            "inactive_keywords": total - active,
            "total_categories": len(categories),
            "total_matches": total_matches,
            "avg_matches_per_keyword": (
                total_matches / total if total > 0 else 0
            ),
        }

    async def search(self, query: str, **filters) -> List[Dict[str, Any]]:
        """
        Поиск ключевых слов

        Args:
            query: Поисковый запрос
            **filters: Дополнительные фильтры

        Returns:
            List[Dict[str, Any]]: Найденные ключевые слова
        """
        query_lower = query.lower()
        results = []

        for keyword in self._keywords.values():
            # Поиск в слове
            if query_lower in keyword["word"].lower():
                results.append(keyword)
                continue

            # Поиск в описании
            if (
                keyword.get("description")
                and query_lower in keyword["description"].lower()
            ):
                results.append(keyword)
                continue

            # Поиск в категории
            category = keyword.get("category")
            if category and isinstance(category, dict):
                if query_lower in category.get("name", "").lower():
                    results.append(keyword)
                    continue
                if query_lower in category.get("description", "").lower():
                    results.append(keyword)
                    continue

        return results

    async def clear(self) -> int:
        """
        Очистить все ключевые слова

        Returns:
            int: Количество удаленных ключевых слов
        """
        count = len(self._keywords)
        self._keywords.clear()
        self._next_id = 1
        return count

    async def get_categories(self) -> List[str]:
        """
        Получить список всех категорий

        Returns:
            List[str]: Список категорий
        """
        categories = set()
        for keyword in self._keywords.values():
            category = keyword.get("category")
            if category and isinstance(category, dict):
                categories.add(category.get("name"))
        return sorted(list(categories))

    async def get_categories_with_stats(self) -> List[Dict[str, Any]]:
        """
        Получить категории со статистикой

        Returns:
            List[Dict[str, Any]]: Категории со статистикой
        """
        category_stats = {}

        for keyword in self._keywords.values():
            category = keyword.get("category")
            if category and isinstance(category, dict):
                cat_name = category.get("name")
                if cat_name not in category_stats:
                    category_stats[cat_name] = {
                        "category_name": cat_name,
                        "keyword_count": 0,
                        "active_count": 0,
                        "total_matches": 0,
                    }

                category_stats[cat_name]["keyword_count"] += 1

                status = keyword.get("status", {})
                if status.get("is_active", True):
                    category_stats[cat_name]["active_count"] += 1

                category_stats[cat_name]["total_matches"] += keyword.get(
                    "match_count", 0
                )

        return list(category_stats.values())


# Функции для создания репозитория
async def get_keywords_repository(db=None) -> KeywordsRepository:
    """Создать репозиторий ключевых слов"""
    return KeywordsRepository(db)


# Экспорт
__all__ = [
    "KeywordsRepository",
    "get_keywords_repository",
]
