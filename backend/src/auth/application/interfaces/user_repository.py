"""
Интерфейс репозитория пользователей для Application Layer

Определяет контракт для работы с пользователями в слое приложения
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from auth.domain.entities.user import User
from auth.domain.value_objects.user_id import UserId
from auth.domain.value_objects.email import Email


class UserRepositoryInterface(ABC):
    """
    Интерфейс репозитория пользователей для Application Layer
    
    Определяет методы для работы с пользователями в слое приложения
    """
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Получить пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Сохранить пользователя
        
        Args:
            user: Пользователь для сохранения
            
        Returns:
            User: Сохраненный пользователь
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """
        Удалить пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True если пользователь удален
        """
        pass
    
    @abstractmethod
    async def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        """
        Получить список пользователей
        
        Args:
            limit: Максимум пользователей
            offset: Смещение
            is_active: Фильтр по активности
            search: Поиск по email или имени
            
        Returns:
            List[User]: Список пользователей
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """
        Проверить существование пользователя по email
        
        Args:
            email: Email пользователя
            
        Returns:
            bool: True если пользователь существует
        """
        pass
    
    @abstractmethod
    async def get_user_stats(self) -> dict:
        """
        Получить статистику пользователей
        
        Returns:
            dict: Статистика пользователей
        """
        pass
