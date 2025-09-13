"""
Интерфейс репозитория пользователей

Определяет контракт для работы с пользователями в domain слое
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from user.domain.entities.user import User
from user.domain.value_objects.user_status import UserStatus


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Создать пользователя
        
        Args:
            user: Пользователь для создания
            
        Returns:
            User: Созданный пользователь
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Проверить существование пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            bool: Существует ли пользователь
        """
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Обновить пользователя
        
        Args:
            user: Пользователь для обновления
            
        Returns:
            User: Обновленный пользователь
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: Удален ли пользователь
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, int]:
        """
        Получить статистику пользователей
        
        Returns:
            Dict[str, int]: Статистика
        """
        pass
