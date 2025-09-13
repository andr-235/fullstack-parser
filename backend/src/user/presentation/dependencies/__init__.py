"""
Dependencies модуля User
"""

from .user_dependencies import (
    get_user_repository,
    get_password_service,
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)

__all__ = [
    "get_user_repository",
    "get_password_service",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
]
