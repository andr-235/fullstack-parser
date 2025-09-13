"""
DI контейнер модуля User
"""

from .container import (
    UserContainer,
    get_container,
    set_container,
    get_user_service,
    get_create_user_use_case,
    get_get_user_use_case,
    get_update_user_use_case,
    get_get_users_list_use_case,
    get_get_user_stats_use_case,
)

__all__ = [
    "UserContainer",
    "get_container",
    "set_container",
    "get_user_service",
    "get_create_user_use_case",
    "get_get_user_use_case",
    "get_update_user_use_case",
    "get_get_users_list_use_case",
    "get_get_user_stats_use_case",
]
