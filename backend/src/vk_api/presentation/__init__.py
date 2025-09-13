"""
Presentation Layer - VK API Module

Содержит API роутеры, схемы, зависимости и обработчики запросов.
"""

from vk_api.presentation.api.vk_api_router import router as vk_api_router
from vk_api.presentation.dependencies.vk_api_dependencies import (
    get_vk_api_service,
    get_vk_api_repository,
    get_vk_api_client,
    VKAPIServiceDep,
    VKAPIRepositoryDep,
    VKAPIClientDep,
)
from vk_api.presentation.schemas.vk_api_schemas import (
    VKAPIHealthCheckResponse,
    VKAPIStatsResponse,
    VKAPIErrorResponse,
    VKAPIConfigResponse,
)

__all__ = [
    "vk_api_router",
    "get_vk_api_service",
    "get_vk_api_repository",
    "get_vk_api_client",
    "VKAPIServiceDep",
    "VKAPIRepositoryDep",
    "VKAPIClientDep",
    "VKAPIHealthCheckResponse",
    "VKAPIStatsResponse",
    "VKAPIErrorResponse",
    "VKAPIConfigResponse",
]
