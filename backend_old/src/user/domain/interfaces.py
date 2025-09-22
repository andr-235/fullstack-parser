"""
Интерфейсы для доменного слоя пользователей
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..schemas import (
    UserCreateRequest,
    UserListRequest,
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Проверяет существование пользователя по email"""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[object]:
        """Получает пользователя по ID"""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[object]:
        """Получает пользователя по email"""
        pass

    @abstractmethod
    async def create(self, user_data: dict) -> object:
        """Создает нового пользователя"""
        pass

    @abstractmethod
    async def update(self, user: object) -> object:
        """Обновляет пользователя"""
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """Удаляет пользователя"""
        pass

    @abstractmethod
    async def get_paginated(
        self,
        limit: int,
        offset: int,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[object], int]:
        """Получает пагинированный список пользователей"""
        pass

    @abstractmethod
    async def get_stats(self) -> dict:
        """Получает статистику пользователей"""
        pass


class IPasswordService(ABC):
    """Интерфейс сервиса паролей"""

    @abstractmethod
    async def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        pass

    @abstractmethod
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверяет пароль"""
        pass


class IUserValidator(ABC):
    """Интерфейс валидатора пользователей"""

    @abstractmethod
    async def validate_create_data(self, data: UserCreateRequest) -> None:
        """Валидирует данные для создания пользователя"""
        pass

    @abstractmethod
    async def validate_update_data(self, data: UserUpdateRequest) -> None:
        """Валидирует данные для обновления пользователя"""
        pass


class IUserService(ABC):
    """Интерфейс сервиса пользователей"""

    @abstractmethod
    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """Создает пользователя"""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получает пользователя по ID"""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Получает пользователя по email"""
        pass

    @abstractmethod
    async def update_user(self, user_id: int, request: UserUpdateRequest) -> UserResponse:
        """Обновляет пользователя"""
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя"""
        pass

    @abstractmethod
    async def get_users_list(self, request: UserListRequest) -> UserListResponse:
        """Получает список пользователей"""
        pass

    @abstractmethod
    async def get_user_stats(self) -> UserStatsResponse:
        """Получает статистику пользователей"""
        pass