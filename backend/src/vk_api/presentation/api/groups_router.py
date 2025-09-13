"""
API роутер для работы с VK группами
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from vk_api.application.services.vk_api_service_impl import VKAPIServiceImpl
from vk_api.application.dto.vk_api_dto import (
    VKGroupDTO,
    VKSearchGroupsRequestDTO,
    VKGroupsResponseDTO
)
from vk_api.presentation.dependencies.vk_api_dependencies import VKAPIServiceDep
from shared.presentation.responses.response_utils import PaginationParams
from shared.presentation.exceptions import (
    NotFoundException as NotFoundError,
    ValidationException as APIValidationError,
    InternalServerException as APIServiceUnavailableError
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/groups", tags=["VK Groups"])


@router.get(
    "/{group_id}",
    response_model=VKGroupDTO,
    summary="Получить группу по ID",
    description="Получить информацию о VK группе по её ID"
)
async def get_group(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    vk_service = VKAPIServiceDep
) -> VKGroupDTO:
    """Получить группу по ID"""
    try:
        group = await vk_service.get_group(group_id)
        
        if not group:
            raise NotFoundError(f"Group with ID {group_id} not found")
        
        return group
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get group {group_id}: {e}")
        raise APIServiceUnavailableError(f"Failed to get group: {e}")


@router.get(
    "/search",
    response_model=VKGroupsResponseDTO,
    summary="Поиск групп",
    description="Поиск VK групп по запросу"
)
async def search_groups(
    query: str = Query(..., min_length=2, max_length=100, description="Поисковый запрос"),
    count: int = Query(default=20, ge=1, le=1000, description="Количество результатов"),
    offset: int = Query(default=0, ge=0, description="Смещение"),
    vk_service = VKAPIServiceDep
) -> VKGroupsResponseDTO:
    """Поиск групп"""
    try:
        request = VKSearchGroupsRequestDTO(
            query=query,
            count=count,
            offset=offset
        )
        
        groups = await vk_service.search_groups(request)
        
        return VKGroupsResponseDTO(
            items=groups,
            total=len(groups),
            page=offset // count + 1,
            size=count,
            pages=(len(groups) + count - 1) // count
        )
        
    except Exception as e:
        logger.error(f"Failed to search groups: {e}")
        raise APIServiceUnavailableError(f"Failed to search groups: {e}")


@router.post(
    "/batch",
    response_model=List[VKGroupDTO],
    summary="Получить группы по списку ID",
    description="Получить информацию о нескольких VK группах по списку ID"
)
async def get_groups_by_ids(
    group_ids: List[int],
    vk_service = VKAPIServiceDep
) -> List[VKGroupDTO]:
    """Получить группы по списку ID"""
    try:
        if not group_ids:
            return []
        
        if len(group_ids) > 100:
            raise APIValidationError("Maximum 100 group IDs allowed")
        
        groups = await vk_service.get_groups_by_ids(group_ids)
        
        return groups
        
    except APIValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to get groups by IDs: {e}")
        raise APIServiceUnavailableError(f"Failed to get groups: {e}")


@router.get(
    "/{group_id}/analytics",
    response_model=dict,
    summary="Получить аналитику группы",
    description="Получить аналитику VK группы за указанный период"
)
async def get_group_analytics(
    group_id: int = Path(..., gt=0, description="ID группы VK"),
    days: int = Query(default=7, ge=1, le=365, description="Период анализа в днях"),
    vk_service = VKAPIServiceDep
) -> dict:
    """Получить аналитику группы"""
    try:
        analytics = await vk_service.get_group_analytics(group_id, days)
        
        if not analytics:
            raise NotFoundError(f"Group with ID {group_id} not found or no data available")
        
        return analytics.model_dump()
        
    except NotFoundError:
        raise
    except Exception as e:
        logger.error(f"Failed to get group analytics: {e}")
        raise APIServiceUnavailableError(f"Failed to get group analytics: {e}")
