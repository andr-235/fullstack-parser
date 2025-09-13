"""
Domain Layer - VK API Module

Содержит доменную логику, сущности, value objects и интерфейсы репозиториев.
"""

from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment
from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID
from vk_api.domain.repositories.vk_api_repository import VKAPIRepositoryInterface
from vk_api.domain.services.vk_api_domain_service import VKAPIDomainService

__all__ = [
    "VKGroup",
    "VKPost",
    "VKComment",
    "VKGroupID",
    "VKPostID",
    "VKUserID",
    "VKAPIRepositoryInterface",
    "VKAPIDomainService",
]
