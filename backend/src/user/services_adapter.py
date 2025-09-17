"""
Адаптер сервисов пользователей для обратной совместимости
"""

from typing import Optional

from .domain.services.service_factory import UserServiceFactory
from .domain.services.user_service import UserService
from .exceptions import UserAlreadyExistsError, UserNotFoundError
from .schemas import (
    UserCreateRequest,
    UserListRequest,
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)


class UserServiceAdapter:
    """Адаптер для обратной совместимости с существующим кодом"""

    def __init__(self, db_session):
        """Инициализация адаптера

        Args:
            db_session: Сессия базы данных
        """
        self.factory = UserServiceFactory(db_session)
        self._service: Optional[UserService] = None

    @property
    def service(self) -> UserService:
        """Получает основной сервис пользователей"""
        if self._service is None:
            self._service = self.factory.user_service
        return self._service

    async def create_user(self, user_data: dict) -> UserResponse:
        """Создает пользователя (устаревший метод для обратной совместимости)

        Args:
            user_data: Данные пользователя

        Returns:
            Созданный пользователь
        """
        request = UserCreateRequest(
            email=user_data["email"],
            full_name=user_data["full_name"],
            password=user_data["password"],
            is_superuser=user_data.get("is_superuser", False)
        )

        try:
            user = await self.service.create_user(request)
            return user
        except Exception as e:
            # Преобразование исключений в старый формат
            if "already exists" in str(e).lower():
                raise UserAlreadyExistsError(user_data["email"])
            raise

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получает пользователя по ID"""
        try:
            return await self.service.get_user_by_id(user_id)
        except Exception as e:
            if "not found" in str(e).lower():
                raise UserNotFoundError(user_id)
            raise

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Получает пользователя по email"""
        return await self.service.get_user_by_email(email)

    async def update_user(self, user_id: int, user_data: dict) -> UserResponse:
        """Обновляет пользователя"""
        request = UserUpdateRequest(
            full_name=user_data.get("full_name"),
            email=user_data.get("email"),
            status=user_data.get("status"),
            is_superuser=user_data.get("is_superuser")
        )

        try:
            return await self.service.update_user(user_id, request)
        except Exception as e:
            if "not found" in str(e).lower():
                raise UserNotFoundError(user_id)
            elif "already exists" in str(e).lower():
                raise UserAlreadyExistsError(user_data.get("email", ""))
            raise

    async def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя"""
        try:
            return await self.service.delete_user(user_id)
        except Exception as e:
            if "not found" in str(e).lower():
                raise UserNotFoundError(user_id)
            raise

    async def get_users_list(self, request: UserListRequest) -> UserListResponse:
        """Получает список пользователей"""
        return await self.service.get_users_list(request)

    async def get_user_stats(self) -> UserStatsResponse:
        """Получает статистику пользователей"""
        return await self.service.get_user_stats()