"""
Инициализация модуля Auth в приложении
"""

from .setup import setup_auth


async def init_auth_module():
    """Инициализировать модуль аутентификации"""
    # Настраиваем auth модуль с None репозиторием
    # Репозиторий будет создаваться в dependencies
    setup_auth(
        user_repository=None,  # Будет создаваться в dependencies
        redis_url="redis://localhost:6379/0",  # TODO: вынести в конфиг
        secret_key="your-secret-key-change-in-production",  # TODO: вынести в конфиг
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=7,
        password_rounds=12
    )
