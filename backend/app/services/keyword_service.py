import csv
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import Keyword
from app.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
)
from app.schemas.keyword import (
    KeywordCreate,
    KeywordResponse,
    KeywordUpdate,
    KeywordUploadResponse,
)


class KeywordService:
    """Сервис для управления ключевыми словами"""

    def __init__(self):
        """Инициализация сервиса ключевых слов"""
        self.logger = logging.getLogger(__name__)

    async def create_keyword(
        self, db: AsyncSession, keyword_data: KeywordCreate
    ) -> Keyword:
        existing = await db.execute(
            select(Keyword).where(
                func.lower(Keyword.word) == keyword_data.word.lower()
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ключевое слово уже существует",
            )
        new_keyword = Keyword(**keyword_data.model_dump())
        db.add(new_keyword)
        await db.commit()
        await db.refresh(new_keyword)
        return new_keyword

    async def get_keywords(
        self,
        db: AsyncSession,
        pagination: PaginationParams,
        active_only: bool = True,
        category: Optional[str] = None,
        q: Optional[str] = None,
    ) -> PaginatedResponse:
        query = select(Keyword)
        if active_only:
            query = query.where(Keyword.is_active)
        if category:
            query = query.where(Keyword.category == category)
        if q:
            search_pattern = f"%{q.lower()}%"
            query = query.where(
                func.lower(Keyword.word).like(search_pattern)
                | func.lower(Keyword.category).like(search_pattern)
            )
        count_query = select(func.count()).select_from(query.subquery())
        total = await db.scalar(count_query)
        paginated_query = query.offset(pagination.skip).limit(pagination.size)
        result = await db.execute(paginated_query)
        keywords = result.scalars().all()
        return PaginatedResponse(
            total=total or 0,
            page=pagination.page,
            size=pagination.size,
            items=[
                KeywordResponse.model_validate(keyword) for keyword in keywords
            ],
        )

    async def get_keyword(self, db: AsyncSession, keyword_id: int) -> Keyword:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        return keyword

    async def update_keyword(
        self, db: AsyncSession, keyword_id: int, keyword_update: KeywordUpdate
    ) -> Keyword:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        if (
            keyword_update.word
            and keyword_update.word.lower() != keyword.word.lower()
        ):
            existing = await db.execute(
                select(Keyword).where(
                    func.lower(Keyword.word) == keyword_update.word.lower()
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ключевое слово с таким названием уже существует",
                )
        update_data = keyword_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(keyword, field, value)
        await db.commit()
        await db.refresh(keyword)
        return keyword

    async def delete_keyword(
        self, db: AsyncSession, keyword_id: int
    ) -> StatusResponse:
        result = await db.execute(
            select(Keyword).where(Keyword.id == keyword_id)
        )
        keyword = result.scalar_one_or_none()
        if not keyword:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ключевое слово не найдено",
            )
        await db.delete(keyword)
        await db.commit()
        return StatusResponse(
            status="success",
            message=f"Ключевое слово '{keyword.word}' удалено",
        )

    async def create_keywords_bulk(
        self, db: AsyncSession, keywords_data: List[KeywordCreate]
    ) -> List[Keyword]:
        created_keywords = []
        for keyword_data in keywords_data:
            existing = await db.execute(
                select(Keyword).where(
                    func.lower(Keyword.word) == keyword_data.word.lower()
                )
            )
            if not existing.scalar_one_or_none():
                new_keyword = Keyword(**keyword_data.model_dump())
                db.add(new_keyword)
                created_keywords.append(new_keyword)
        await db.commit()
        for keyword in created_keywords:
            await db.refresh(keyword)
        return created_keywords

    async def get_categories(self, db: AsyncSession) -> List[str]:
        result = await db.execute(
            select(Keyword.category)
            .distinct()
            .where(Keyword.category.isnot(None))
        )
        categories = [cat for cat in result.scalars().all() if cat]
        return sorted(categories)

    async def upload_keywords_from_file(
        self,
        db: AsyncSession,
        file: UploadFile,
        default_category: Optional[str] = None,
        is_active: bool = True,
        is_case_sensitive: bool = False,
        is_whole_word: bool = False,
    ) -> KeywordUploadResponse:
        """
        Загружает ключевые слова из файла (CSV или TXT)

        Поддерживаемые форматы:
        - CSV: word,category,description
        - TXT: одно слово на строку
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не выбран",
            )

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in [".csv", ".txt"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только файлы CSV и TXT",
            )

        try:
            content = await file.read()
            content_str = content.decode("utf-8")
        except UnicodeDecodeError as err:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в кодировке UTF-8",
            ) from err

        keywords_data = []
        errors = []
        total_processed = 0

        if file_extension == ".csv":
            # Обработка CSV файла
            try:
                csv_reader = csv.reader(io.StringIO(content_str))
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
                            errors.append(
                                f"Строка {row_num}: пустое ключевое слово"
                            )
                            continue

                        keywords_data.append(
                            KeywordCreate(
                                word=word,
                                category=category,
                                description=description,
                                is_active=is_active,
                                is_case_sensitive=is_case_sensitive,
                                is_whole_word=is_whole_word,
                            )
                        )
                    except Exception as e:
                        errors.append(f"Строка {row_num}: {str(e)}")

            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка чтения CSV файла: {str(e)}",
                ) from e

        elif file_extension == ".txt":
            # Обработка TXT файла (одно слово на строку)
            lines = content_str.split("\n")
            for _line_num, line in enumerate(lines, 1):
                total_processed += 1

                word = line.strip()
                if not word or word.startswith(
                    "#"
                ):  # Пропускаем пустые строки и комментарии
                    continue

                keywords_data.append(
                    KeywordCreate(
                        word=word,
                        category=default_category,
                        description=None,
                        is_active=is_active,
                        is_case_sensitive=is_case_sensitive,
                        is_whole_word=is_whole_word,
                    )
                )

        if not keywords_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл не содержит валидных ключевых слов",
            )

        # Создаем ключевые слова
        created_keywords = []
        skipped_count = 0

        for keyword_data in keywords_data:
            try:
                # Проверяем существование
                existing = await db.execute(
                    select(Keyword).where(
                        func.lower(Keyword.word) == keyword_data.word.lower()
                    )
                )
                if existing.scalar_one_or_none():
                    skipped_count += 1
                    continue

                # Создаем и сразу сохраняем ключевое слово
                new_keyword = Keyword(**keyword_data.model_dump())
                db.add(new_keyword)
                await db.commit()
                await db.refresh(new_keyword)
                created_keywords.append(new_keyword)

            except Exception as e:
                await db.rollback()
                errors.append(
                    f"Ошибка создания '{keyword_data.word}': {str(e)}"
                )

        return KeywordUploadResponse(
            status="success",
            message=f"Загружено {len(created_keywords)} ключевых слов из {total_processed} строк",
            total_processed=total_processed,
            created=len(created_keywords),
            skipped=skipped_count,
            errors=errors,
            created_keywords=[
                KeywordResponse.model_validate(kw) for kw in created_keywords
            ],
        )

    # Новые методы для улучшения функциональности

    async def get_keyword_statistics(self, db: AsyncSession) -> Dict:
        """
        Получить статистику по ключевым словам.

        Args:
            db: Сессия базы данных

        Returns:
            Статистика по ключевым словам
        """
        try:
            # Общая статистика
            total_result = await db.execute(select(func.count()).select_from(Keyword))
            total = total_result.scalar()

            # Активные ключевые слова
            active_result = await db.execute(
                select(func.count()).select_from(Keyword).where(Keyword.is_active == True)
            )
            active = active_result.scalar()

            # Статистика по категориям
            category_result = await db.execute(
                select(Keyword.category, func.count(Keyword.id))
                .where(Keyword.category.isnot(None))
                .group_by(Keyword.category)
            )
            categories_stats = dict(category_result.all())

            # Самые популярные ключевые слова (по длине слова)
            popular_result = await db.execute(
                select(Keyword.word, func.length(Keyword.word))
                .order_by(func.length(Keyword.word).desc())
                .limit(5)
            )
            longest_keywords = dict(popular_result.all())

            stats = {
                "total_keywords": total,
                "active_keywords": active,
                "inactive_keywords": total - active,
                "categories_count": len(categories_stats),
                "categories_stats": categories_stats,
                "longest_keywords": longest_keywords,
                "average_word_length": await self._get_average_word_length(db)
            }

            self.logger.info(f"Generated keyword statistics: {total} total keywords")
            return stats

        except Exception as e:
            self.logger.error(f"Error getting keyword statistics: {e}")
            return {}

    async def bulk_update_status(
        self,
        db: AsyncSession,
        keyword_ids: List[int],
        is_active: bool
    ) -> StatusResponse:
        """
        Массовое обновление статуса ключевых слов.

        Args:
            db: Сессия базы данных
            keyword_ids: Список ID ключевых слов
            is_active: Новый статус активности

        Returns:
            Результат операции
        """
        try:
            if not keyword_ids:
                return StatusResponse(
                    success=False,
                    message="Не указаны ID ключевых слов для обновления"
                )

            # Обновляем статус
            result = await db.execute(
                select(Keyword).where(Keyword.id.in_(keyword_ids))
            )
            keywords = result.scalars().all()

            updated_count = 0
            for keyword in keywords:
                keyword.is_active = is_active
                updated_count += 1

            await db.commit()

            message = f"Обновлено {updated_count} ключевых слов, статус: {'активно' if is_active else 'неактивно'}"
            self.logger.info(message)

            return StatusResponse(
                success=True,
                message=message
            )

        except Exception as e:
            await db.rollback()
            error_msg = f"Ошибка при массовом обновлении статуса: {str(e)}"
            self.logger.error(error_msg)
            return StatusResponse(
                success=False,
                message=error_msg
            )

    async def search_keywords(
        self,
        db: AsyncSession,
        query: str,
        category: Optional[str] = None,
        active_only: bool = True,
        limit: int = 20,
        offset: int = 0
    ) -> PaginatedResponse[KeywordResponse]:
        """
        Поиск ключевых слов по различным критериям.

        Args:
            db: Сессия базы данных
            query: Поисковый запрос
            category: Фильтр по категории
            active_only: Только активные ключевые слова
            limit: Максимальное количество результатов
            offset: Смещение для пагинации

        Returns:
            Пагинированный ответ с результатами поиска
        """
        try:
            # Строим запрос
            sql_query = select(Keyword)

            # Добавляем условия поиска
            conditions = []
            if query:
                search_pattern = f"%{query}%"
                conditions.append(
                    or_(
                        Keyword.word.ilike(search_pattern),
                        Keyword.description.ilike(search_pattern)
                    )
                )

            if category:
                conditions.append(Keyword.category == category)

            if active_only:
                conditions.append(Keyword.is_active == True)

            if conditions:
                sql_query = sql_query.where(and_(*conditions))

            # Получаем общее количество
            count_query = sql_query.with_only_columns(func.count())
            total_result = await db.execute(count_query)
            total = total_result.scalar()

            # Получаем результаты с пагинацией
            sql_query = sql_query.order_by(Keyword.word).limit(limit).offset(offset)
            result = await db.execute(sql_query)
            keywords = result.scalars().all()

            # Преобразуем в response
            items = [KeywordResponse.model_validate(keyword) for keyword in keywords]

            self.logger.info(f"Search completed: {len(items)} results for query '{query}'")

            return PaginatedResponse(
                total=total,
                page=(offset // limit) + 1,
                size=limit,
                items=items
            )

        except Exception as e:
            self.logger.error(f"Error searching keywords: {e}")
            return PaginatedResponse(
                total=0,
                page=1,
                size=limit,
                items=[]
            )

    async def get_keywords_by_category(
        self,
        db: AsyncSession,
        category: str,
        pagination: PaginationParams
    ) -> PaginatedResponse[KeywordResponse]:
        """
        Получить ключевые слова по категории.

        Args:
            db: Сессия базы данных
            category: Название категории
            pagination: Параметры пагинации

        Returns:
            Пагинированный ответ с ключевыми словами категории
        """
        try:
            # Получаем общее количество
            count_query = select(func.count()).select_from(Keyword).where(
                and_(
                    Keyword.category == category,
                    Keyword.is_active == True
                )
            )
            count_result = await db.execute(count_query)
            total = count_result.scalar()

            # Получаем ключевые слова
            query = (
                select(Keyword)
                .where(
                    and_(
                        Keyword.category == category,
                        Keyword.is_active == True
                    )
                )
                .order_by(Keyword.word)
                .limit(pagination.size)
                .offset(pagination.skip)
            )

            result = await db.execute(query)
            keywords = result.scalars().all()

            # Преобразуем в response
            items = [KeywordResponse.model_validate(keyword) for keyword in keywords]

            self.logger.info(f"Retrieved {len(items)} keywords for category '{category}'")

            return PaginatedResponse(
                total=total,
                page=pagination.page,
                size=pagination.size,
                items=items
            )

        except Exception as e:
            self.logger.error(f"Error getting keywords by category '{category}': {e}")
            return PaginatedResponse(
                total=0,
                page=pagination.page,
                size=pagination.size,
                items=[]
            )

    async def duplicate_keywords_check(
        self,
        db: AsyncSession,
        words: List[str]
    ) -> Dict[str, bool]:
        """
        Проверить наличие дубликатов среди списка слов.

        Args:
            db: Сессия базы данных
            words: Список слов для проверки

        Returns:
            Словарь {слово: существует_ли_уже}
        """
        try:
            results = {}

            for word in words:
                result = await db.execute(
                    select(Keyword).where(
                        func.lower(Keyword.word) == word.lower()
                    )
                )
                exists = result.scalar_one_or_none() is not None
                results[word] = exists

            self.logger.info(f"Checked {len(words)} words for duplicates")
            return results

        except Exception as e:
            self.logger.error(f"Error checking for duplicates: {e}")
            return {word: False for word in words}

    async def _get_average_word_length(self, db: AsyncSession) -> float:
        """
        Получить среднюю длину ключевых слов.

        Args:
            db: Сессия базы данных

        Returns:
            Средняя длина слова
        """
        try:
            result = await db.execute(
                select(func.avg(func.length(Keyword.word)))
            )
            avg_length = result.scalar()
            return round(avg_length, 2) if avg_length else 0.0

        except Exception as e:
            self.logger.error(f"Error calculating average word length: {e}")
            return 0.0


keyword_service = KeywordService()
