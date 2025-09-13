"""
Модуль пользователей

Предоставляет функциональность управления пользователями
"""

# Импорты для внешнего использования
from user.presentation.routers import user_router

# Импорты application слоя
from user.application import (
    UserService,
    CreateUserUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
    GetUsersListUseCase,
    GetUserStatsUseCase,
)

# Импорты DI контейнера
from user.infrastructure.di import (
    UserContainer,
    get_user_service,
    get_create_user_use_case,
    get_get_user_use_case,
    get_update_user_use_case,
    get_get_users_list_use_case,
    get_get_user_stats_use_case,
)

# Экспорт
__all__ = [
    # Router
    "user_router",
    # Service
    "UserService",
    # Use Cases
    "CreateUserUseCase",
    "GetUserUseCase",
    "UpdateUserUseCase",
    "GetUsersListUseCase",
    "GetUserStatsUseCase",
    # DI Container
    "UserContainer",
    "get_user_service",
    "get_create_user_use_case",
    "get_get_user_use_case",
    "get_update_user_use_case",
    "get_get_users_list_use_case",
    "get_get_user_stats_use_case",
]
