"""
Use Cases для пользователей

Содержит use cases для операций с пользователями
"""

from typing import List
from user.domain.entities.user import User
from user.application.services.user_service import UserService
from user.application.dtos.user_dtos import (
    CreateUserRequestDTO,
    UpdateUserRequestDTO,
    UserResponseDTO,
    UserListRequestDTO,
    UserListResponseDTO,
    UserStatsResponseDTO,
)
from shared.infrastructure.logging import get_logger


class CreateUserUseCase:
    """Use Case для создания пользователя"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self, request: CreateUserRequestDTO) -> UserResponseDTO:
        """
        Выполнить создание пользователя
        
        Args:
            request: Данные для создания пользователя
            
        Returns:
            UserResponseDTO: Созданный пользователь
        """
        self.logger.info(f"User creation attempt for email: {request.email}")
        return await self.user_service.create_user(request)


class GetUserUseCase:
    """Use Case для получения пользователя по ID"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self, user_id: int) -> UserResponseDTO:
        """
        Выполнить получение пользователя по ID
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserResponseDTO: Данные пользователя
        """
        self.logger.info(f"Get user request for ID: {user_id}")
        return await self.user_service.get_user_by_id(user_id)


class GetCurrentUserUseCase:
    """Use Case для получения текущего пользователя"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self, user: User) -> UserResponseDTO:
        """
        Выполнить получение текущего пользователя
        
        Args:
            user: Текущий пользователь
            
        Returns:
            UserResponseDTO: Данные пользователя
        """
        self.logger.info(f"Get current user request for ID: {user.id.value}")
        return await self.user_service.get_current_user(user)


class UpdateUserUseCase:
    """Use Case для обновления пользователя"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self, user: User, request: UpdateUserRequestDTO) -> UserResponseDTO:
        """
        Выполнить обновление пользователя
        
        Args:
            user: Текущий пользователь
            request: Данные для обновления
            
        Returns:
            UserResponseDTO: Обновленный пользователь
        """
        self.logger.info(f"User update attempt for ID: {user.id.value}")
        return await self.user_service.update_user(user, request)


class GetUsersListUseCase:
    """Use Case для получения списка пользователей"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self, request: UserListRequestDTO) -> UserListResponseDTO:
        """
        Выполнить получение списка пользователей
        
        Args:
            request: Параметры запроса
            
        Returns:
            UserListResponseDTO: Список пользователей
        """
        self.logger.info(f"Get users list request: limit={request.limit}, offset={request.offset}")
        return await self.user_service.get_users_list(request)


class GetUserStatsUseCase:
    """Use Case для получения статистики пользователей"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self.logger = get_logger()
    
    async def execute(self) -> UserStatsResponseDTO:
        """
        Выполнить получение статистики пользователей
        
        Returns:
            UserStatsResponseDTO: Статистика пользователей
        """
        self.logger.info("Get user stats request")
        return await self.user_service.get_user_stats()
