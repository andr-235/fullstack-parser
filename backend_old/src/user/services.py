"""
Сервисы пользователей
"""

from datetime import datetime
from typing import Optional

from src.auth.service import AuthService

from .exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
)
from .models import User
from .repository import UserRepository
from .schemas import (
    UserCreateRequest,
    UserListRequest,
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    UserStatus,
    UserUpdateRequest,
)


class UserService:
    """Сервис пользователей с поддержкой аутентификации"""

    def __init__(
        self,
        repository: UserRepository,
        auth_service: AuthService
    ):
        """Инициализация сервиса пользователей

        Args:
            repository: Репозиторий пользователей
            auth_service: Сервис аутентификации
        """
        self.repository = repository
        self.auth_service = auth_service

    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """Создать пользователя"""
        # Проверяем существование пользователя
        if await self.repository.exists_by_email(request.email):
            raise UserAlreadyExistsError(request.email)

        # Хешируем пароль
        hashed_password = await self.auth_service.hash_password(request.password)

        # Создаем пользователя
        user_data = {
            "email": request.email,
            "full_name": request.full_name,
            "hashed_password": hashed_password,
            "status": UserStatus.ACTIVE.value,
            "is_superuser": request.is_superuser,
            "email_verified": False
        }

        user = await self.repository.create(user_data)
        return self._user_to_response(user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получить пользователя по ID"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        return self._user_to_response(user)

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Получить пользователя по email"""
        user = await self.repository.get_by_email(email)
        if not user:
            return None

        return self._user_to_response(user)

    async def update_user(self, user_id: int, request: UserUpdateRequest) -> UserResponse:
        """Обновить пользователя"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Проверяем email на уникальность
        if request.email and request.email != user.email:
            if await self.repository.exists_by_email(request.email):
                raise UserAlreadyExistsError(request.email)

        # Обновляем поля
        if request.full_name is not None:
            user.full_name = request.full_name
        if request.email is not None:
            user.email = request.email
        if request.status is not None:
            user.status = request.status.value
        if request.is_superuser is not None:
            user.is_superuser = request.is_superuser

        user.updated_at = datetime.utcnow()

        updated_user = await self.repository.update(user)
        return self._user_to_response(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        return await self.repository.delete(user_id)

    async def get_users_list(self, request: UserListRequest) -> UserListResponse:
        """Получить список пользователей"""
        users, total = await self.repository.get_paginated(
            limit=request.limit,
            offset=request.offset,
            status=request.status,
            search=request.search
        )

        user_responses = [self._user_to_response(user) for user in users]

        return UserListResponse(
            users=user_responses,
            total=total,
            limit=request.limit,
            offset=request.offset,
            has_next=request.offset + request.limit < total,
            has_prev=request.offset > 0
        )

    async def get_user_stats(self) -> UserStatsResponse:
        """Получить статистику пользователей"""
        stats = await self.repository.get_stats()

        return UserStatsResponse(
            total_users=stats["total"],
            active_users=stats["active"],
            inactive_users=stats["inactive"],
            locked_users=stats["locked"],
            pending_verification=stats["pending_verification"],
            superusers=stats["superusers"]
        )

    def _user_to_response(self, user: User) -> UserResponse:
        """Преобразовать User в UserResponse"""
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            status=UserStatus(user.status),
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
