"""
Интерфейсы для модуля аутентификации
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.user.models import User


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass

    @abstractmethod
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Создать нового пользователя"""
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        """Обновить пользователя"""
        pass


class IPasswordService(ABC):
    """Интерфейс сервиса паролей"""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Захешировать пароль"""
        pass

    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверить пароль"""
        pass


class IJWTService(ABC):
    """Интерфейс JWT сервиса"""

    @abstractmethod
    async def create_access_token(self, data: Dict[str, Any]) -> str:
        """Создать access токен"""
        pass

    @abstractmethod
    async def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Создать refresh токен"""
        pass

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Валидировать токен"""
        pass

    @abstractmethod
    async def revoke_token(self, token: str) -> None:
        """Отозвать токен"""
        pass


class ICacheService(ABC):
    """Интерфейс сервиса кеширования"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кеш"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Удалить значение из кеша"""
        pass


class IEventPublisher(ABC):
    """Интерфейс для публикации событий"""

    @abstractmethod
    async def publish_event(self, event_type: str, user_id: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Опубликовать событие"""
        pass

    @abstractmethod
    async def send_email(self, email: str, subject: str, body: str) -> None:
        """Отправить email"""
        pass