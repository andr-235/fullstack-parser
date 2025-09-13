"""
Use Cases - VK API Module
"""

from vk_api.application.use_cases.get_group_use_case import GetGroupUseCase
from vk_api.application.use_cases.search_groups_use_case import SearchGroupsUseCase
from vk_api.application.use_cases.get_group_posts_use_case import GetGroupPostsUseCase
from vk_api.application.use_cases.get_post_comments_use_case import GetPostCommentsUseCase

__all__ = [
    "GetGroupUseCase",
    "SearchGroupsUseCase",
    "GetGroupPostsUseCase",
    "GetPostCommentsUseCase",
]
