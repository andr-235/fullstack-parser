"""
Use Case для регистрации пользователя

Инкапсулирует бизнес-логику регистрации
"""

from typing import Dict, Any
from auth.application.dto.register_user_dto import RegisterUserDTO
from auth.application.dto.user_dto import UserDTO
from auth.application.interfaces.user_repository import UserRepositoryInterface
from auth.application.interfaces.password_service import PasswordServiceInterface
from auth.domain.entities.user import User
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from auth.domain.value_objects.user_id import UserId
from auth.shared.exceptions import EmailAlreadyExistsError, ValidationError


class RegisterUserUseCase:
    """
    Use Case для регистрации пользователя
    
    Инкапсулирует бизнес-логику создания нового пользователя
    """
    
    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        password_service: PasswordServiceInterface,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
    
    async def execute(self, dto: RegisterUserDTO) -> UserDTO:
        """
        Выполнить регистрацию пользователя
        
        Args:
            dto: Данные для регистрации
            
        Returns:
            UserDTO: Данные созданного пользователя
            
        Raises:
            EmailAlreadyExistsError: Если email уже используется
            ValidationError: Если данные невалидны
        """
        # Создаем Value Objects
        email = Email(dto.email)
        password = Password.create_from_plain(dto.password)
        
        # Проверяем, что пользователь с таким email не существует
        if await self.user_repository.exists_by_email(email):
            raise EmailAlreadyExistsError(dto.email)
        
        # Хешируем пароль
        hashed_password = self.password_service.hash_password(password)
        
        # Создаем пользователя
        user = User(
            id=UserId(0),  # Будет установлен при сохранении
            email=email,
            full_name=dto.full_name.strip(),
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )
        
        # Сохраняем пользователя
        saved_user = await self.user_repository.save(user)
        
        # Возвращаем DTO
        return UserDTO.from_entity(saved_user)
