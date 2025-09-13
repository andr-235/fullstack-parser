"""
API роутер для работы с VK пользователями
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.application.dto.vk_api_dto import VKUserDTO
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep
from vk_api.shared.presentation.exceptions.api_exceptions import (
    NotFoundError,
    ValidationError as APIValidationError,
    ServiceUnavailableError as APIServiceUnavailableError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["VK Users"])


@router.get(
    "/{user_id}",
    response_model=VKUserDTO,
    summary="Получить пользователя по ID",
    description="Получить информацию о VK пользователе по его ID"
)
async def get_user(
    user_id: int = Path(..., gt=0, description="ID пользователя VK"),
    vk_service: VKAPIServiceImpl = VKAPIServiceDep
) -> VKUserDTO:
    """Получить пользователя по ID"""
    try:
        user = await vk_service.get_user(user_id)
        
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        return user
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        raise APIServiceUnavailableError(f"Failed to get user: {e}")


@router.post(
    "/batch",
    response_model=List[VKUserDTO],
    summary="Получить пользователей по списку ID",
    description="Получить информацию о нескольких VK пользователях по списку ID"
)
async def get_users_by_ids(
    user_ids: List[int],
    vk_service: VKAPIServiceImpl = VKAPIServiceDep
) -> List[VKUserDTO]:
    """Получить пользователей по списку ID"""
    try:
        if not user_ids:
            return []
        
        if len(user_ids) > 100:
            raise APIValidationError("Maximum 100 user IDs allowed")
        
        users = await vk_service.get_users_by_ids(user_ids)
        
        return users
        
    except APIValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to get users by IDs: {e}")
        raise APIServiceUnavailableError(f"Failed to get users: {e}")
