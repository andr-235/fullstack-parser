"""
Настройка DI контейнера для модуля Auth

Содержит функции для инициализации и настройки зависимостей
"""

from typing import Optional
from auth.infrastructure.di.container import AuthContainer, set_container
from user.domain.interfaces.user_repository import UserRepositoryInterface
from auth.domain.interfaces.password_service import PasswordServiceInterface
from auth.domain.interfaces.jwt_service import JWTServiceInterface
from shared.infrastructure.logging import get_logger


def setup_auth_container(
    user_repository: UserRepositoryInterface,
    password_service: PasswordServiceInterface,
    jwt_service: JWTServiceInterface,
    container: Optional[AuthContainer] = None
) -> AuthContainer:
    """
    Настроить DI контейнер для модуля Auth
    
    Args:
        user_repository: Репозиторий пользователей
        password_service: Сервис паролей
        jwt_service: JWT сервис
        container: Существующий контейнер (опционально)
        
    Returns:
        AuthContainer: Настроенный контейнер
    """
    logger = get_logger()
    
    if container is None:
        container = AuthContainer()
    
    # Устанавливаем зависимости
    container.set_user_repository(user_repository)
    container.set_password_service(password_service)
    container.set_jwt_service(jwt_service)
    
    # Устанавливаем глобальный контейнер
    set_container(container)
    
    logger.info("Auth DI container configured successfully")
    return container


def get_configured_container() -> AuthContainer:
    """
    Получить настроенный контейнер
    
    Returns:
        AuthContainer: Настроенный контейнер
        
    Raises:
        ValueError: Если контейнер не настроен
    """
    from .container import get_container
    
    container = get_container()
    
    # Проверяем что контейнер настроен
    try:
        container._validate_dependencies()
    except ValueError as e:
        raise ValueError(f"Auth container not properly configured: {e}")
    
    return container


def reset_container() -> None:
    """Сбросить глобальный контейнер"""
    set_container(None)
    logger = get_logger()
    logger.info("Auth DI container reset")
