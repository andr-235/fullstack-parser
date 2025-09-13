"""
VK API Module - Simplified Implementation

Простой и эффективный модуль для работы с VK API
"""

from .client import VKAPIClient
from .service import VKAPIService
from .exceptions import VKAPIError

__all__ = [
    "VKAPIClient",
    "VKAPIService", 
    "VKAPIError",
]