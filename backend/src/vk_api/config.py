"""
Конфигурация VK API
"""

import os
from typing import Optional


class VKAPIConfig:
    """Конфигурация VK API"""
    
    def __init__(self):
        self.access_token: Optional[str] = os.getenv("VK_API_ACCESS_TOKEN")
        self.version: str = os.getenv("VK_API_VERSION", "5.131")
        self.timeout: float = float(os.getenv("VK_API_TIMEOUT", "30.0"))


# Глобальная конфигурация
config = VKAPIConfig()

__all__ = ["VKAPIConfig", "config"]
