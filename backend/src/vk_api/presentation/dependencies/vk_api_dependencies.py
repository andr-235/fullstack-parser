"""
Зависимости для VK API модуля
"""

from typing import Annotated
from fastapi import Depends

from vk_api.application.interfaces.vk_api_service_interface import VKAPIServiceInterface
from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl
from vk_api.infrastructure.clients.vk_api_client_impl import VKAPIClientImpl
from shared.infrastructure.cache.redis_cache import RedisCache
from shared.presentation.dependencies.cache import get_cache


async def get_vk_api_client() -> VKAPIClientImpl:
    """Получить VK API клиент"""
    return VKAPIClientImpl()


async def get_vk_api_repository(
    vk_client: Annotated[VKAPIClientImpl, Depends(get_vk_api_client)],
    cache: Annotated[RedisCache, Depends(get_cache)]
) -> VKAPIRepositoryImpl:
    """Получить VK API репозиторий"""
    return VKAPIRepositoryImpl(
        vk_client=vk_client,
        cache=cache,
        cache_ttl=300  # 5 минут по умолчанию
    )


async def get_vk_api_service(
    repository: Annotated[VKAPIRepositoryImpl, Depends(get_vk_api_repository)]
) -> VKAPIServiceInterface:
    """Получить VK API сервис"""
    return VKAPIServiceImpl(repository=repository)


# Типизированные зависимости для использования в роутерах
VKAPIServiceDep = Annotated[VKAPIServiceImpl, Depends(get_vk_api_service)]
VKAPIRepositoryDep = Annotated[VKAPIRepositoryImpl, Depends(get_vk_api_repository)]
VKAPIClientDep = Annotated[VKAPIClientImpl, Depends(get_vk_api_client)]
