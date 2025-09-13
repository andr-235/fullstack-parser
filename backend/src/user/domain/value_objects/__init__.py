"""
Value objects модуля User
"""

from .user_id import UserId
from .user_status import UserStatus
# Email и Password перенесены в auth модуль

__all__ = [
    "UserId",
    "UserStatus",
]
