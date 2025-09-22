"""
VK API Module - Simplified Implementation

Простой и эффективный модуль для работы с VK API
"""

from .client import VKAPIClient
from .exceptions import VKAPIError
from .service import VKAPIService

__all__ = [
    "VKAPIClient",
    "VKAPIService",
    "VKAPIError",
]
