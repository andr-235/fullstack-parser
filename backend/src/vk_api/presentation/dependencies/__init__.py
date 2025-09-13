"""
Presentation Dependencies - VK API Module
"""

from vk_api.presentation.dependencies.vk_api_dependencies import (
    get_vk_api_service,
    get_vk_api_repository,
    get_vk_api_client,
    VKAPIServiceDep,
    VKAPIRepositoryDep,
    VKAPIClientDep,
)

__all__ = [
    "get_vk_api_service",
    "get_vk_api_repository",
    "get_vk_api_client",
    "VKAPIServiceDep",
    "VKAPIRepositoryDep",
    "VKAPIClientDep",
]
