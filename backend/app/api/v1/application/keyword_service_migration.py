"""
Миграция KeywordService в DDD архитектуру

Этот файл содержит методы, мигрированные из оригинального KeywordService
в DDD Application Service.
"""

from typing import Dict, List, Optional, Any


class KeywordServiceMigration:
    """
    Методы, мигрированные из KeywordService в DDD архитектуру
    """

    async def create_keyword_ddd(
        self, keyword_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Создать ключевое слово (мигрировано из KeywordService)

        Args:
            keyword_data: Данные ключевого слова

        Returns:
            Созданное ключевое слово
        """
        from ..domain.keyword import Keyword, KeywordContent
        from datetime import datetime

        # Проверяем существование ключевого слова
        existing = await self.get_keyword_by_word(keyword_data.get("word", ""))
        if existing:
            raise ValueError(
                f"Ключевое слово '{keyword_data.get('word')}' уже существует"
            )

        # Создаем контент ключевого слова
        content = KeywordContent(
            word=keyword_data.get("word", ""),
            category=keyword_data.get("category"),
            description=keyword_data.get("description"),
        )

        # Создаем доменную сущность
        keyword = Keyword(
            id=None,  # Будет присвоен при сохранении
            content=content,
            is_active=keyword_data.get("is_active", True),
            is_case_sensitive=keyword_data.get("is_case_sensitive", False),
            is_whole_word=keyword_data.get("is_whole_word", False),
        )

        # Валидируем бизнес-правила
        keyword.validate_business_rules()

        # Сохраняем через репозиторий
        await self.keyword_repository.save(keyword)

        return await self.get_keyword_by_id(keyword.id)

    async def get_keywords_paginated_ddd(
        self,
        active_only: bool = True,
        category: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Получить ключевые слова с пагинацией и фильтрами (мигрировано из KeywordService)

        Args:
            active_only: Только активные ключевые слова
            category: Фильтр по категории
            search: Поисковый запрос
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Пагинированный результат
        """
        # Получаем все ключевые слова
        all_keywords = await self.keyword_repository.find_all()

        # Применяем фильтры
        if active_only:
            all_keywords = [k for k in all_keywords if k.is_active]

        if category:
            all_keywords = [
                k for k in all_keywords if k.content.category == category
            ]

        if search:
            search_lower = search.lower()
            all_keywords = [
                k
                for k in all_keywords
                if search_lower in k.content.word.lower()
                or (
                    k.content.description
                    and search_lower in k.content.description.lower()
                )
            ]

        # Пагинация
        total = len(all_keywords)
        paginated_keywords = all_keywords[offset : offset + limit]

        # Преобразуем в response формат
        keywords_response = []
        for keyword in paginated_keywords:
            keywords_response.append(
                {
                    "id": keyword.id,
                    "word": keyword.content.word,
                    "category": keyword.content.category,
                    "description": keyword.content.description,
                    "is_active": keyword.is_active,
                    "is_case_sensitive": keyword.is_case_sensitive,
                    "is_whole_word": keyword.is_whole_word,
                    "created_at": keyword.created_at.isoformat(),
                    "updated_at": keyword.updated_at.isoformat(),
                }
            )

        return {
            "keywords": keywords_response,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": len(paginated_keywords) == limit,
            "has_prev": offset > 0,
        }

    async def get_keyword_by_word_ddd(
        self, word: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить ключевое слово по слову (мигрировано из KeywordService)

        Args:
            word: Слово для поиска

        Returns:
            Информация о ключевом слове или None
        """
        # Получаем все ключевые слова и ищем по слову
        all_keywords = await self.keyword_repository.find_all()
        keyword = next(
            (
                k
                for k in all_keywords
                if k.content.word.lower() == word.lower()
            ),
            None,
        )

        if not keyword:
            return None

        return await self.get_keyword_by_id(keyword.id)

    async def update_keyword_ddd(
        self, keyword_id: int, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Обновить ключевое слово (мигрировано из KeywordService)

        Args:
            keyword_id: ID ключевого слова
            update_data: Данные для обновления

        Returns:
            Обновленное ключевое слово или None
        """
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return None

        # Проверяем дубликат при изменении слова
        if (
            "word" in update_data
            and update_data["word"].lower() != keyword.content.word.lower()
        ):
            existing = await self.get_keyword_by_word(update_data["word"])
            if existing:
                raise ValueError(
                    f"Ключевое слово '{update_data['word']}' уже существует"
                )

        # Обновляем поля
        for field, value in update_data.items():
            if field == "word":
                keyword.content.word = value
            elif field == "category":
                keyword.content.category = value
            elif field == "description":
                keyword.content.description = value
            elif hasattr(keyword, field):
                setattr(keyword, field, value)

        # Валидируем бизнес-правила после обновления
        keyword.validate_business_rules()

        # Сохраняем изменения
        await self.keyword_repository.save(keyword)

        return await self.get_keyword_by_id(keyword.id)

    async def delete_keyword_ddd(self, keyword_id: int) -> Dict[str, Any]:
        """
        Удалить ключевое слово (мигрировано из KeywordService)

        Args:
            keyword_id: ID ключевого слова

        Returns:
            Результат операции
        """
        keyword = await self.keyword_repository.find_by_id(keyword_id)
        if not keyword:
            return {"deleted": False, "reason": "Keyword not found"}

        keyword_word = keyword.content.word

        # Удаляем через репозиторий
        await self.keyword_repository.delete(keyword_id)

        return {
            "deleted": True,
            "keyword_id": keyword_id,
            "keyword_word": keyword_word,
            "message": f"Keyword '{keyword_word}' deleted successfully",
        }

    async def create_keywords_bulk_ddd(
        self, keywords_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Массовое создание ключевых слов (мигрировано из KeywordService)

        Args:
            keywords_data: Список данных ключевых слов

        Returns:
            Результат массовой операции
        """
        created_keywords = []
        skipped_count = 0
        errors = []

        for keyword_data in keywords_data:
            try:
                # Проверяем существование
                existing = await self.get_keyword_by_word(
                    keyword_data.get("word", "")
                )
                if existing:
                    skipped_count += 1
                    continue

                # Создаем ключевое слово
                created_keyword = await self.create_keyword(keyword_data)
                created_keywords.append(created_keyword)

            except Exception as e:
                errors.append(
                    f"Error creating '{keyword_data.get('word', '')}': {str(e)}"
                )

        return {
            "status": "success",
            "message": f"Created {len(created_keywords)} keywords from {len(keywords_data)} items",
            "total_processed": len(keywords_data),
            "created": len(created_keywords),
            "skipped": skipped_count,
            "errors": errors,
            "created_keywords": created_keywords,
        }

    async def search_keywords_ddd(
        self,
        query: str,
        category: Optional[str] = None,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Поиск ключевых слов по различным критериям (мигрировано из KeywordService)

        Args:
            query: Поисковый запрос
            category: Фильтр по категории
            active_only: Только активные ключевые слова
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Результаты поиска с пагинацией
        """
        return await self.get_keywords_paginated(
            active_only=active_only,
            category=category,
            search=query,
            limit=limit,
            offset=offset,
        )

    async def get_keywords_by_category_paginated(
        self, category: str, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить ключевые слова по категории с пагинацией (мигрировано из KeywordService)

        Args:
            category: Название категории
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Пагинированный результат
        """
        return await self.get_keywords_paginated(
            active_only=True, category=category, limit=limit, offset=offset
        )

    async def duplicate_keywords_check_ddd(
        self, words: List[str]
    ) -> Dict[str, bool]:
        """
        Проверить наличие дубликатов среди списка слов (мигрировано из KeywordService)

        Args:
            words: Список слов для проверки

        Returns:
            Словарь {слово: существует_ли_уже}
        """
        results = {}

        for word in words:
            existing = await self.get_keyword_by_word(word)
            results[word] = existing is not None

        return results

    async def bulk_update_status_ddd(
        self, keyword_ids: List[int], is_active: bool
    ) -> Dict[str, Any]:
        """
        Массовое обновление статуса ключевых слов (мигрировано из KeywordService)

        Args:
            keyword_ids: Список ID ключевых слов
            is_active: Новый статус активности

        Returns:
            Результат массовой операции
        """
        updated_count = 0
        errors = []

        for keyword_id in keyword_ids:
            try:
                keyword = await self.keyword_repository.find_by_id(keyword_id)
                if keyword:
                    keyword.is_active = is_active
                    await self.keyword_repository.save(keyword)
                    updated_count += 1
                else:
                    errors.append(f"Keyword {keyword_id} not found")
            except Exception as e:
                errors.append(f"Error updating keyword {keyword_id}: {str(e)}")

        return {
            "status": "success" if len(errors) == 0 else "partial",
            "message": f"Updated {updated_count} keywords, {len(errors)} errors",
            "updated_count": updated_count,
            "total_requested": len(keyword_ids),
            "errors": errors,
        }

    async def get_categories_ddd(self) -> List[str]:
        """
        Получить список категорий ключевых слов (мигрировано из KeywordService)

        Returns:
            Список уникальных категорий
        """
        all_keywords = await self.keyword_repository.find_all()

        # Собираем уникальные категории
        categories = set()
        for keyword in all_keywords:
            if keyword.content.category:
                categories.add(keyword.content.category)

        return sorted(list(categories))

    async def get_keyword_statistics_ddd(self) -> Dict[str, Any]:
        """
        Получить статистику по ключевым словам (мигрировано из KeywordService)

        Returns:
            Детальная статистика
        """
        all_keywords = await self.keyword_repository.find_all()

        total_keywords = len(all_keywords)
        active_keywords = len([k for k in all_keywords if k.is_active])

        # Статистика по категориям
        categories_stats = {}
        for keyword in all_keywords:
            category = keyword.content.category or "Без категории"
            categories_stats[category] = categories_stats.get(category, 0) + 1

        # Длина слов
        word_lengths = [len(k.content.word) for k in all_keywords]
        avg_word_length = (
            sum(word_lengths) / len(word_lengths) if word_lengths else 0
        )

        return {
            "total_keywords": total_keywords,
            "active_keywords": active_keywords,
            "inactive_keywords": total_keywords - active_keywords,
            "categories_count": len(categories_stats),
            "categories_stats": categories_stats,
            "average_word_length": round(avg_word_length, 2),
            "activity_rate": (
                (active_keywords / total_keywords * 100)
                if total_keywords > 0
                else 0
            ),
        }

    # =============== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ KeywordService ===============

    async def upload_keywords_from_file_ddd(
        self,
        file_content: str,
        file_extension: str,
        default_category: Optional[str] = None,
        is_active: bool = True,
        is_case_sensitive: bool = False,
        is_whole_word: bool = False,
    ) -> Dict[str, Any]:
        """
        Загрузка ключевых слов из файла CSV/TXT (мигрировано из KeywordService)

        Args:
            file_content: Содержимое файла
            file_extension: Расширение файла (.csv, .txt)
            default_category: Категория по умолчанию
            is_active: Статус активности
            is_case_sensitive: Чувствительность к регистру
            is_whole_word: Поиск целого слова

        Returns:
            Результат загрузки
        """
        import csv
        import io

        keywords_data = []
        errors = []
        total_processed = 0

        try:
            if file_extension == ".csv":
                # Обработка CSV файла
                csv_reader = csv.reader(io.StringIO(file_content))
                for row_num, row in enumerate(csv_reader, 1):
                    total_processed += 1

                    if not row or not row[0].strip():
                        continue  # Пропускаем пустые строки

                    try:
                        word = row[0].strip()
                        category = (
                            row[1].strip()
                            if len(row) > 1 and row[1].strip()
                            else default_category
                        )
                        description = (
                            row[2].strip()
                            if len(row) > 2 and row[2].strip()
                            else None
                        )

                        if not word:
                            errors.append(f"Строка {row_num}: пустое ключевое слово")
                            continue

                        keywords_data.append({
                            "word": word,
                            "category": category,
                            "description": description,
                            "is_active": is_active,
                            "is_case_sensitive": is_case_sensitive,
                            "is_whole_word": is_whole_word,
                        })

                    except Exception as e:
                        errors.append(f"Строка {row_num}: {str(e)}")

            elif file_extension == ".txt":
                # Обработка TXT файла
                lines = file_content.strip().split('\n')
                for line_num, line in enumerate(lines, 1):
                    total_processed += 1
                    word = line.strip()

                    if not word:
                        continue

                    keywords_data.append({
                        "word": word,
                        "category": default_category,
                        "description": None,
                        "is_active": is_active,
                        "is_case_sensitive": is_case_sensitive,
                        "is_whole_word": is_whole_word,
                    })

            else:
                return {
                    "status": "error",
                    "message": f"Неподдерживаемый формат файла: {file_extension}"
                }

            # Создаем ключевые слова массово
            result = await self.create_keywords_bulk(keywords_data)

            return {
                "status": "success",
                "message": f"Загружено {result['created']} ключевых слов из {total_processed} строк",
                "total_processed": total_processed,
                "created": result["created"],
                "skipped": result["skipped"],
                "errors": errors + result["errors"],
                "created_keywords": result["created_keywords"]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка обработки файла: {str(e)}",
                "total_processed": total_processed,
                "created": 0,
                "skipped": 0,
                "errors": [str(e)]
            }

    async def get_average_word_length_ddd(self) -> float:
        """
        Получить среднюю длину ключевых слов (мигрировано из KeywordService)

        Returns:
            Средняя длина слова
        """
        all_keywords = await self.keyword_repository.find_all()

        if not all_keywords:
            return 0.0

        word_lengths = [len(k.content.word) for k in all_keywords]
        return round(sum(word_lengths) / len(word_lengths), 2)

    async def search_keywords_paginated_ddd(
        self,
        query: str,
        category: Optional[str] = None,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Поиск ключевых слов с пагинацией (мигрировано из KeywordService)

        Args:
            query: Поисковый запрос
            category: Фильтр по категории
            active_only: Только активные ключевые слова
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Результаты поиска с пагинацией
        """
        return await self.get_keywords_paginated(
            active_only=active_only,
            category=category,
            search=query,
            limit=limit,
            offset=offset
        )

    async def get_keywords_by_category_paginated_ddd(
        self,
        category: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Получить ключевые слова по категории с пагинацией (мигрировано из KeywordService)

        Args:
            category: Название категории
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Пагинированный результат
        """
        return await self.get_keywords_paginated(
            active_only=True,
            category=category,
            limit=limit,
            offset=offset
        )

    async def get_keyword_statistics_detailed_ddd(self) -> Dict[str, Any]:
        """
        Детальная статистика по ключевым словам (мигрировано из KeywordService)

        Returns:
            Расширенная статистика
        """
        all_keywords = await self.keyword_repository.find_all()

        total_keywords = len(all_keywords)
        active_keywords = len([k for k in all_keywords if k.is_active])

        # Статистика по категориям
        categories_stats = {}
        for keyword in all_keywords:
            category = keyword.content.category or "Без категории"
            categories_stats[category] = categories_stats.get(category, 0) + 1

        # Статистика по длине слов
        word_lengths = [len(k.content.word) for k in all_keywords]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0

        # Самые длинные слова
        longest_keywords = sorted(
            [(k.content.word, len(k.content.word)) for k in all_keywords],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        # Статистика по чувствительности к регистру
        case_sensitive_count = len([k for k in all_keywords if k.is_case_sensitive])
        whole_word_count = len([k for k in all_keywords if k.is_whole_word])

        return {
            "total_keywords": total_keywords,
            "active_keywords": active_keywords,
            "inactive_keywords": total_keywords - active_keywords,
            "categories_count": len(categories_stats),
            "categories_stats": categories_stats,
            "average_word_length": round(avg_word_length, 2),
            "longest_keywords": dict(longest_keywords),
            "case_sensitive_keywords": case_sensitive_count,
            "whole_word_keywords": whole_word_count,
            "case_sensitive_rate": (case_sensitive_count / total_keywords * 100) if total_keywords > 0 else 0,
            "whole_word_rate": (whole_word_count / total_keywords * 100) if total_keywords > 0 else 0,
            "activity_rate": (active_keywords / total_keywords * 100) if total_keywords > 0 else 0,
        }

    async def validate_keyword_data_ddd(
        self, keyword_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Валидация данных ключевого слова (мигрировано из KeywordService)

        Args:
            keyword_data: Данные для валидации

        Returns:
            Результат валидации
        """
        errors = []
        warnings = []

        # Проверяем обязательные поля
        if not keyword_data.get("word", "").strip():
            errors.append("Ключевое слово не может быть пустым")

        # Проверяем длину слова
        word = keyword_data.get("word", "")
        if len(word) > 100:
            errors.append("Ключевое слово слишком длинное (макс. 100 символов)")
        elif len(word) < 2:
            errors.append("Ключевое слово слишком короткое (мин. 2 символа)")

        # Проверяем на специальные символы
        if any(char in word for char in ['<', '>', '&', '"', "'"]):
            warnings.append("Ключевое слово содержит специальные символы")

        # Проверяем категорию
        category = keyword_data.get("category")
        if category and len(category) > 50:
            errors.append("Название категории слишком длинное (макс. 50 символов)")

        # Проверяем описание
        description = keyword_data.get("description")
        if description and len(description) > 500:
            errors.append("Описание слишком длинное (макс. 500 символов)")

        # Проверяем дубликат
        if word:
            existing = await self.get_keyword_by_word(word)
            if existing:
                errors.append("Ключевое слово с таким названием уже существует")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }

    async def export_keywords_ddd(
        self,
        category: Optional[str] = None,
        active_only: bool = True,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Экспорт ключевых слов (мигрировано из KeywordService)

        Args:
            category: Фильтр по категории
            active_only: Только активные ключевые слова
            format: Формат экспорта

        Returns:
            Данные для экспорта
        """
        from datetime import datetime

        # Получаем ключевые слова с фильтрами
        result = await self.get_keywords_paginated(
            active_only=active_only,
            category=category,
            limit=10000,  # Получаем все для экспорта
            offset=0
        )

        keywords = result["keywords"]

        # Форматируем для экспорта
        export_data = []
        for keyword in keywords:
            export_data.append({
                "id": keyword["id"],
                "word": keyword["word"],
                "category": keyword["category"],
                "description": keyword["description"],
                "is_active": keyword["is_active"],
                "is_case_sensitive": keyword["is_case_sensitive"],
                "is_whole_word": keyword["is_whole_word"],
                "created_at": keyword["created_at"],
                "updated_at": keyword["updated_at"],
            })

        return {
            "data": export_data,
            "total": len(export_data),
            "format": format,
            "exported_at": datetime.utcnow().isoformat(),
            "filters": {
                "category": category,
                "active_only": active_only
            }
        }

    async def get_keywords_count_ddd(
        self,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> int:
        """
        Получить количество ключевых слов с фильтрами (мигрировано из KeywordService)

        Args:
            category: Фильтр по категории
            active_only: Только активные ключевые слова

        Returns:
            Количество ключевых слов
        """
        result = await self.get_keywords_paginated(
            active_only=active_only,
            category=category,
            limit=1,
            offset=0
        )

        return result["total"]
