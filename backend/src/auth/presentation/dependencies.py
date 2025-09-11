"""
Зависимости для модуля Auth (Clean Architecture)

Определяет FastAPI зависимости для аутентификации с использованием Clean Architecture
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.application.use_cases.register_user import RegisterUserUseCase
from auth.application.interfaces.user_repository import UserRepositoryInterface
from auth.application.interfaces.password_service import PasswordServiceInterface
from auth.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from auth.infrastructure.adapters.security_service_adapter import (
    SecurityServicePasswordAdapter,
    SecurityServiceTokenAdapter,
)
from auth.application.dto.user_dto import UserDTO
from auth.domain.value_objects.user_id import UserId
from auth.domain.value_objects.email import Email
from auth.shared.exceptions import UserNotFoundError, InvalidTokenError
from src.database import get_db_session
from src.infrastructure import security_service

# Схема аутентификации
security = HTTPBearer(auto_error=False)


async def get_user_repository() -> UserRepositoryInterface:
    """
    Получить репозиторий пользователей
    
    Returns:
        UserRepositoryInterface: Репозиторий пользователей
    """
    db_session = await get_db_session()
    return SQLAlchemyUserRepository(db_session)


async def get_password_service() -> PasswordServiceInterface:
    """
    Получить сервис паролей
    
    Returns:
        PasswordServiceInterface: Сервис паролей
    """
    return SecurityServicePasswordAdapter()


async def get_token_service():
    """
    Получить сервис токенов
    
    Returns:
        TokenService: Сервис токенов
    """
    return SecurityServiceTokenAdapter()


async def get_register_user_use_case(
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    password_service: PasswordServiceInterface = Depends(get_password_service),
) -> RegisterUserUseCase:
    """
    Получить use case для регистрации пользователя
    
    Args:
        user_repository: Репозиторий пользователей
        password_service: Сервис паролей
        
    Returns:
        RegisterUserUseCase: Use case для регистрации
    """
    return RegisterUserUseCase(user_repository, password_service)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    user_repository: UserRepositoryInterface = Depends(get_user_repository),
    token_service = Depends(get_token_service),
) -> Optional[UserDTO]:
    """
    Получить текущего пользователя (опционально)
    
    Args:
        credentials: Учетные данные аутентификации
        user_repository: Репозиторий пользователей
        token_service: Сервис токенов
        
    Returns:
        Optional[UserDTO]: Пользователь или None
    """
    if not credentials:
        return None
    
    try:
        # Декодируем токен
        payload = token_service.decode_token(credentials.credentials)
        if not payload:
            return None
        
        # Получаем ID пользователя
        user_id = int(payload.get("sub"))
        if not user_id:
            return None
        
        # Получаем пользователя из репозитория
        user = await user_repository.get_by_id(UserId(user_id))
        if not user or not user.is_active:
            return None
        
        # Преобразуем в DTO
        return UserDTO.from_entity(user)
        
    except Exception:
        return None


async def get_current_user(
    user: Optional[UserDTO] = Depends(get_current_user_optional),
) -> UserDTO:
    """
    Получить текущего пользователя (обязательно)
    
    Args:
        user: Текущий пользователь
        
    Returns:
        UserDTO: Пользователь
        
    Raises:
        HTTPException: Если пользователь не аутентифицирован
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    """
    Получить текущего активного пользователя
    
    Args:
        user: Текущий пользователь
        
    Returns:
        UserDTO: Активный пользователь
        
    Raises:
        HTTPException: Если пользователь не активен
    """
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не активен",
        )
    
    return user


async def get_current_superuser(
    user: UserDTO = Depends(get_current_active_user),
) -> UserDTO:
    """
    Получить текущего суперпользователя
    
    Args:
        user: Текущий пользователь
        
    Returns:
        UserDTO: Суперпользователь
        
    Raises:
        HTTPException: Если пользователь не суперпользователь
    """
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа",
        )
    
    return user


# Экспорт зависимостей
__all__ = [
    "get_user_repository",
    "get_password_service",
    "get_token_service",
    "get_register_user_use_case",
    "get_current_user_optional",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "security",
]
