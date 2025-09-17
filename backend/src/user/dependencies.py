"""
FastAPI зависимости для пользователей
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.password_service import PasswordService, PasswordServiceProtocol
from src.common.database import get_db_session
from src.common.logging import get_logger

from .exceptions import UserNotFoundError
from .models import User
from .repository import UserRepository
from .services import UserService

# Security scheme
security = HTTPBearer()


def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Получить репозиторий пользователей

    Args:
        session: Асинхронная сессия базы данных

    Returns:
        UserRepository: Репозиторий пользователей
    """
    return UserRepository(session)


def get_password_service() -> PasswordServiceProtocol:
    """Получить сервис паролей

    Returns:
        PasswordServiceProtocol: Сервис для работы с паролями
    """
    return PasswordService()


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    password_service: PasswordServiceProtocol = Depends(get_password_service)
) -> UserService:
    """Получить сервис пользователей

    Args:
        repository: Репозиторий пользователей
        password_service: Сервис для работы с паролями

    Returns:
        UserService: Сервис пользователей
    """
    return UserService(repository, password_service)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Получить текущего пользователя по JWT токену
    
    Args:
        credentials: JWT токен из заголовка Authorization
        user_service: Сервис пользователей
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    logger = get_logger()

    try:
        # TODO: Реализовать JWT сервис
        # Пока возвращаем заглушку для тестирования
        if credentials.credentials == "test_token":
            # Создаем тестового пользователя
            from datetime import datetime

            from .models import User
            from .schemas import UserStatus

            return User(
                id=1,
                email="test@example.com",
                full_name="Test User",
                hashed_password="hashed_password",
                status=UserStatus.ACTIVE.value,
                is_superuser=False,
                email_verified=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    except UserNotFoundError:
        logger.warning("User not found for token")
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
    """Получить текущего активного пользователя"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Получить текущего суперпользователя"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
