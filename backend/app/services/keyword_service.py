from typing import List, Optional
import csv
import io
from pathlib import Path

from fastapi import HTTPException, status, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.keyword import Keyword
from app.schemas.base import (
    PaginatedResponse,
    PaginationParams,
    StatusResponse,
)
from app.schemas.keyword import KeywordCreate, KeywordResponse, KeywordUpdate, KeywordUploadResponse


class KeywordService:
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
        if file_extension not in ['.csv', '.txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поддерживаются только файлы CSV и TXT",
            )
        
        try:
            content = await file.read()
            content_str = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в кодировке UTF-8",
            )
        
        keywords_data = []
        errors = []
        total_processed = 0
        
        if file_extension == '.csv':
            # Обработка CSV файла
            try:
                csv_reader = csv.reader(io.StringIO(content_str))
                for row_num, row in enumerate(csv_reader, 1):
                    total_processed += 1
                    
                    if not row or not row[0].strip():
                        continue  # Пропускаем пустые строки
                    
                    try:
                        word = row[0].strip()
                        category = row[1].strip() if len(row) > 1 and row[1].strip() else default_category
                        description = row[2].strip() if len(row) > 2 and row[2].strip() else None
                        
                        if not word:
                            errors.append(f"Строка {row_num}: пустое ключевое слово")
                            continue
                        
                        keywords_data.append(KeywordCreate(
                            word=word,
                            category=category,
                            description=description,
                            is_active=is_active,
                            is_case_sensitive=is_case_sensitive,
                            is_whole_word=is_whole_word,
                        ))
                    except Exception as e:
                        errors.append(f"Строка {row_num}: {str(e)}")
                        
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ошибка чтения CSV файла: {str(e)}",
                )
        
        elif file_extension == '.txt':
            # Обработка TXT файла (одно слово на строку)
            lines = content_str.split('\n')
            for line_num, line in enumerate(lines, 1):
                total_processed += 1
                
                word = line.strip()
                if not word or word.startswith('#'):  # Пропускаем пустые строки и комментарии
                    continue
                
                keywords_data.append(KeywordCreate(
                    word=word,
                    category=default_category,
                    description=None,
                    is_active=is_active,
                    is_case_sensitive=is_case_sensitive,
                    is_whole_word=is_whole_word,
                ))
        
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
                
                new_keyword = Keyword(**keyword_data.model_dump())
                db.add(new_keyword)
                created_keywords.append(new_keyword)
                
            except Exception as e:
                errors.append(f"Ошибка создания '{keyword_data.word}': {str(e)}")
        
        if created_keywords:
            await db.commit()
            for keyword in created_keywords:
                await db.refresh(keyword)
        
        return KeywordUploadResponse(
            status="success",
            message=f"Загружено {len(created_keywords)} ключевых слов из {total_processed} строк",
            total_processed=total_processed,
            created=len(created_keywords),
            skipped=skipped_count,
            errors=errors,
            created_keywords=[KeywordResponse.model_validate(kw) for kw in created_keywords],
        )


keyword_service = KeywordService()
