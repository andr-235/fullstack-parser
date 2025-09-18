"""
Сервис пользователей с применением SOLID принципов
"""

from typing import List, Optional

from ...exceptions import UserAlreadyExistsError, UserNotFoundError
from ...schemas import (
    UserCreateRequest,
    UserListRequest,
    UserListResponse,
    UserResponse,
    UserStatsResponse,
    UserUpdateRequest,
)
from ..interfaces import IUserRepository, IUserService, IUserValidator, IPasswordService


class UserService(IUserService):
    """Сервис пользователей с разделением ответственности"""

    def __init__(
        self,
        repository: IUserRepository,
        password_service: IPasswordService,
        validator: IUserValidator
    ):
        """Инициализация сервиса пользователей

        Args:
            repository: Репозиторий пользователей
            password_service: Сервис для работы с паролями
            validator: Валидатор данных пользователей
        """
        self.repository = repository
        self.password_service = password_service
        self.validator = validator

    async def create_user(self, request: UserCreateRequest) -> UserResponse:
        """Создает пользователя с валидацией

        Args:
            request: Данные для создания пользователя

        Returns:
            Созданный пользователь

        Raises:
            ValidationError: Если данные невалидны
            UserAlreadyExistsError: Если пользователь уже существует
        """
        # Валидация входных данных
        await self.validator.validate_create_data(request)

        # Проверяем существование пользователя
        if await self.repository.exists_by_email(request.email):
            raise UserAlreadyExistsError(request.email)

        # Хешируем пароль
        hashed_password = await self.password_service.hash_password(request.password)

        # Создаем пользователя
        user_data = {
            "email": request.email,
            "full_name": request.full_name,
            "hashed_password": hashed_password,
            "status": "active",
            "is_superuser": request.is_superuser,
            "email_verified": False
        }

        user = await self.repository.create(user_data)
        return self._user_to_response(user)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получает пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            Пользователь

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        return self._user_to_response(user)

    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Получает пользователя по email

        Args:
            email: Email пользователя

        Returns:
            Пользователь или None
        """
        user = await self.repository.get_by_email(email)
        if not user:
            return None

        return self._user_to_response(user)

    async def update_user(self, user_id: int, request: UserUpdateRequest) -> UserResponse:
        """Обновляет пользователя

        Args:
            user_id: ID пользователя
            request: Данные для обновления

        Returns:
            Обновленный пользователь

        Raises:
            UserNotFoundError: Если пользователь не найден
            ValidationError: Если данные невалидны
            UserAlreadyExistsError: Если email уже занят
        """
        # Валидация входных данных
        await self.validator.validate_update_data(request)

        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        # Проверяем email на уникальность
        if request.email and request.email != user.email:
            if await self.repository.exists_by_email(request.email):
                raise UserAlreadyExistsError(request.email)

        # Обновляем поля
        update_data = {}
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.email is not None:
            update_data["email"] = request.email
        if request.status is not None:
            update_data["status"] = request.status.value
        if request.is_superuser is not None:
            update_data["is_superuser"] = request.is_superuser

        updated_user = await self.repository.update(user_id, update_data)
        return self._user_to_response(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        """Удаляет пользователя

        Args:
            user_id: ID пользователя

        Returns:
            True если пользователь удален
        """
        return await self.repository.delete(user_id)

    async def get_users_list(self, request: UserListRequest) -> UserListResponse:
        """Получает список пользователей

        Args:
            request: Параметры запроса

        Returns:
            Список пользователей с пагинацией
        """
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
        """Получает статистику пользователей

        Returns:
            Статистика пользователей
        """
        stats = await self.repository.get_stats()
        return UserStatsResponse(**stats)

    def _user_to_response(self, user: object) -> UserResponse:
        """Преобразует модель пользователя в схему ответа

        Args:
            user: Модель пользователя

        Returns:
            Схема ответа
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            status=user.status,
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at
        )