"""
Роутер пользователей

Содержит эндпоинты для управления пользователями
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from user.presentation.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserResponse,
    UserListResponse,
    UserStatsResponse,
    PaginationParams,
)
from user.presentation.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_superuser,
    get_password_service,
    get_user_repository,
)
from user.domain.entities.user import User
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from user.domain.value_objects.user_id import UserId
from user.domain.value_objects.user_status import UserStatus
from user.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
)
from shared.infrastructure.logging import get_logger

# Роутер
user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    password_service = Depends(get_password_service),
    user_repository = Depends(get_user_repository)
):
    """
    Создать пользователя
    
    Args:
        user_data: Данные для создания пользователя
        password_service: Сервис паролей
        user_repository: Репозиторий пользователей
        
    Returns:
        UserResponse: Созданный пользователь
    """
    logger = get_logger()
    
    try:
        # Проверяем не существует ли пользователь
        existing_user = await user_repository.get_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsError(user_data.email)
        
        # Хешируем пароль
        hashed_password = await password_service.hash_password(user_data.password)
        
        # Создаем пользователя
        user = User(
            id=UserId(value=0),  # ID будет установлен БД
            email=Email(value=user_data.email),
            full_name=user_data.full_name,
            hashed_password=Password.create_from_hash(hashed_password),
            is_superuser=user_data.is_superuser
        )
        
        created_user = await user_repository.create(user)
        
        return UserResponse(
            id=created_user.id.value,
            email=created_user.email.value,
            full_name=created_user.full_name,
            status=created_user.status,
            is_superuser=created_user.is_superuser,
            email_verified=created_user.email_verified,
            last_login=created_user.last_login,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
        
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


@user_router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Получить информацию о текущем пользователе
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        UserResponse: Данные пользователя
    """
    return UserResponse(
        id=current_user.id.value,
        email=current_user.email.value,
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
    user_repository = Depends(get_user_repository)
):
    """
    Обновить информацию о текущем пользователе
    
    Args:
        user_data: Данные для обновления
        current_user: Текущий пользователь
        user_repository: Репозиторий пользователей
        
    Returns:
        UserResponse: Обновленный пользователь
    """
    logger = get_logger()
    
    try:
        # Проверяем email на уникальность если он изменился
        if user_data.email and user_data.email != current_user.email.value:
            existing_user = await user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
        
        # Обновляем пользователя
        updated_user = current_user.update_profile(
            full_name=user_data.full_name or current_user.full_name,
            email=Email(value=user_data.email) if user_data.email else current_user.email
        )
        
        saved_user = await user_repository.update(updated_user)
        
        return UserResponse(
            id=saved_user.id.value,
            email=saved_user.email.value,
            full_name=saved_user.full_name,
            status=saved_user.status,
            is_superuser=saved_user.is_superuser,
            email_verified=saved_user.email_verified,
            last_login=saved_user.last_login,
            created_at=saved_user.created_at,
            updated_at=saved_user.updated_at
        )
        
    except Exception as e:
        logger.error(f"Update user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/", response_model=UserListResponse)
async def get_users(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[UserStatus] = Query(None, description="Фильтр по статусу"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    current_user: User = Depends(get_current_superuser),
    user_repository = Depends(get_user_repository)
):
    """
    Получить список пользователей (только для суперпользователей)
    
    Args:
        pagination: Параметры пагинации
        status_filter: Фильтр по статусу
        search: Поисковый запрос
        current_user: Текущий суперпользователь
        user_repository: Репозиторий пользователей
        
    Returns:
        UserListResponse: Список пользователей
    """
    try:
        users, total = await user_repository.get_paginated(
            limit=pagination.limit,
            offset=pagination.offset,
            status=status_filter,
            search=search
        )
        
        user_responses = [
            UserResponse(
                id=user.id.value,
                email=user.email.value,
                full_name=user.full_name,
                status=user.status,
                is_superuser=user.is_superuser,
                email_verified=user.email_verified,
                last_login=user.last_login,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            has_next=pagination.offset + pagination.limit < total,
            has_prev=pagination.offset > 0
        )
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_superuser),
    user_repository = Depends(get_user_repository)
):
    """
    Получить статистику пользователей (только для суперпользователей)
    
    Args:
        current_user: Текущий суперпользователь
        user_repository: Репозиторий пользователей
        
    Returns:
        UserStatsResponse: Статистика пользователей
    """
    try:
        stats = await user_repository.get_stats()
        
        return UserStatsResponse(
            total_users=stats.get("total", 0),
            active_users=stats.get("active", 0),
            inactive_users=stats.get("inactive", 0),
            locked_users=stats.get("locked", 0),
            pending_verification=stats.get("pending_verification", 0),
            superusers=stats.get("superusers", 0)
        )
        
    except Exception as e:
        logger = get_logger()
        logger.error(f"Get user stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_superuser),
    user_repository = Depends(get_user_repository)
):
    """
    Получить пользователя по ID (только для суперпользователей)
    
    Args:
        user_id: ID пользователя
        current_user: Текущий суперпользователь
        user_repository: Репозиторий пользователей
        
    Returns:
        UserResponse: Данные пользователя
    """
    try:
        user = await user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        return UserResponse(
            id=user.id.value,
            email=user.email.value,
            full_name=user.full_name,
            status=user.status,
            is_superuser=user.is_superuser,
            email_verified=user.email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger = get_logger()
        logger.error(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
