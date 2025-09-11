"""
FastAPI роутер для модуля Auth (Clean Architecture)

Определяет API эндпоинты для аутентификации и управления пользователями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request, status

from auth.presentation.dependencies import get_register_user_use_case, get_current_user
from auth.presentation.schemas.user_schemas import (
    UserResponse,
    UserListResponse,
    UserCreate,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    TokenValidationResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    UserStats,
    RegisterRequest,
    RegisterResponse,
    ProfileUpdate,
)
from auth.application.use_cases.register_user import RegisterUserUseCase
from auth.application.dto.register_user_dto import RegisterUserDTO
from auth.application.dto.user_dto import UserDTO
from auth.shared.exceptions import (
    EmailAlreadyExistsError,
    ValidationError,
    UserNotFoundError,
    InvalidCredentialsError,
)
from src.pagination import (
    get_pagination_params,
    PaginationParams,
    create_paginated_response,
    PageParam,
    SizeParam,
    SearchParam,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создать новый аккаунт пользователя",
)
async def register(
    user_data: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> RegisterResponse:
    """Регистрация нового пользователя"""
    try:
        # Преобразуем Pydantic модель в DTO
        dto = RegisterUserDTO(
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password,
        )
        
        # Выполняем use case
        user_dto = await use_case.execute(dto)
        
        # Преобразуем DTO в Pydantic модель для ответа
        user_response = UserResponse(
            id=user_dto.id,
            email=user_dto.email,
            full_name=user_dto.full_name,
            is_active=user_dto.is_active,
            is_superuser=user_dto.is_superuser,
            last_login=user_dto.last_login,
            login_attempts=user_dto.login_attempts,
            locked_until=user_dto.locked_until,
            email_verified=user_dto.email_verified,
            created_at=user_dto.created_at,
            updated_at=user_dto.updated_at,
        )
        
        return RegisterResponse(
            user=user_response,
            message="Пользователь успешно зарегистрирован"
        )
        
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Аутентифицировать пользователя и получить JWT токены",
)
async def login(
    credentials: LoginRequest,
    # TODO: Добавить use case для логина
) -> TokenResponse:
    """Вход в систему"""
    # TODO: Реализовать с использованием Clean Architecture
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновить токены",
    description="Получить новые токены с помощью refresh токена",
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    # TODO: Добавить use case для refresh
) -> TokenResponse:
    """Обновить токены"""
    # TODO: Реализовать с использованием Clean Architecture
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Валидировать токен",
    description="Проверить валидность JWT токена",
)
async def validate_token(
    token: str = Query(..., description="JWT токен для валидации"),
    # TODO: Добавить use case для валидации
) -> TokenValidationResponse:
    """Валидировать токен"""
    # TODO: Реализовать с использованием Clean Architecture
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Получить информацию о текущем аутентифицированном пользователе",
)
async def get_current_user_info(
    current_user: UserDTO = Depends(get_current_user),
) -> UserResponse:
    """Получить текущего пользователя"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        last_login=current_user.last_login,
        login_attempts=current_user.login_attempts,
        locked_until=current_user.locked_until,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


# Остальные эндпоинты будут добавлены по мере реализации use cases
# TODO: Добавить остальные эндпоинты с использованием Clean Architecture

# Экспорт роутера
__all__ = ["router"]
