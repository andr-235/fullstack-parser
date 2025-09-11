"""
DTO для пользователя

Data Transfer Object для передачи данных пользователя между слоями
"""

from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from auth.domain.entities.user import User


@dataclass
class UserDTO:
    """
    DTO для пользователя
    
    Представляет данные пользователя для передачи между слоями
    """
    
    id: int
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    email_verified: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserDTO':
        """
        Создать DTO из доменной сущности
        
        Args:
            user: Доменная сущность пользователя
            
        Returns:
            UserDTO: DTO пользователя
        """
        return cls(
            id=user.id.value,
            email=user.email.value,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            last_login=user.last_login,
            login_attempts=user.login_attempts,
            locked_until=user.locked_until,
            email_verified=user.email_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    
    def to_dict(self) -> dict:
        """
        Преобразовать в словарь
        
        Returns:
            dict: Словарь с данными пользователя
        """
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login,
            "login_attempts": self.login_attempts,
            "locked_until": self.locked_until,
            "email_verified": self.email_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
