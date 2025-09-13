"""
Domain слой модуля User

Содержит бизнес-логику, сущности и value objects
"""

from .entities.user import User
from .value_objects import (
    Email,
    UserId,
    Password,
    UserStatus,
)

__all__ = [
    "User",
    "Email",
    "UserId", 
    "Password",
    "UserStatus",
]
