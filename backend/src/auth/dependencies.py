"""
Зависимости для аутентификации
"""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from common.logging import get_logger

from .exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)
from .services import AuthService

security = HTTPBearer()


async def get_auth_service() -> AuthService:
    """Получить сервис аутентификации"""
    from .setup import get_auth_service as _get_auth_service
    return _get_auth_service()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Получить текущего пользователя по токену"""
    try:
        user = await auth_service.validate_user_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (InvalidTokenError, TokenExpiredError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger = get_logger_with_correlation()
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Получить активного пользователя"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_correlation_id() -> Optional[str]:
    """Получить correlation ID из контекста"""
    # Здесь должна быть логика получения correlation ID
    # Пока возвращаем None
    return None
