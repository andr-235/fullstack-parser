"""
Сервис пользователей

Содержит бизнес-логику для управления пользователями
"""

from typing import List, Optional, Dict, Any
from user.domain.entities.user import User
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from user.domain.value_objects.user_id import UserId
from user.domain.value_objects.user_status import UserStatus
from user.domain.interfaces.user_repository import UserRepositoryInterface
from auth.domain.interfaces.password_service import PasswordServiceInterface
from user.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
)
from user.application.dtos.user_dtos import (
    CreateUserRequestDTO,
    UpdateUserRequestDTO,
    UserResponseDTO,
    UserListRequestDTO,
    UserListResponseDTO,
    UserStatsResponseDTO,
)
from shared.infrastructure.logging import get_logger


class UserService:
    """Сервис пользователей"""
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.logger = get_logger()
    
    async def create_user(self, request: CreateUserRequestDTO) -> UserResponseDTO:
        """
        Создать пользователя
        
        Args:
            request: Данные для создания пользователя
            
        Returns:
            UserResponseDTO: Созданный пользователь
            
        Raises:
            UserAlreadyExistsError: Пользователь уже существует
        """
        # Проверяем не существует ли пользователь
        existing_user = await self.user_repository.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError(request.email)
        
        # Хешируем пароль
        hashed_password = await self.password_service.hash_password(request.password)
        
        # Создаем пользователя
        user = User(
            id=UserId(value=0),  # ID будет установлен БД
            email=Email(value=request.email),
            full_name=request.full_name,
            hashed_password=Password.create_from_hash(hashed_password),
            is_superuser=request.is_superuser
        )
        
        created_user = await self.user_repository.create(user)
        return self._user_to_dto(created_user)
    
    async def get_user_by_id(self, user_id: int) -> UserResponseDTO:
        """
        Получить пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserResponseDTO: Данные пользователя
            
        Raises:
            UserNotFoundError: Пользователь не найден
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        return self._user_to_dto(user)
    
    async def get_current_user(self, user: User) -> UserResponseDTO:
        """
        Получить данные текущего пользователя
        
        Args:
            user: Текущий пользователь
            
        Returns:
            UserResponseDTO: Данные пользователя
        """
        return self._user_to_dto(user)
    
    async def update_user(
        self, 
        user: User, 
        request: UpdateUserRequestDTO
    ) -> UserResponseDTO:
        """
        Обновить пользователя
        
        Args:
            user: Текущий пользователь
            request: Данные для обновления
            
        Returns:
            UserResponseDTO: Обновленный пользователь
            
        Raises:
            UserAlreadyExistsError: Email уже используется
        """
        # Проверяем email на уникальность если он изменился
        if request.email and request.email != user.email.value:
            existing_user = await self.user_repository.get_by_email(request.email)
            if existing_user:
                raise UserAlreadyExistsError(request.email)
        
        # Обновляем пользователя
        updated_user = user.update_profile(
            full_name=request.full_name or user.full_name,
            email=Email(value=request.email) if request.email else user.email
        )
        
        # Обновляем статус если указан
        if request.status is not None:
            updated_user = updated_user._copy(status=request.status)
        
        # Обновляем права суперпользователя если указаны
        if request.is_superuser is not None:
            updated_user = updated_user._copy(is_superuser=request.is_superuser)
        
        saved_user = await self.user_repository.update(updated_user)
        return self._user_to_dto(saved_user)
    
    async def get_users_list(self, request: UserListRequestDTO) -> UserListResponseDTO:
        """
        Получить список пользователей
        
        Args:
            request: Параметры запроса
            
        Returns:
            UserListResponseDTO: Список пользователей
        """
        users, total = await self.user_repository.get_paginated(
            limit=request.limit,
            offset=request.offset,
            status=request.status,
            search=request.search
        )
        
        user_dtos = [self._user_to_dto(user) for user in users]
        
        return UserListResponseDTO(
            users=user_dtos,
            total=total,
            limit=request.limit,
            offset=request.offset,
            has_next=request.offset + request.limit < total,
            has_prev=request.offset > 0
        )
    
    async def get_user_stats(self) -> UserStatsResponseDTO:
        """
        Получить статистику пользователей
        
        Returns:
            UserStatsResponseDTO: Статистика пользователей
        """
        stats = await self.user_repository.get_stats()
        
        return UserStatsResponseDTO(
            total_users=stats.get("total", 0),
            active_users=stats.get("active", 0),
            inactive_users=stats.get("inactive", 0),
            locked_users=stats.get("locked", 0),
            pending_verification=stats.get("pending_verification", 0),
            superusers=stats.get("superusers", 0)
        )
    
    def _user_to_dto(self, user: User) -> UserResponseDTO:
        """
        Преобразовать User entity в UserResponseDTO
        
        Args:
            user: User entity
            
        Returns:
            UserResponseDTO: DTO пользователя
        """
        return UserResponseDTO(
            id=user.id.value,
            email=user.email.value,
            full_name=user.full_name,
            status=user.status,
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
