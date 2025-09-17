"""
Доменные сущности аутентификации
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class UserStatus(Enum):
    """Статусы пользователя"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"


class TokenType(Enum):
    """Типы токенов"""
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


class SecurityEventType(Enum):
    """Типы событий безопасности"""
    USER_REGISTERED = "user_registered"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"


@dataclass
class User:
    """Доменная сущность пользователя"""
    id: int
    email: str
    full_name: str
    hashed_password: str
    status: UserStatus
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    email_verified: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def is_active(self) -> bool:
        """Проверить, активен ли пользователь"""
        return self.status == UserStatus.ACTIVE
    
    def is_locked(self) -> bool:
        """Проверить, заблокирован ли пользователь"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def can_login(self) -> bool:
        """Проверить, может ли пользователь войти в систему"""
        return self.is_active() and not self.is_locked()


@dataclass
class TokenData:
    """Данные токена"""
    sub: str
    email: str
    is_superuser: bool
    type: TokenType
    exp: datetime
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenData':
        """Создать из словаря"""
        return cls(
            sub=data.get("sub", ""),
            email=data.get("email", ""),
            is_superuser=data.get("is_superuser", False),
            type=TokenType(data.get("type", "access")),
            exp=datetime.fromtimestamp(data.get("exp", 0))
        )


@dataclass
class SecurityEvent:
    """Событие безопасности"""
    event_type: SecurityEventType
    user_id: str
    metadata: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class LoginAttempt:
    """Попытка входа"""
    email: str
    attempts: int
    locked_until: Optional[datetime] = None
    last_attempt: datetime = None
    
    def __post_init__(self):
        if self.last_attempt is None:
            self.last_attempt = datetime.utcnow()
    
    def is_locked(self) -> bool:
        """Проверить, заблокированы ли попытки входа"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
