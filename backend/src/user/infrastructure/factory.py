"""
Фабрика для создания зависимостей модуля User

Содержит функции для создания всех Infrastructure компонентов
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from user.infrastructure.repositories import SQLAlchemyUserRepository, CachedUserRepository
from user.infrastructure.di.container import UserContainer
from shared.infrastructure.logging import get_logger


def create_user_repository(session: AsyncSession) -> SQLAlchemyUserRepository:
    """
    Создать репозиторий пользователей
    
    Args:
        session: SQLAlchemy сессия
        
    Returns:
        SQLAlchemyUserRepository: Репозиторий пользователей
    """
    return SQLAlchemyUserRepository(session=session)


def create_cached_user_repository(
    repository: SQLAlchemyUserRepository,
    cache,
    cache_ttl: int = 300
) -> CachedUserRepository:
    """
    Создать кэшированный репозиторий пользователей
    
    Args:
        repository: Базовый репозиторий
        cache: Кэш адаптер
        cache_ttl: TTL кэша в секундах
        
    Returns:
        CachedUserRepository: Кэшированный репозиторий
    """
    return CachedUserRepository(
        repository=repository,
        cache=cache,
        cache_ttl=cache_ttl
    )


def setup_user_infrastructure(
    session: AsyncSession,
    password_service,
    cache=None,
    use_cache: bool = False
) -> UserContainer:
    """
    Настроить инфраструктуру модуля User
    
    Args:
        session: SQLAlchemy сессия
        password_service: Сервис паролей
        cache: Кэш адаптер (опционально)
        use_cache: Использовать ли кэширование
        
    Returns:
        UserContainer: Настроенный DI контейнер
    """
    logger = get_logger()
    logger.info("Setting up User infrastructure")
    
    # Создаем репозиторий
    user_repository = create_user_repository(session)
    
    # Если нужно кэширование и есть кэш
    if use_cache and cache:
        user_repository = create_cached_user_repository(
            repository=user_repository,
            cache=cache
        )
        logger.info("User repository with caching enabled")
    else:
        logger.info("User repository without caching")
    
    # Создаем контейнер
    container = UserContainer()
    container.set_user_repository(user_repository)
    container.set_password_service(password_service)
    
    logger.info("User infrastructure setup completed")
    return container
