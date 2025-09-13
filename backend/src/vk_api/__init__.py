"""
VK API Module - Clean Architecture Implementation

Этот модуль предоставляет высокоуровневый интерфейс для работы с VK API
с применением принципов Clean Architecture.

Архитектура:
- Domain Layer: Сущности, Value Objects, Репозитории, Доменные сервисы
- Application Layer: Use Cases, DTO, Интерфейсы сервисов
- Infrastructure Layer: Реализации репозиториев, клиентов, адаптеров
- Presentation Layer: API роутеры, схемы, зависимости

Основные компоненты:
- VKAPIService: Основной сервис для работы с VK API
- VKAPIRepository: Репозиторий для кеширования и работы с данными
- VKAPIClient: HTTP клиент для VK API
- API роутеры: REST API эндпоинты

Примеры использования:

    # 1. Использование через зависимости FastAPI (рекомендуемый способ)
    from fastapi import Depends
    from .presentation.dependencies.vk_api_dependencies import VKAPIServiceDep

    async def my_endpoint(vk_service: VKAPIServiceInterface = VKAPIServiceDep):
        group = await vk_service.get_group(12345)
        return group

    # 2. Прямое создание сервиса
    from .application.services.vk_api_service_impl import VKAPIServiceImpl
    from .infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl
    from .infrastructure.clients.vk_api_client_impl import VKAPIClientImpl

    vk_client = VKAPIClientImpl()
    repository = VKAPIRepositoryImpl(vk_client, cache)
    service = VKAPIServiceImpl(repository)

    # 3. Использование API роутеров
    from .presentation.api.vk_api_router import router as vk_api_router
    app.include_router(vk_api_router)

Автор: AI Assistant
Версия: 3.0 (Clean Architecture)
Дата: 2025
"""

# Domain Layer
from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID
from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.services.vk_api_domain_service import VKAPIDomainService

# Application Layer
from vk_api.application.interfaces.vk_api_service_interface import VKAPIServiceInterface
from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.application.dto.vk_api_dto import (
    VKGroupDTO,
    VKPostDTO,
    VKCommentDTO,
    VKUserDTO,
    VKGroupWithPostsDTO,
    VKPostWithCommentsDTO,
    VKGroupAnalyticsDTO,
    VKSearchGroupsRequestDTO,
    VKGetGroupPostsRequestDTO,
    VKGetPostCommentsRequestDTO,
)

# Infrastructure Layer
from vk_api.infrastructure.repositories.vk_api_repository_impl import VKAPIRepositoryImpl
from vk_api.infrastructure.clients.vk_api_client_impl import VKAPIClientImpl

# Presentation Layer
from vk_api.presentation.api.vk_api_router import router as vk_api_router
from vk_api.presentation.dependencies.vk_api_dependencies import (
    get_vk_api_service,
    get_vk_api_repository,
    get_vk_api_client,
    VKAPIServiceDep,
    VKAPIRepositoryDep,
    VKAPIClientDep,
)

# Backward compatibility (deprecated)
from vk_api.dependencies import create_vk_api_service as _create_vk_api_service

# Deprecated - используйте VKAPIServiceDep вместо этого
def create_vk_api_service():
    """Deprecated: используйте VKAPIServiceDep для внедрения зависимостей"""
    import warnings
    warnings.warn(
        "create_vk_api_service is deprecated. Use VKAPIServiceDep for dependency injection.",
        DeprecationWarning,
        stacklevel=2
    )
    return _create_vk_api_service()


__all__ = [
    # Domain Layer
    "VKGroup",
    "VKPost", 
    "VKComment",
    "VKGroupID",
    "VKPostID",
    "VKUserID",
    "VKAPIRepositoryInterface",
    "VKAPIDomainService",
    
    # Application Layer
    "VKAPIServiceInterface",
    "VKAPIServiceImpl",
    "VKGroupDTO",
    "VKPostDTO",
    "VKCommentDTO",
    "VKUserDTO",
    "VKGroupWithPostsDTO",
    "VKPostWithCommentsDTO",
    "VKGroupAnalyticsDTO",
    "VKSearchGroupsRequestDTO",
    "VKGetGroupPostsRequestDTO",
    "VKGetPostCommentsRequestDTO",
    
    # Infrastructure Layer
    "VKAPIRepositoryImpl",
    "VKAPIClientImpl",
    
    # Presentation Layer
    "vk_api_router",
    "get_vk_api_service",
    "get_vk_api_repository", 
    "get_vk_api_client",
    "VKAPIServiceDep",
    "VKAPIRepositoryDep",
    "VKAPIClientDep",
    
    # Backward compatibility
    "create_vk_api_service",
]