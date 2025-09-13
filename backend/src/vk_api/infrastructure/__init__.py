"""
Infrastructure Layer - VK API Module

Содержит реализации репозиториев, клиентов, адаптеров и внешних сервисов.
"""

from vk_api.infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl
from vk_api.infrastructure.clients.vk_api_client_impl import VKAPIClientImpl

__all__ = [
    "VKAPIRepositoryImpl",
    "VKAPIClientImpl",
]
