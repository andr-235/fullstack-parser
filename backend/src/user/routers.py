"""
FastAPI роутеры для пользователей
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from .schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListRequest,
    UserListResponse,
    UserStatsResponse,
)
from .services import UserService
from .dependencies import (
    get_user_service,
    get_current_user,
    get_current_active_user,
    get_current_superuser,
)
from .exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    UserInactiveError,
)
from .models import User
from shared.infrastructure.logging import get_logger

# Роутер
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(get_user_service)
):
    """Создать пользователя"""
    logger = get_logger()
    
    try:
        return await user_service.create_user(user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Получить пользователя по ID"""
    logger = get_logger()
    
    try:
        return await user_service.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Получить данные текущего пользователя"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        status=current_user.status,
        is_superuser=current_user.is_superuser,
        email_verified=current_user.email_verified,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@user_router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить профиль текущего пользователя"""
    logger = get_logger()
    
    try:
        return await user_service.update_user(current_user.id, user_data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/", response_model=UserListResponse)
async def get_users_list(
    limit: int = Query(default=50, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(default=0, ge=0, description="Смещение"),
    status: Optional[str] = Query(default=None, description="Фильтр по статусу"),
    search: Optional[str] = Query(default=None, max_length=100, description="Поисковый запрос"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_superuser)
):
    """Получить список пользователей (только для суперпользователей)"""
    logger = get_logger()
    
    try:
        request = UserListRequest(
            limit=limit,
            offset=offset,
            status=status,
            search=search
        )
        return await user_service.get_users_list(request)
    except Exception as e:
        logger.error(f"Get users list error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_superuser)
):
    """Получить статистику пользователей (только для суперпользователей)"""
    logger = get_logger()
    
    try:
        return await user_service.get_user_stats()
    except Exception as e:
        logger.error(f"Get user stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_superuser)
):
    """Удалить пользователя (только для суперпользователей)"""
    logger = get_logger()
    
    try:
        deleted = await user_service.delete_user(user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
