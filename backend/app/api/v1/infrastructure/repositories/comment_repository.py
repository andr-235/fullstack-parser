"""
Репозиторий комментариев (DDD Infrastructure Layer)

Реализация Repository паттерна для работы с комментариями через SQLAlchemy.
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...domain.comment import Comment, CommentContent, CommentStatus
from ...domain.base import Entity
from .base import Repository, Specification, QueryOptions
from app.models.vk_comment import VKComment
from app.models.vk_post import VKPost
from app.models.keyword_match import KeywordMatch

logger = logging.getLogger(__name__)


class CommentRepository(Repository[Comment]):
    """
    Репозиторий для работы с комментариями

    Реализует интерфейс Repository для доменной сущности Comment,
    предоставляя доступ к данным через SQLAlchemy ORM.
    """

    def __init__(self, session_factory):
        """
        Инициализация репозитория

        Args:
            session_factory: Фабрика сессий SQLAlchemy
        """
        self.session_factory = session_factory

    async def _get_session(self) -> AsyncSession:
        """Получить сессию базы данных"""
        return self.session_factory()

    async def save(self, entity: Comment) -> Comment:
        """
        Сохранить комментарий

        Args:
            entity: Доменная сущность Comment

        Returns:
            Сохраненная сущность с обновленным ID
        """
        async with self._get_session() as session:
            try:
                # Преобразуем доменную сущность в модель базы данных
                db_comment = self._domain_to_db(entity)

                if entity.id and await self.exists(entity.id):
                    # Обновление существующего комментария
                    session.add(db_comment)
                else:
                    # Создание нового комментария
                    session.add(db_comment)

                await session.commit()
                await session.refresh(db_comment)

                # Возвращаем обновленную доменную сущность
                return self._db_to_domain(db_comment)

            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving comment: {e}")
                raise

    async def save_all(self, entities: List[Comment]) -> List[Comment]:
        """Сохранить несколько комментариев"""
        async with self._get_session() as session:
            try:
                db_comments = [
                    self._domain_to_db(entity) for entity in entities
                ]
                session.add_all(db_comments)
                await session.commit()

                # Обновляем ID для новых сущностей
                for db_comment in db_comments:
                    await session.refresh(db_comment)

                return [
                    self._db_to_domain(db_comment)
                    for db_comment in db_comments
                ]

            except Exception as e:
                await session.rollback()
                logger.error(f"Error saving comments: {e}")
                raise

    async def find_by_id(
        self, entity_id: Any, include_deleted: bool = False
    ) -> Optional[Comment]:
        """
        Найти комментарий по ID

        Args:
            entity_id: ID комментария
            include_deleted: Включать ли удаленные комментарии

        Returns:
            Доменная сущность Comment или None
        """
        async with self._get_session() as session:
            try:
                query = (
                    select(VKComment)
                    .options(
                        selectinload(VKComment.post).selectinload(
                            VKPost.group
                        ),
                        selectinload(VKComment.keyword_matches),
                    )
                    .where(VKComment.id == entity_id)
                )

                if not include_deleted:
                    query = query.where(VKComment.is_archived == False)

                result = await session.execute(query)
                db_comment = result.scalar_one_or_none()

                return self._db_to_domain(db_comment) if db_comment else None

            except Exception as e:
                logger.error(f"Error finding comment {entity_id}: {e}")
                raise

    async def find_all(
        self, options: Optional[QueryOptions] = None
    ) -> List[Comment]:
        """
        Найти все комментарии

        Args:
            options: Опции запроса (пагинация, фильтры, сортировка)

        Returns:
            Список доменных сущностей Comment
        """
        async with self._get_session() as session:
            try:
                query = select(VKComment).options(
                    selectinload(VKComment.post).selectinload(VKPost.group),
                    selectinload(VKComment.keyword_matches),
                )

                # Применяем фильтры
                if options and options.filters:
                    conditions = []
                    filters = options.filters

                    if "group_id" in filters:
                        query = query.join(
                            VKPost, VKComment.post_id == VKPost.id
                        )
                        conditions.append(
                            VKPost.group_id == filters["group_id"]
                        )

                    if "is_viewed" in filters:
                        conditions.append(
                            VKComment.is_viewed == filters["is_viewed"]
                        )

                    if "is_processed" in filters:
                        conditions.append(
                            VKComment.is_processed == filters["is_processed"]
                        )

                    if "is_archived" in filters:
                        conditions.append(
                            VKComment.is_archived == filters["is_archived"]
                        )
                    elif not (options and options.include_deleted):
                        conditions.append(VKComment.is_archived == False)

                    if conditions:
                        query = query.where(and_(*conditions))

                # Применяем сортировку
                if options and options.order_by:
                    order_column = getattr(VKComment, options.order_by, None)
                    if order_column is not None:
                        if options.order_direction == "desc":
                            query = query.order_by(desc(order_column))
                        else:
                            query = query.order_by(asc(order_column))
                else:
                    query = query.order_by(desc(VKComment.published_at))

                # Применяем пагинацию
                if options and options.limit:
                    query = query.limit(options.limit)
                    if options.offset:
                        query = query.offset(options.offset)

                result = await session.execute(query)
                db_comments = result.scalars().all()

                return [
                    self._db_to_domain(db_comment)
                    for db_comment in db_comments
                ]

            except Exception as e:
                logger.error(f"Error finding all comments: {e}")
                raise

    async def find_by_specification(
        self,
        specification: Specification,
        options: Optional[QueryOptions] = None,
    ) -> List[Comment]:
        """
        Найти комментарии по спецификации

        Args:
            specification: Спецификация для фильтрации
            options: Опции запроса

        Returns:
            Список доменных сущностей, удовлетворяющих спецификации
        """
        # Получаем все комментарии и фильтруем по спецификации
        all_comments = await self.find_all(options)
        return [
            comment
            for comment in all_comments
            if specification.is_satisfied_by(comment)
        ]

    async def count(
        self, specification: Optional[Specification] = None
    ) -> int:
        """
        Подсчитать количество комментариев

        Args:
            specification: Спецификация для фильтрации

        Returns:
            Количество комментариев
        """
        async with self._get_session() as session:
            try:
                query = select(func.count(VKComment.id))

                if specification:
                    # Для простоты получаем все и фильтруем
                    # В реальном проекте можно реализовать более эффективные запросы
                    all_comments = await self.find_all()
                    return len(
                        [
                            c
                            for c in all_comments
                            if specification.is_satisfied_by(c)
                        ]
                    )

                result = await session.execute(query)
                return result.scalar()

            except Exception as e:
                logger.error(f"Error counting comments: {e}")
                raise

    async def exists(self, entity_id: Any) -> bool:
        """
        Проверить существование комментария

        Args:
            entity_id: ID комментария

        Returns:
            True если комментарий существует
        """
        async with self._get_session() as session:
            try:
                query = select(func.count(VKComment.id)).where(
                    VKComment.id == entity_id
                )
                result = await session.execute(query)
                return result.scalar() > 0

            except Exception as e:
                logger.error(
                    f"Error checking comment existence {entity_id}: {e}"
                )
                raise

    async def delete(self, entity_id: Any) -> bool:
        """
        Удалить комментарий (soft delete)

        Args:
            entity_id: ID комментария

        Returns:
            True если комментарий успешно удален
        """
        async with self._get_session() as session:
            try:
                query = select(VKComment).where(VKComment.id == entity_id)
                result = await session.execute(query)
                db_comment = result.scalar_one_or_none()

                if db_comment:
                    db_comment.is_archived = True
                    db_comment.archived_at = datetime.utcnow()
                    await session.commit()
                    return True

                return False

            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting comment {entity_id}: {e}")
                raise

    async def delete_permanently(self, entity_id: Any) -> bool:
        """
        Удалить комментарий навсегда (hard delete)

        Args:
            entity_id: ID комментария

        Returns:
            True если комментарий успешно удален
        """
        async with self._get_session() as session:
            try:
                query = select(VKComment).where(VKComment.id == entity_id)
                result = await session.execute(query)
                db_comment = result.scalar_one_or_none()

                if db_comment:
                    await session.delete(db_comment)
                    await session.commit()
                    return True

                return False

            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Error permanently deleting comment {entity_id}: {e}"
                )
                raise

    async def update(self, entity: Comment) -> Comment:
        """
        Обновить комментарий

        Args:
            entity: Доменная сущность Comment

        Returns:
            Обновленная сущность
        """
        return await self.save(entity)

    def _domain_to_db(self, comment: Comment) -> VKComment:
        """
        Преобразовать доменную сущность в модель базы данных

        Args:
            comment: Доменная сущность Comment

        Returns:
            Модель базы данных VKComment
        """
        return VKComment(
            id=comment.id,
            vk_id=getattr(comment, "vk_comment_id", None),
            text=comment.content.text if comment.content else "",
            author_id=comment.content.author_id if comment.content else None,
            author_name=(
                comment.content.author_name if comment.content else None
            ),
            published_at=comment.published_at,
            post_id=comment.post_id,
            is_viewed=comment.status.is_viewed,
            is_processed=comment.status.is_processed,
            is_archived=comment.status.is_archived,
            matched_keywords_count=len(comment.keyword_matches),
        )

    def _db_to_domain(self, db_comment: VKComment) -> Comment:
        """
        Преобразовать модель базы данных в доменную сущность

        Args:
            db_comment: Модель базы данных VKComment

        Returns:
            Доменная сущность Comment
        """
        # Создаем Value Objects
        content = CommentContent(
            text=db_comment.text,
            author_name=db_comment.author_name,
            author_id=db_comment.author_id,
        )

        status = CommentStatus(
            is_viewed=db_comment.is_viewed,
            is_processed=db_comment.is_processed,
            is_archived=db_comment.is_archived,
        )

        # Создаем доменную сущность
        comment = Comment(
            id=db_comment.id,
            group_id=(
                db_comment.post.group_id
                if db_comment.post and db_comment.post.group
                else None
            ),
            content=content,
            published_at=db_comment.published_at,
            vk_comment_id=db_comment.vk_id,
            post_id=db_comment.post_id,
        )

        # Устанавливаем статус
        comment.status = status

        # Добавляем keyword matches
        if db_comment.keyword_matches:
            for match in db_comment.keyword_matches:
                comment.keyword_matches.append(match)

        return comment
