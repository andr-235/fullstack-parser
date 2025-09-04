"""
Сервис для работы с ключевыми словами

Содержит бизнес-логику для операций с ключевыми словами
"""

import json
import csv
import io
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from ..exceptions import (
    ValidationError,
    NotFoundError,
    ServiceUnavailableError,
)
from .models import KeywordsRepository
from .constants import (
    MAX_KEYWORD_LENGTH,
    MAX_KEYWORDS_PER_REQUEST,
    MAX_DESCRIPTION_LENGTH,
    MAX_CATEGORY_LENGTH,
    DEFAULT_PRIORITY,
    MIN_PRIORITY,
    MAX_PRIORITY,
    ALLOWED_EXPORT_FORMATS,
    ALLOWED_BULK_ACTIONS,
)


class KeywordsService:
    """
    Сервис для работы с ключевыми словами

    Реализует бизнес-логику для CRUD операций с ключевыми словами
    """

    def __init__(self, repository: KeywordsRepository):
        self.repository = repository

    async def create_keyword(
        self, keyword_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать новое ключевое слово

        Args:
            keyword_data: Данные ключевого слова

        Returns:
            Dict[str, Any]: Созданное ключевое слово
        """
        # Валидация входных данных
        self._validate_keyword_data(keyword_data)

        word = keyword_data["word"]
        category_name = keyword_data.get("category_name")
        category_description = keyword_data.get("category_description")
        description = keyword_data.get("description")
        priority = keyword_data.get("priority", DEFAULT_PRIORITY)

        # Проверка на дубликаты
        existing = await self.repository.find_by_word(word)
        if existing:
            raise ValidationError(
                "Ключевое слово уже существует", field="word"
            )

        # Создание категории, если указана
        category_data = None
        if category_name:
            category_data = {
                "name": category_name,
                "description": category_description,
            }

        # Создание ключевого слова
        keyword_dict = {
            "word": word,
            "category": category_data,
            "description": description,
            "priority": priority,
            "match_count": 0,
            "status": {
                "is_active": True,
                "is_archived": False,
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        keyword_id = await self.repository.create(keyword_dict)
        keyword_dict["id"] = keyword_id

        return keyword_dict

    async def get_keyword(self, keyword_id: int) -> Optional[Dict[str, Any]]:
        """
        Получить ключевое слово по ID

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Ключевое слово или None
        """
        return await self.repository.find_by_id(keyword_id)

    async def get_keywords(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        **filters,
    ) -> Dict[str, Any]:
        """
        Получить список ключевых слов с фильтрами

        Args:
            active_only: Только активные ключевые слова
            category: Фильтр по категории
            search: Поисковый запрос
            limit: Количество результатов
            offset: Смещение
            **filters: Дополнительные фильтры

        Returns:
            Dict[str, Any]: Результаты поиска с пагинацией
        """
        # Получение ключевых слов
        keywords = await self.repository.find_all()

        # Применение фильтров
        filtered_keywords = self._apply_filters(
            keywords, active_only, category, search, **filters
        )

        # Пагинация
        total = len(filtered_keywords)
        paginated_keywords = filtered_keywords[offset : offset + limit]

        # Вычисляем параметры пагинации
        if limit <= 0:
            limit = 50  # Значение по умолчанию
        page = (offset // limit) + 1
        pages = (total + limit - 1) // limit

        return {
            "items": paginated_keywords,
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages,
        }

    async def update_keyword(
        self, keyword_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить ключевое слово

        Args:
            keyword_id: ID ключевого слова
            update_data: Данные для обновления

        Returns:
            Optional[Dict[str, Any]]: Обновленное ключевое слово или None
        """
        # Проверка существования ключевого слова
        existing = await self.repository.find_by_id(keyword_id)
        if not existing:
            return None

        # Валидация данных обновления
        await self._validate_update_data(update_data, existing)

        # Подготовка данных для обновления
        update_dict = {}
        if "word" in update_data:
            update_dict["word"] = update_data["word"]
        if "description" in update_data:
            update_dict["description"] = update_data["description"]
        if "priority" in update_data:
            update_dict["priority"] = update_data["priority"]

        # Обновление категории
        if "category_name" in update_data:
            update_dict["category"] = {
                "name": update_data["category_name"],
                "description": update_data.get("category_description"),
            }

        update_dict["updated_at"] = datetime.utcnow()

        # Обновление в репозитории
        success = await self.repository.update(keyword_id, update_dict)
        if success:
            return await self.repository.find_by_id(keyword_id)

        return None

    async def delete_keyword(self, keyword_id: int) -> bool:
        """
        Удалить ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            bool: Успешно ли удалено
        """
        # Проверка существования ключевого слова
        existing = await self.repository.find_by_id(keyword_id)
        if not existing:
            return False

        # Проверка статуса (нельзя удалять активные ключевые слова)
        if existing.get("status", {}).get("is_active", True):
            raise ValidationError(
                "Нельзя удалять активное ключевое слово. Сначала деактивируйте его."
            )

        return await self.repository.delete(keyword_id)

    async def activate_keyword(
        self, keyword_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Активировать ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Активированное ключевое слово или None
        """
        existing = await self.repository.find_by_id(keyword_id)
        if not existing:
            return None

        if existing.get("status", {}).get("is_archived", False):
            raise ValidationError(
                "Нельзя активировать архивированное ключевое слово"
            )

        update_data = {
            "status": {
                "is_active": True,
                "is_archived": False,
            },
            "updated_at": datetime.utcnow(),
        }

        success = await self.repository.update(keyword_id, update_data)
        if success:
            return await self.repository.find_by_id(keyword_id)

        return None

    async def deactivate_keyword(
        self, keyword_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Деактивировать ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Деактивированное ключевое слово или None
        """
        existing = await self.repository.find_by_id(keyword_id)
        if not existing:
            return None

        update_data = {
            "status": {
                "is_active": False,
                "is_archived": False,
            },
            "updated_at": datetime.utcnow(),
        }

        success = await self.repository.update(keyword_id, update_data)
        if success:
            return await self.repository.find_by_id(keyword_id)

        return None

    async def archive_keyword(
        self, keyword_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Архивировать ключевое слово

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Optional[Dict[str, Any]]: Архивированное ключевое слово или None
        """
        existing = await self.repository.find_by_id(keyword_id)
        if not existing:
            return None

        update_data = {
            "status": {
                "is_active": False,
                "is_archived": True,
            },
            "updated_at": datetime.utcnow(),
        }

        success = await self.repository.update(keyword_id, update_data)
        if success:
            return await self.repository.find_by_id(keyword_id)

        return None

    async def bulk_create_keywords(
        self, keywords_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Массовая загрузка ключевых слов

        Args:
            keywords_data: Список данных ключевых слов

        Returns:
            Dict[str, Any]: Результат массовой загрузки
        """
        if len(keywords_data) > MAX_KEYWORDS_PER_REQUEST:
            raise ValidationError(
                f"Максимум {MAX_KEYWORDS_PER_REQUEST} ключевых слов за один запрос"
            )

        successful = 0
        failed = 0
        errors = []

        for i, keyword_data in enumerate(keywords_data):
            try:
                await self.create_keyword(keyword_data)
                successful += 1
            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "index": i,
                        "word": keyword_data.get("word", "unknown"),
                        "error": str(e),
                    }
                )

        return {
            "total_requested": len(keywords_data),
            "successful": successful,
            "failed": failed,
            "errors": errors,
        }

    async def bulk_action(
        self, keyword_ids: List[int], action: str
    ) -> Dict[str, Any]:
        """
        Массовая операция с ключевыми словами

        Args:
            keyword_ids: ID ключевых слов
            action: Действие (activate, deactivate, archive, delete)

        Returns:
            Dict[str, Any]: Результат массовой операции
        """
        if action not in ALLOWED_BULK_ACTIONS:
            raise ValidationError(f"Недопустимое действие: {action}")

        successful = 0
        failed = 0
        errors = []

        for keyword_id in keyword_ids:
            try:
                if action == "activate":
                    result = await self.activate_keyword(keyword_id)
                elif action == "deactivate":
                    result = await self.deactivate_keyword(keyword_id)
                elif action == "archive":
                    result = await self.archive_keyword(keyword_id)
                elif action == "delete":
                    success = await self.delete_keyword(keyword_id)
                    result = (
                        await self.get_keyword(keyword_id) if success else None
                    )

                if result is not None:
                    successful += 1
                else:
                    failed += 1
                    errors.append(
                        {
                            "keyword_id": keyword_id,
                            "error": "Ключевое слово не найдено",
                        }
                    )
            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "keyword_id": keyword_id,
                        "error": str(e),
                    }
                )

        return {
            "total_requested": len(keyword_ids),
            "successful": successful,
            "failed": failed,
            "errors": errors,
        }

    async def search_keywords(
        self, query: str, **filters
    ) -> List[Dict[str, Any]]:
        """
        Поиск ключевых слов

        Args:
            query: Поисковый запрос
            **filters: Дополнительные фильтры

        Returns:
            List[Dict[str, Any]]: Найденные ключевые слова
        """
        keywords = await self.repository.find_all()
        query_lower = query.lower()

        results = []
        for keyword in keywords:
            # Поиск в слове
            if query_lower in keyword["word"].lower():
                results.append(keyword)
                continue

            # Поиск в категории
            category = keyword.get("category")
            if category and query_lower in category["name"].lower():
                results.append(keyword)
                continue

            # Поиск в описании
            if (
                keyword.get("description")
                and query_lower in keyword["description"].lower()
            ):
                results.append(keyword)
                continue

        # Применение дополнительных фильтров
        return self._apply_filters(results, **filters)

    async def get_categories(self) -> List[str]:
        """
        Получить список всех категорий

        Returns:
            List[str]: Список категорий
        """
        keywords = await self.repository.find_all()

        categories = set()
        for keyword in keywords:
            category = keyword.get("category")
            if category:
                categories.add(category["name"])

        return sorted(list(categories))

    async def get_categories_with_stats(self) -> List[Dict[str, Any]]:
        """
        Получить категории со статистикой

        Returns:
            List[Dict[str, Any]]: Категории со статистикой
        """
        keywords = await self.repository.find_all()

        category_stats: Dict[str, Dict[str, Any]] = {}
        for keyword in keywords:
            category = keyword.get("category")
            if category:
                cat_name = category["name"]
                if cat_name not in category_stats:
                    category_stats[cat_name] = {
                        "category_name": cat_name,
                        "keyword_count": 0,
                        "active_count": 0,
                        "total_matches": 0,
                    }

                category_stats[cat_name]["keyword_count"] += 1
                if keyword.get("status", {}).get("is_active", True):
                    category_stats[cat_name]["active_count"] += 1
                category_stats[cat_name]["total_matches"] += keyword.get(
                    "match_count", 0
                )

        return list(category_stats.values())

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику ключевых слов

        Returns:
            Dict[str, Any]: Статистика
        """
        keywords = await self.repository.find_all()

        total_keywords = len(keywords)
        active_keywords = sum(
            1 for k in keywords if k.get("status", {}).get("is_active", True)
        )
        archived_keywords = sum(
            1
            for k in keywords
            if k.get("status", {}).get("is_archived", False)
        )

        # Категории
        categories = set()
        total_matches = 0
        for keyword in keywords:
            category = keyword.get("category")
            if category:
                categories.add(category["name"])
            total_matches += keyword.get("match_count", 0)

        # Топ категорий
        category_counts: Dict[str, int] = {}
        for keyword in keywords:
            category = keyword.get("category")
            if category:
                cat_name = category["name"]
                category_counts[cat_name] = (
                    category_counts.get(cat_name, 0) + 1
                )

        # Формируем типизированный список для надежной сортировки по count (int)
        category_items: List[Dict[str, Any]] = [
            {"name": name, "count": count}
            for name, count in category_counts.items()
        ]
        top_categories = sorted(
            category_items, key=lambda x: x["count"], reverse=True
        )[:5]

        return {
            "total_keywords": total_keywords,
            "active_keywords": active_keywords,
            "archived_keywords": archived_keywords,
            "total_categories": len(categories),
            "total_matches": total_matches,
            "avg_matches_per_keyword": (
                total_matches / total_keywords if total_keywords > 0 else 0
            ),
            "top_categories": top_categories,
        }

    async def export_keywords(
        self, format_type: str = "json", **filters
    ) -> Dict[str, Any]:
        """
        Экспорт ключевых слов

        Args:
            format_type: Формат экспорта
            **filters: Фильтры

        Returns:
            Dict[str, Any]: Результат экспорта
        """
        if format_type not in ALLOWED_EXPORT_FORMATS:
            raise ValidationError(
                f"Недопустимый формат экспорта: {format_type}"
            )

        # Получение ключевых слов с фильтрами
        result = await self.get_keywords(**filters)
        keywords = result["items"]

        if format_type == "json":
            export_data = json.dumps(
                keywords, indent=2, default=str, ensure_ascii=False
            )
            filename = "keywords_export.json"
        elif format_type == "csv":
            export_data = self._export_to_csv(keywords)
            filename = "keywords_export.csv"
        elif format_type == "txt":
            export_data = self._export_to_txt(keywords)
            filename = "keywords_export.txt"

        return {
            "export_data": export_data,
            "format": format_type,
            "total_exported": len(keywords),
            "filename": filename,
        }

    async def import_keywords(
        self, import_data: str, update_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Импорт ключевых слов

        Args:
            import_data: Данные для импорта в формате JSON
            update_existing: Обновлять существующие ключевые слова

        Returns:
            Dict[str, Any]: Результат импорта
        """
        try:
            keywords_data = json.loads(import_data)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Неверный формат JSON: {str(e)}")

        if not isinstance(keywords_data, list):
            raise ValidationError("Данные должны быть списком ключевых слов")

        successful = 0
        failed = 0
        updated = 0
        errors = []

        for i, keyword_data in enumerate(keywords_data):
            try:
                word = keyword_data.get("word")
                if not word:
                    raise ValidationError("Отсутствует поле 'word'")

                # Проверка существования
                existing = await self.repository.find_by_word(word)
                if existing:
                    if update_existing:
                        # Обновление существующего
                        await self.repository.update(
                            existing["id"], keyword_data
                        )
                        updated += 1
                    else:
                        raise ValidationError(
                            f"Ключевое слово '{word}' уже существует"
                        )
                else:
                    # Создание нового
                    await self.create_keyword(keyword_data)
                    successful += 1

            except Exception as e:
                failed += 1
                errors.append(
                    {
                        "index": i,
                        "word": keyword_data.get("word", "unknown"),
                        "error": str(e),
                    }
                )

        return {
            "total_imported": len(keywords_data),
            "successful": successful,
            "updated": updated,
            "failed": failed,
            "errors": errors,
        }

    async def validate_keywords(self, words: List[str]) -> Dict[str, Any]:
        """
        Валидация списка слов для использования в качестве ключевых слов

        Args:
            words: Список слов для валидации

        Returns:
            Dict[str, Any]: Результат валидации
        """
        valid_keywords = []
        invalid_keywords = []
        suggestions = {}

        for word in words:
            is_valid, error = self._validate_keyword_word(word)
            if is_valid:
                valid_keywords.append(word)
            else:
                invalid_keywords.append(word)
                suggestions[word] = [f"Исправьте: {error}"]

        return {
            "valid_keywords": valid_keywords,
            "invalid_keywords": invalid_keywords,
            "suggestions": suggestions,
        }

    def _validate_keyword_data(self, data: Dict[str, Any]) -> None:
        """Валидация данных ключевого слова"""
        if not data.get("word"):
            raise ValidationError("Ключевое слово обязательно", field="word")

        if len(data["word"]) > MAX_KEYWORD_LENGTH:
            raise ValidationError(
                f"Ключевое слово слишком длинное (макс {MAX_KEYWORD_LENGTH} символов)",
                field="word",
            )

        if (
            data.get("description")
            and len(data["description"]) > MAX_DESCRIPTION_LENGTH
        ):
            raise ValidationError(
                f"Описание слишком длинное (макс {MAX_DESCRIPTION_LENGTH} символов)",
                field="description",
            )

        if (
            data.get("category_name")
            and len(data["category_name"]) > MAX_CATEGORY_LENGTH
        ):
            raise ValidationError(
                f"Название категории слишком длинное (макс {MAX_CATEGORY_LENGTH} символов)",
                field="category_name",
            )

        priority = data.get("priority", DEFAULT_PRIORITY)
        if not (MIN_PRIORITY <= priority <= MAX_PRIORITY):
            raise ValidationError(
                f"Приоритет должен быть от {MIN_PRIORITY} до {MAX_PRIORITY}",
                field="priority",
            )

    async def _validate_update_data(
        self, data: Dict[str, Any], existing: Dict[str, Any]
    ) -> None:
        """Валидация данных обновления"""
        if "word" in data:
            self._validate_keyword_data({"word": data["word"]})

            # Проверка на дубликаты
            if data["word"] != existing["word"]:
                duplicate = await self.repository.find_by_word(data["word"])
                if duplicate:
                    raise ValidationError(
                        "Ключевое слово уже существует", field="word"
                    )

    def _validate_keyword_word(self, word: str) -> Tuple[bool, str]:
        """Валидация отдельного слова"""
        if not word or not word.strip():
            return False, "Слово не может быть пустым"

        word = word.strip()
        if len(word) > MAX_KEYWORD_LENGTH:
            return (
                False,
                f"Слово слишком длинное (макс {MAX_KEYWORD_LENGTH} символов)",
            )

        # Проверка на допустимые символы
        if (
            not word.replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .isalnum()
        ):
            return False, "Слово содержит недопустимые символы"

        return True, ""

    def _apply_filters(
        self,
        keywords: List[Dict[str, Any]],
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        **filters,
    ) -> List[Dict[str, Any]]:
        """Применение фильтров к списку ключевых слов"""
        filtered = keywords

        # Фильтр по активности
        if active_only:
            filtered = [
                k
                for k in filtered
                if k.get("status", {}).get("is_active", True)
            ]

        # Фильтр по категории
        if category:
            filtered = [
                k
                for k in filtered
                if k.get("category", {}).get("name") == category
            ]

        # Поисковый фильтр
        if search:
            search_lower = search.lower()
            filtered = [
                k
                for k in filtered
                if search_lower in k["word"].lower()
                or (
                    k.get("category", {})
                    .get("name", "")
                    .lower()
                    .find(search_lower)
                    != -1
                )
                or (k.get("description", "").lower().find(search_lower) != -1)
            ]

        # Дополнительные фильтры
        if "priority_min" in filters:
            filtered = [
                k
                for k in filtered
                if k.get("priority", 0) >= filters["priority_min"]
            ]

        if "priority_max" in filters:
            filtered = [
                k
                for k in filtered
                if k.get("priority", 0) <= filters["priority_max"]
            ]

        if "match_count_min" in filters:
            filtered = [
                k
                for k in filtered
                if k.get("match_count", 0) >= filters["match_count_min"]
            ]

        if "match_count_max" in filters:
            filtered = [
                k
                for k in filtered
                if k.get("match_count", 0) <= filters["match_count_max"]
            ]

        return filtered

    def _export_to_csv(self, keywords: List[Dict[str, Any]]) -> str:
        """Экспорт в CSV формат"""
        if not keywords:
            return ""

        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        headers = [
            "id",
            "word",
            "category",
            "description",
            "priority",
            "is_active",
            "match_count",
            "created_at",
        ]
        writer.writerow(headers)

        # Данные
        for keyword in keywords:
            row = [
                keyword.get("id"),
                keyword.get("word"),
                keyword.get("category", {}).get("name", ""),
                keyword.get("description", ""),
                keyword.get("priority"),
                keyword.get("status", {}).get("is_active"),
                keyword.get("match_count"),
                keyword.get("created_at"),
            ]
            writer.writerow(row)

        return output.getvalue()

    def _export_to_txt(self, keywords: List[Dict[str, Any]]) -> str:
        """Экспорт в текстовый формат"""
        if not keywords:
            return ""

        lines = []
        for keyword in keywords:
            category = keyword.get("category", {}).get("name", "без категории")
            line = f"{keyword['word']} [{category}] - {keyword.get('description', 'без описания')}"
            lines.append(line)

        return "\n".join(lines)


# Экспорт
__all__ = [
    "KeywordsService",
]
