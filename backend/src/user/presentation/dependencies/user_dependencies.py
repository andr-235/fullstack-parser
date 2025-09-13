"""
Зависимости для модуля User

Содержит FastAPI зависимости для работы с пользователями
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from user.domain.entities.user import User
from user.domain.interfaces.user_repository import UserRepositoryInterface
from auth.domain.interfaces.password_service import PasswordServiceInterface
from user.domain.exceptions import (
    UserNotFoundError,
    UserInactiveError,
)
from shared.infrastructure.logging import get_logger

# Security scheme
security = HTTPBearer()


async def get_user_repository() -> UserRepositoryInterface:
    """
    Получить репозиторий пользователей
    
    Returns:
        UserRepositoryInterface: Репозиторий пользователей
    """
    # TODO: Реализовать DI контейнер
    # Пока возвращаем заглушку
    raise NotImplementedError("User repository dependency not implemented")


async def get_password_service() -> PasswordServiceInterface:
    """
    Получить сервис паролей
    
    Returns:
        PasswordServiceInterface: Сервис паролей
    """
    # TODO: Реализовать DI контейнер
    # Пока возвращаем заглушку
    raise NotImplementedError("Password service dependency not implemented")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repository: UserRepositoryInterface = Depends(get_user_repository)
) -> User:
    """
    Получить текущего пользователя по JWT токену
    
    Args:
        credentials: JWT токен из заголовка Authorization
        user_repository: Репозиторий пользователей
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    logger = get_logger()
    
    try:
        # TODO: Реализовать JWT сервис
        # Пока возвращаем заглушку
        raise NotImplementedError("JWT service not implemented")
        
    except UserNotFoundError:
        logger.warning(f"User not found for token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Получить текущего активного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Активный пользователь
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    if not current_user.status.can_login():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Получить текущего суперпользователя
    
    Args:
        current_user: Текущий активный пользователь
        
    Returns:
        User: Суперпользователь
        
    Raises:
        HTTPException: Если пользователь не является суперпользователем
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
