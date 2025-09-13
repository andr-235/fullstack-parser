"""
SQLAlchemy репозиторий пользователей

Реализует UserRepositoryInterface с использованием SQLAlchemy 2.0 async
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from user.domain.entities.user import User
from user.domain.value_objects.user_status import UserStatus
from user.domain.interfaces.user_repository import UserRepositoryInterface
from user.domain.exceptions import UserNotFoundError
from shared.infrastructure.logging import get_logger


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """SQLAlchemy репозиторий пользователей"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = get_logger()
    
    async def create(self, user: User) -> User:
        """
        Создать пользователя
        
        Args:
            user: Пользователь для создания
            
        Returns:
            User: Созданный пользователь
        """
        try:
            # TODO: Реализовать SQLAlchemy модель User
            # Пока возвращаем пользователя с ID = 1
            created_user = User(
                id=user.id._replace(value=1),  # Устанавливаем ID
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                status=user.status,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                login_attempts=user.login_attempts,
                locked_until=user.locked_until,
                email_verified=user.email_verified,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
            self.logger.info(f"User created with ID: {created_user.id.value}")
            return created_user
            
        except Exception as e:
            self.logger.error(f"Error creating user: {e}")
            raise
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос
            # Пока возвращаем заглушку
            if user_id == 1:
                from auth.domain.value_objects.email import Email
                from auth.domain.value_objects.password import Password
                from user.domain.value_objects.user_id import UserId
                from datetime import datetime
                
                return User(
                    id=UserId(value=1),
                    email=Email(value="test@example.com"),
                    full_name="Test User",
                    hashed_password=Password.create_from_hash("hashed_password"),
                    status=UserStatus.ACTIVE,
                    is_superuser=False,
                    email_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос
            # Пока возвращаем заглушку
            if email == "test@example.com":
                from auth.domain.value_objects.email import Email
                from auth.domain.value_objects.password import Password
                from user.domain.value_objects.user_id import UserId
                from datetime import datetime
                
                return User(
                    id=UserId(value=1),
                    email=Email(value=email),
                    full_name="Test User",
                    hashed_password=Password.create_from_hash("hashed_password"),
                    status=UserStatus.ACTIVE,
                    is_superuser=False,
                    email_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить существование пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            bool: Существует ли пользователь
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос
            # Пока возвращаем заглушку
            return email == "test@example.com"
            
        except Exception as e:
            self.logger.error(f"Error checking user existence by email {email}: {e}")
            return False
    
    async def update(self, user: User) -> User:
        """
        Обновить пользователя
        
        Args:
            user: Пользователь для обновления
            
        Returns:
            User: Обновленный пользователь
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос
            # Пока возвращаем пользователя с обновленным updated_at
            from datetime import datetime
            
            updated_user = User(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                status=user.status,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                login_attempts=user.login_attempts,
                locked_until=user.locked_until,
                email_verified=user.email_verified,
                created_at=user.created_at,
                updated_at=datetime.utcnow()
            )
            
            self.logger.info(f"User updated with ID: {updated_user.id.value}")
            return updated_user
            
        except Exception as e:
            self.logger.error(f"Error updating user: {e}")
            raise
    
    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: Удален ли пользователь
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос
            # Пока возвращаем заглушку
            self.logger.info(f"User deleted with ID: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    async def get_paginated(
        self,
        limit: int = 50,
        offset: int = 0,
        status: Optional[UserStatus] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """
        Получить пользователей с пагинацией
        
        Args:
            limit: Лимит записей
            offset: Смещение
            status: Фильтр по статусу
            search: Поисковый запрос
            
        Returns:
            tuple[List[User], int]: Список пользователей и общее количество
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос с пагинацией
            # Пока возвращаем заглушку
            from auth.domain.value_objects.email import Email
            from auth.domain.value_objects.password import Password
            from user.domain.value_objects.user_id import UserId
            from datetime import datetime
            
            # Создаем тестового пользователя
            test_user = User(
                id=UserId(value=1),
                email=Email(value="test@example.com"),
                full_name="Test User",
                hashed_password=Password.create_from_hash("hashed_password"),
                status=UserStatus.ACTIVE,
                is_superuser=False,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            users = [test_user] if offset == 0 else []
            total = 1
            
            self.logger.info(f"Retrieved {len(users)} users with pagination")
            return users, total
            
        except Exception as e:
            self.logger.error(f"Error getting paginated users: {e}")
            return [], 0
    
    async def get_stats(self) -> Dict[str, int]:
        """
        Получить статистику пользователей
        
        Returns:
            Dict[str, int]: Статистика
        """
        try:
            # TODO: Реализовать SQLAlchemy запрос для статистики
            # Пока возвращаем заглушку
            stats = {
                "total": 1,
                "active": 1,
                "inactive": 0,
                "locked": 0,
                "pending_verification": 0,
                "superusers": 0
            }
            
            self.logger.info(f"Retrieved user stats: {stats}")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting user stats: {e}")
            return {
                "total": 0,
                "active": 0,
                "inactive": 0,
                "locked": 0,
                "pending_verification": 0,
                "superusers": 0
            }
