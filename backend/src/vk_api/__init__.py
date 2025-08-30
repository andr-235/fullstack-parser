"""
VK API Module - только для внутренних вызовов

Этот модуль предоставляет высокоуровневый интерфейс для работы с VK API.
Предназначен только для внутреннего использования в других модулях проекта.
"""

from .service import VKAPIService
from .dependencies import create_vk_api_service

__all__ = [
    # Основные компоненты
    "VKAPIService",
    "create_vk_api_service",
]
