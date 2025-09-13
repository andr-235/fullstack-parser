"""
Presentation API - VK API Module
"""

from vk_api.presentation.api.vk_api_router import router as vk_api_router
from vk_api.presentation.api.groups_router import router as groups_router
from vk_api.presentation.api.posts_router import router as posts_router
from vk_api.presentation.api.comments_router import router as comments_router
from vk_api.presentation.api.users_router import router as users_router

__all__ = [
    "vk_api_router",
    "groups_router",
    "posts_router",
    "comments_router",
    "users_router",
]
