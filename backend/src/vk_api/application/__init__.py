"""
Application Layer - VK API Module

Содержит use cases, DTO, интерфейсы сервисов и бизнес-логику приложения.
"""

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

__all__ = [
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
]
