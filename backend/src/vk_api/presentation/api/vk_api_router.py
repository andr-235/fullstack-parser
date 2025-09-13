"""
Главный роутер VK API модуля
"""

from fastapi import APIRouter

from vk_api.presentation.api.groups_router import router as groups_router
from vk_api.presentation.api.posts_router import router as posts_router
from vk_api.presentation.api.comments_router import router as comments_router
from vk_api.presentation.api.users_router import router as users_router

# Создаем главный роутер
router = APIRouter(prefix="/vk-api", tags=["VK API"])

# Подключаем подроутеры
router.include_router(groups_router)
router.include_router(posts_router)
router.include_router(comments_router)
router.include_router(users_router)
