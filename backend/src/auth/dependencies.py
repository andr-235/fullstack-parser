"""
Зависимости для модуля Auth

Определяет FastAPI зависимости для аутентификации
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .service import AuthService
from .models import UserRepository, get_user_repository


# Схема аутентификации
security = HTTPBearer(auto_error=False)


async def get_auth_service(
    repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """
    Получить сервис аутентификации

    Args:
        repository: Репозиторий пользователей

    Returns:
        AuthService: Сервис аутентификации
    """
    return AuthService(repository)


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    service: AuthService = Depends(get_auth_service),
) -> Optional[dict]:
    """
    Получить текущего пользователя (опционально)

    Args:
        credentials: Учетные данные аутентификации
        service: Сервис аутентификации

    Returns:
        Optional[dict]: Пользователь или None
    """
    if not credentials:
        return None

    try:
        # Валидируем токен
        token_data = await service.validate_token(credentials.credentials)
        if token_data and token_data.get("valid"):
            return token_data.get("user")
    except Exception:
        pass

    return None


async def get_current_user(
    user: Optional[dict] = Depends(get_current_user_optional),
) -> dict:
    """
    Получить текущего пользователя (обязательно)

    Args:
        user: Текущий пользователь

    Returns:
        dict: Пользователь

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
    user: dict = Depends(get_current_user),
) -> dict:
    """
    Получить текущего активного пользователя

    Args:
        user: Текущий пользователь

    Returns:
        dict: Активный пользователь

    Raises:
        HTTPException: Если пользователь не активен
    """
    if not user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не активен",
        )

    return user


async def get_current_superuser(
    user: dict = Depends(get_current_active_user),
) -> dict:
    """
    Получить текущего суперпользователя

    Args:
        user: Текущий пользователь

    Returns:
        dict: Суперпользователь

    Raises:
        HTTPException: Если пользователь не суперпользователь
    """
    if not user.get("is_superuser"):
        raise HTTPHTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа",
        )

    return user


async def get_user_by_id(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Получить пользователя по ID

    Args:
        user_id: ID пользователя
        service: Сервис аутентификации

    Returns:
        dict: Пользователь

    Raises:
        HTTPException: Если пользователь не найден
    """
    try:
        return await service.get_user(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )


# Экспорт зависимостей
__all__ = [
    "get_auth_service",
    "get_current_user_optional",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_user_by_id",
    "security",
]
