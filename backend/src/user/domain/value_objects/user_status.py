"""
Enum для статуса пользователя

Инкапсулирует логику работы со статусами пользователей
"""

from enum import Enum


class UserStatus(str, Enum):
    """Статусы пользователя"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"

    def is_active(self) -> bool:
        """Проверить активен ли пользователь"""
        return self == UserStatus.ACTIVE

    def is_locked(self) -> bool:
        """Проверить заблокирован ли пользователь"""
        return self == UserStatus.LOCKED

    def can_login(self) -> bool:
        """Проверить может ли пользователь войти"""
        return self == UserStatus.ACTIVE
