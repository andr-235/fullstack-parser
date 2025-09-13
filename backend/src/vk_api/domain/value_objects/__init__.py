"""
Domain Value Objects - VK API Module
"""

from vk_api.domain.value_objects.group_id import VKGroupID
from vk_api.domain.value_objects.post_id import VKPostID
from vk_api.domain.value_objects.user_id import VKUserID

__all__ = [
    "VKGroupID",
    "VKPostID",
    "VKUserID",
]
