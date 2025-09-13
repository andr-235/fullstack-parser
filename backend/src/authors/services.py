"""
Сервис для работы с авторами - упрощенная версия
"""

import asyncio
import json
import logging
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AuthorModel
from .schemas import (
    AuthorCreate, AuthorUpdate, AuthorResponse, AuthorWithCommentsResponse,
    AuthorListResponse, AuthorFilter, AuthorSearch, AuthorBulkAction,
    AuthorStatus
)

logger = logging.getLogger(__name__)


class AuthorService:
    """Сервис для работы с авторами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_author(self, data: AuthorCreate) -> AuthorResponse:
        """Создает автора"""
        try:
            # Проверяем, не существует ли уже автор с таким VK ID
            existing = await self.get_by_vk_id(data.vk_id)
            if existing:
                raise ValueError(f"Author with VK ID {data.vk_id} already exists")
            
            # Создаем автора
            author_data = data.model_dump()
            if author_data.get('metadata'):
                author_data['metadata'] = json.dumps(author_data['metadata'])
                
            author = AuthorModel(**author_data)
            self.db.add(author)
            await self.db.commit()
            await self.db.refresh(author)
            
            logger.info(f"Created author: ID={author.id}, VK ID={author.vk_id}")
            return AuthorResponse.model_validate(author)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create author: {e}")
            raise
    
    async def get_by_id(self, author_id: int) -> Optional[AuthorResponse]:
        """Получает автора по ID"""
        result = await self.db.execute(
            select(AuthorModel).where(AuthorModel.id == author_id)
        )
        author = result.scalar_one_or_none()
        return AuthorResponse.model_validate(author) if author else None
    
    async def get_by_vk_id(self, vk_id: int) -> Optional[AuthorResponse]:
        """Получает автора по VK ID"""
        result = await self.db.execute(
            select(AuthorModel).where(AuthorModel.vk_id == vk_id)
        )
        author = result.scalar_one_or_none()
        return AuthorResponse.model_validate(author) if author else None
    
    async def get_by_screen_name(self, screen_name: str) -> Optional[AuthorResponse]:
        """Получает автора по screen name"""
        result = await self.db.execute(
            select(AuthorModel).where(AuthorModel.screen_name == screen_name)
        )
        author = result.scalar_one_or_none()
        return AuthorResponse.model_validate(author) if author else None
    
    async def update_author(self, author_id: int, data: AuthorUpdate) -> Optional[AuthorResponse]:
        """Обновляет автора"""
        # Получаем автора
        author = await self.get_by_id(author_id)
        if not author:
            return None
        
        # Подготавливаем данные для обновления
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get('metadata'):
            update_data['metadata'] = json.dumps(update_data['metadata'])
        
        # Обновляем
        await self.db.execute(
            update(AuthorModel)
            .where(AuthorModel.id == author_id)
            .values(**update_data, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        
        # Возвращаем обновленного автора
        return await self.get_by_id(author_id)
    
    async def delete_author(self, author_id: int) -> bool:
        """Удаляет автора"""
        result = await self.db.execute(
            delete(AuthorModel).where(AuthorModel.id == author_id)
        )
        await self.db.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted author: ID={author_id}")
        return deleted
    
    async def list_authors(self, filter_data: AuthorFilter) -> AuthorListResponse:
        """Получает список авторов"""
        # Базовые условия
        conditions = []
        if filter_data.status:
            conditions.append(AuthorModel.status == filter_data.status)
        if filter_data.is_verified is not None:
            conditions.append(AuthorModel.is_verified == filter_data.is_verified)
        if filter_data.is_closed is not None:
            conditions.append(AuthorModel.is_closed == filter_data.is_closed)
        
        # Сортировка
        order_column = getattr(AuthorModel, filter_data.order_by, AuthorModel.created_at)
        if filter_data.order_direction == "desc":
            order_clause = order_column.desc()
        else:
            order_clause = order_column.asc()
        
        # Оптимизированный запрос с подсчетом
        query = select(AuthorModel).where(*conditions).order_by(order_clause)
        count_query = select(func.count(AuthorModel.id)).where(*conditions)
        
        # Выполняем оба запроса параллельно
        result, total_result = await asyncio.gather(
            self.db.execute(query.offset(filter_data.offset).limit(filter_data.limit)),
            self.db.execute(count_query)
        )
        
        authors = result.scalars().all()
        total = total_result.scalar()
        
        return AuthorListResponse(
            items=[AuthorResponse.model_validate(author) for author in authors],
            total=total,
            limit=filter_data.limit,
            offset=filter_data.offset
        )
    
    async def search_authors(self, search_data: AuthorSearch) -> AuthorListResponse:
        """Поиск авторов"""
        query = select(AuthorModel).where(
            or_(
                AuthorModel.first_name.ilike(f"%{search_data.query}%"),
                AuthorModel.last_name.ilike(f"%{search_data.query}%"),
                AuthorModel.screen_name.ilike(f"%{search_data.query}%")
            )
        )
        
        # Подсчет общего количества
        count_query = select(func.count(AuthorModel.id)).where(
            or_(
                AuthorModel.first_name.ilike(f"%{search_data.query}%"),
                AuthorModel.last_name.ilike(f"%{search_data.query}%"),
                AuthorModel.screen_name.ilike(f"%{search_data.query}%")
            )
        )
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Пагинация
        query = query.offset(search_data.offset).limit(search_data.limit)
        
        # Выполняем запрос
        result = await self.db.execute(query)
        authors = result.scalars().all()
        
        return AuthorListResponse(
            items=[AuthorResponse.model_validate(author) for author in authors],
            total=total,
            limit=search_data.limit,
            offset=search_data.offset
        )
    
    async def bulk_action(self, action_data: AuthorBulkAction) -> dict:
        """Выполняет массовое действие"""
        author_ids = action_data.author_ids
        
        if action_data.action == "activate":
            await self.db.execute(
                update(AuthorModel)
                .where(AuthorModel.id.in_(author_ids))
                .values(status=AuthorStatus.ACTIVE, updated_at=datetime.utcnow())
            )
        elif action_data.action == "suspend":
            await self.db.execute(
                update(AuthorModel)
                .where(AuthorModel.id.in_(author_ids))
                .values(status=AuthorStatus.SUSPENDED, updated_at=datetime.utcnow())
            )
        elif action_data.action == "delete":
            await self.db.execute(
                delete(AuthorModel).where(AuthorModel.id.in_(author_ids))
            )
        else:
            raise ValueError(f"Unknown action: {action_data.action}")
        
        await self.db.commit()
        
        logger.info(f"Bulk action '{action_data.action}' applied to {len(author_ids)} authors")
        return {"action": action_data.action, "affected_count": len(author_ids)}
    
    async def get_stats(self) -> dict:
        """Получает статистику авторов"""
        # Общее количество
        total_result = await self.db.execute(select(func.count(AuthorModel.id)))
        total = total_result.scalar()
        
        # По статусам
        status_result = await self.db.execute(
            select(AuthorModel.status, func.count(AuthorModel.id))
            .group_by(AuthorModel.status)
        )
        status_stats = {status: count for status, count in status_result.fetchall()}
        
        # Верифицированные
        verified_result = await self.db.execute(
            select(func.count(AuthorModel.id)).where(AuthorModel.is_verified == True)
        )
        verified_count = verified_result.scalar()
        
        # Закрытые профили
        closed_result = await self.db.execute(
            select(func.count(AuthorModel.id)).where(AuthorModel.is_closed == True)
        )
        closed_count = closed_result.scalar()
        
        return {
            "total": total,
            "by_status": status_stats,
            "verified": verified_count,
            "closed": closed_count
        }
    
    async def get_author_with_comments(
        self, 
        author_id: int, 
        comments_limit: int = 20, 
        comments_offset: int = 0
    ) -> Optional[AuthorWithCommentsResponse]:
        """Получить автора с его комментариями"""
        # Получаем автора
        author = await self.get_by_id(author_id)
        if not author:
            return None
        
        # Получаем комментарии автора
        from comments.service import CommentService
        from comments.repository import CommentRepository
        from comments.schemas import CommentFilter
        
        comment_repo = CommentRepository(self.db)
        comment_service = CommentService(comment_repo)
        
        comments_response = await comment_service.get_comments_by_author(
            author_id=author_id,
            limit=comments_limit,
            offset=comments_offset,
            include_author=False  # Не нужно дублировать автора
        )
        
        # Преобразуем комментарии в словари
        comments_data = []
        for comment in comments_response.items:
            comments_data.append({
                "id": comment.id,
                "vk_id": comment.vk_id,
                "group_id": comment.group_id,
                "post_id": comment.post_id,
                "text": comment.text,
                "created_at": comment.created_at,
                "is_deleted": comment.is_deleted,
                "keyword_matches": comment.keyword_matches
            })
        
        # Создаем ответ с комментариями
        author_data = author.model_dump()
        author_data["comments"] = comments_data
        
        return AuthorWithCommentsResponse(**author_data)
