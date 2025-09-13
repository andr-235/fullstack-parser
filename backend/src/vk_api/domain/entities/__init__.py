"""
Domain Entities - VK API Module
"""

from vk_api.domain.entities.vk_group import VKGroup
from vk_api.domain.entities.vk_post import VKPost
from vk_api.domain.entities.vk_comment import VKComment

__all__ = [
    "VKGroup",
    "VKPost",
    "VKComment",
]
