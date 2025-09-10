"""
Модели для модуля Keywords

Определяет репозиторий для работы с ключевыми словами
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update

from ..database import get_db_session
from ..models import Keyword


class KeywordsRepository:
    """
    Репозиторий для работы с данными ключевых слов

    Предоставляет интерфейс для хранения результатов анализа
    """

    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db

    async def get_db(self) -> AsyncSession:
        """Получить сессию БД"""
        if self.db:
            return self.db
        else:
            # Создаем новую асинхронную сессию
            from ..database import get_db

            return await get_db()

    async def create(self, keyword_data: Dict[str, Any]) -> int:
        """
        Создать новое ключевое слово

        Args:
            keyword_data: Данные ключевого слова

        Returns:
            int: ID созданного ключевого слова
        """
        db = await self.get_db()

        # Извлекаем данные категории
        category = keyword_data.get("category")
        category_name = None
        category_description = None
        if category and isinstance(category, dict):
            category_name = category.get("name")
            category_description = category.get("description")

        # Извлекаем статус
        status = keyword_data.get("status", {})
        is_active = status.get("is_active", True)
        is_archived = status.get("is_archived", False)

        keyword = Keyword(
            word=keyword_data["word"],
            description=keyword_data.get("description"),
            category_name=category_name,
            category_description=category_description,
            priority=keyword_data.get("priority", 5),
            match_count=keyword_data.get("match_count", 0),
            is_active=is_active,
            is_archived=is_archived,
            group_id=keyword_data.get("group_id"),
        )

        db.add(keyword)
        await db.commit()
        await db.refresh(keyword)

        return int(keyword.id)

    async def find_by_id(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """
        Найти ключевое слово по ID

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Ключевое слово или None
        """
        db = await self.get_db()
        stmt = select(Keyword).where(Keyword.id == keyword_id)
        result = await db.execute(stmt)
        keyword = result.scalar_one_or_none()

        if keyword:
            return self._keyword_to_dict(keyword)
        return None

    async def find_by_word(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Найти ключевое слово по слову

        Args:
            word: Ключевое слово

        Returns:
            Optional[Dict[str, Any]]: Ключевое слово или None
        """
        db = await self.get_db()
        stmt = select(Keyword).where(Keyword.word == word)
        result = await db.execute(stmt)
        keyword = result.scalar_one_or_none()

        if keyword:
            return self._keyword_to_dict(keyword)
        return None

    async def find_all(self) -> List[Dict[str, Any]]:
        """
        Найти все ключевые слова

        Returns:
            List[Dict[str, Any]]: Список всех ключевых слов
        """
        db = await self.get_db()
        stmt = select(Keyword).order_by(Keyword.created_at.desc())
        result = await db.execute(stmt)
        results = result.scalars().all()

        return [self._keyword_to_dict(keyword) for keyword in results]

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
        db = await self.get_db()
        stmt = select(Keyword).where(Keyword.id == keyword_id)
        result = await db.execute(stmt)
        keyword = result.scalar_one_or_none()

        if not keyword:
            return False

        # Обновляем поля
        for field, value in update_data.items():
            if hasattr(keyword, field) and field != "updated_at":
                setattr(keyword, field, value)

        # Обновляем время изменения через SQLAlchemy
        update_stmt = (
            update(Keyword)
            .where(Keyword.id == keyword_id)
            .values(updated_at=datetime.utcnow())
        )
        await db.execute(update_stmt)

        await db.commit()
        return True

    async def delete(self, keyword_id: int) -> bool:
        """
        Удалить ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            bool: Успешно ли удалено
        """
        db = await self.get_db()
        stmt = select(Keyword).where(Keyword.id == keyword_id)
        result = await db.execute(stmt)
        keyword = result.scalar_one_or_none()

        if not keyword:
            return False

        await db.delete(keyword)
        await db.commit()
        return True

    async def count(self) -> int:
        """
        Подсчитать количество ключевых слов

        Returns:
            int: Количество ключевых слов
        """
        db = await self.get_db()
        stmt = select(func.count(Keyword.id))
        result = await db.execute(stmt)
        value = result.scalar()
        return result or 0

    async def exists(self, keyword_id: int) -> bool:
        """
        Проверить существование ключевого слова

        Args:
            keyword_id: ID ключевого слова

        Returns:
            bool: Существует ли ключевое слово
        """
        db = await self.get_db()
        stmt = select(Keyword.id).where(Keyword.id == keyword_id)
        result = await db.execute(stmt)
        keyword = result.scalar_one_or_none()
        return result is not None

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
        db = await self.get_db()
        stmt = select(Keyword).where(Keyword.category_name == category_name)
        result = await db.execute(stmt)
        results = result.scalars().all()

        return [self._keyword_to_dict(keyword) for keyword in results]

    async def find_active(self) -> List[Dict[str, Any]]:
        """
        Найти активные ключевые слова

        Returns:
            List[Dict[str, Any]]: Активные ключевые слова
        """
        db = await self.get_db()
        stmt = select(Keyword).where(
            and_(Keyword.is_active == True, Keyword.is_archived == False)
        )
        result = await db.execute(stmt)
        results = result.scalars().all()

        return [self._keyword_to_dict(keyword) for keyword in results]

    def _keyword_to_dict(self, keyword: Keyword) -> Dict[str, Any]:
        """
        Преобразовать объект Keyword в словарь

        Args:
            keyword: Объект Keyword

        Returns:
            Dict[str, Any]: Словарь с данными ключевого слова
        """
        result = {
            "id": keyword.id,
            "word": keyword.word,
            "description": keyword.description,
            "priority": keyword.priority,
            "match_count": keyword.match_count,
            "group_id": keyword.group_id,
            "created_at": keyword.created_at,
            "updated_at": keyword.updated_at,
            "status": {
                "is_active": keyword.is_active,
                "is_archived": keyword.is_archived,
            },
        }

        # Добавляем категорию, если есть
        if keyword.category_name:
            result["category"] = {
                "name": keyword.category_name,
                "description": keyword.category_description,
            }

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
            if keyword_id is not None and isinstance(keyword_id, int):
                success = await self.update(keyword_id, update_data)
                results.append(success)
            else:
                results.append(False)
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
        db = await self.get_db()

        # Общая статистика
        total_stmt = select(func.count(Keyword.id))
        total = db.execute(total_stmt).scalar() or 0

        # Активные ключевые слова
        active_stmt = select(func.count(Keyword.id)).where(
            Keyword.is_active == True
        )
        active = db.execute(active_stmt).scalar() or 0

        # Архивированные ключевые слова
        archived_stmt = select(func.count(Keyword.id)).where(
            Keyword.is_archived == True
        )
        archived = db.execute(archived_stmt).scalar() or 0

        # Общее количество совпадений
        matches_stmt = select(func.sum(Keyword.match_count))
        total_matches = db.execute(matches_stmt).scalar() or 0

        # Количество категорий
        categories_stmt = select(
            func.count(func.distinct(Keyword.category_name))
        ).where(Keyword.category_name.isnot(None))
        total_categories = db.execute(categories_stmt).scalar() or 0

        return {
            "total_keywords": total,
            "active_keywords": active,
            "archived_keywords": archived,
            "inactive_keywords": total - active,
            "total_categories": total_categories,
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
        db = await self.get_db()

        # Поиск по слову, описанию и категории
        stmt = select(Keyword).where(
            or_(
                Keyword.word.ilike(f"%{query}%"),
                Keyword.description.ilike(f"%{query}%"),
                Keyword.category_name.ilike(f"%{query}%"),
                Keyword.category_description.ilike(f"%{query}%"),
            )
        )

        result = await db.execute(stmt)
        results = result.scalars().all()
        return [self._keyword_to_dict(keyword) for keyword in results]

    async def clear(self) -> int:
        """
        Очистить все ключевые слова

        Returns:
            int: Количество удаленных ключевых слов
        """
        db = await self.get_db()

        # Подсчитываем количество перед удалением
        count_stmt = select(func.count(Keyword.id))
        count = db.execute(count_stmt).scalar() or 0

        # Удаляем все ключевые слова
        delete_stmt = select(Keyword)
        keywords_to_delete = db.execute(delete_stmt).scalars().all()

        for keyword in keywords_to_delete:
            await db.delete(keyword)

        await db.commit()
        return count

    async def get_categories(self) -> List[str]:
        """
        Получить список всех категорий

        Returns:
            List[str]: Список категорий
        """
        db = await self.get_db()
        stmt = select(func.distinct(Keyword.category_name)).where(
            Keyword.category_name.isnot(None)
        )
        result = await db.execute(stmt)
        results = result.scalars().all()
        return sorted([cat for cat in results if cat])

    async def get_categories_with_stats(self) -> List[Dict[str, Any]]:
        """
        Получить категории со статистикой

        Returns:
            List[Dict[str, Any]]: Категории со статистикой
        """
        db = await self.get_db()

        # Получаем статистику по категориям
        stmt = (
            select(
                Keyword.category_name,
                func.count(Keyword.id).label("keyword_count"),
                func.sum(
                    func.case((Keyword.is_active == True, 1), else_=0)
                ).label("active_count"),
                func.sum(Keyword.match_count).label("total_matches"),
            )
            .where(Keyword.category_name.isnot(None))
            .group_by(Keyword.category_name)
        )

        result = await db.execute(stmt)
        results = result.all()

        category_stats = []
        for row in results:
            category_stats.append(
                {
                    "category_name": row.category_name,
                    "keyword_count": row.keyword_count,
                    "active_count": row.active_count,
                    "total_matches": row.total_matches or 0,
                }
            )

        return category_stats


# Функции для создания репозитория
async def get_keywords_repository(
    db: Optional[AsyncSession] = None,
) -> KeywordsRepository:
    """Создать репозиторий ключевых слов"""
    return KeywordsRepository(db)


# Экспорт
__all__ = [
    "KeywordsRepository",
    "get_keywords_repository",
]
