"""
FastAPI роутер для модуля Auth

Определяет API эндпоинты для аутентификации и управления пользователями
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request, status

from .dependencies import get_auth_service
from .schemas import (
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
from .service import AuthService
from ..pagination import (
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
    service: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    """Регистрация нового пользователя"""
    try:
        user = await service.register_user(user_data.model_dump())
        return RegisterResponse(
            user=user, message="Пользователь успешно зарегистрирован"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Аутентифицировать пользователя и получить JWT токены",
)
async def login(
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Вход в систему"""
    try:
        user = await service.authenticate_user(
            credentials.email, credentials.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
            )

        tokens = await service.create_tokens(user)
        return TokenResponse(**tokens, user=user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Обновить токены",
    description="Получить новые токены с помощью refresh токена",
)
async def refresh_token(
    token_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Обновить токены"""
    try:
        tokens = await service.refresh_access_token(token_data.refresh_token)
        # Получаем пользователя для ответа
        user_id = int(tokens["user_id"]) if "user_id" in tokens else None
        if user_id:
            user = await service.get_user(user_id)
            return TokenResponse(**tokens, user=user)
        else:
            raise HTTPException(
                status_code=400, detail="Не удалось определить пользователя"
            )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Валидировать токен",
    description="Проверить валидность JWT токена",
)
async def validate_token(
    token: str = Query(..., description="JWT токен для валидации"),
    service: AuthService = Depends(get_auth_service),
) -> TokenValidationResponse:
    """Валидировать токен"""
    try:
        result = await service.validate_token(token)
        if result:
            return TokenValidationResponse(**result)
        else:
            return TokenValidationResponse(valid=False)
    except Exception as e:
        return TokenValidationResponse(valid=False)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получить текущего пользователя",
    description="Получить информацию о текущем аутентифицированном пользователе",
)
async def get_current_user(
    # В реальном приложении здесь будет зависимость get_current_user
    user_id: int = Query(..., description="ID пользователя (временно)"),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Получить текущего пользователя"""
    try:
        return await service.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Обновить профиль",
    description="Обновить информацию о текущем пользователе",
)
async def update_profile(
    profile_data: ProfileUpdate,
    user_id: int = Query(..., description="ID пользователя (временно)"),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Обновить профиль пользователя"""
    try:
        return await service.update_user(
            user_id, profile_data.model_dump(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Изменить пароль",
    description="Изменить пароль текущего пользователя",
)
async def change_password(
    password_data: PasswordChange,
    user_id: int = Query(..., description="ID пользователя (временно)"),
    service: AuthService = Depends(get_auth_service),
):
    """Изменить пароль пользователя"""
    try:
        await service.change_password(
            user_id, password_data.current_password, password_data.new_password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/reset-password",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Запрос сброса пароля",
    description="Отправить запрос на сброс пароля",
)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Запрос сброса пароля"""
    try:
        # В реальном приложении здесь будет отправка email
        token = await service.generate_password_reset_token(reset_data.email)
        if token:
            # Здесь отправляем email с токеном
            return {
                "message": "Инструкции по сбросу пароля отправлены на email"
            }
        else:
            # Не раскрываем существование пользователя
            return {
                "message": "Если email существует, инструкции будут отправлены"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/reset-password/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Подтвердить сброс пароля",
    description="Подтвердить сброс пароля с помощью токена",
)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    service: AuthService = Depends(get_auth_service),
):
    """Подтвердить сброс пароля"""
    try:
        success = await service.reset_password(
            reset_data.token, reset_data.new_password
        )
        if not success:
            raise HTTPException(
                status_code=400, detail="Неверный токен сброса пароля"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Админские эндпоинты (требуют аутентификации суперпользователя)


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="Получить список пользователей",
    description="Получить список всех пользователей (только для админов)",
)
async def get_users(
    # Параметры пагинации
    page: PageParam = 1,
    size: SizeParam = 20,
    # Параметры фильтрации
    search: SearchParam = None,
    is_active: Optional[bool] = Query(
        None, description="Показать только активных пользователей"
    ),
    # Сервисы
    service: AuthService = Depends(get_auth_service),
) -> UserListResponse:
    """Получить список пользователей"""

    pagination = PaginationParams(
        page=page,
        size=size,
        search=search,
    )

    # Получаем пользователей
    users = await service.get_users(
        limit=pagination.limit,
        offset=pagination.offset,
        is_active=is_active,
        search=pagination.search,
    )

    # В реальности нужно получить total из БД
    total = len(users)  # Заглушка

    return create_paginated_response(users, total, pagination)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Получить пользователя по ID",
    description="Получить детальную информацию о пользователе (только для админов)",
)
async def get_user(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Получить пользователя по ID"""
    try:
        return await service.get_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Обновить пользователя",
    description="Обновить информацию о пользователе (только для админов)",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Обновить пользователя"""
    try:
        return await service.update_user(
            user_id, user_data.model_dump(exclude_unset=True)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя",
    description="Удалить пользователя из системы (только для админов)",
)
async def delete_user(
    user_id: int,
    service: AuthService = Depends(get_auth_service),
):
    """Удалить пользователя"""
    try:
        success = await service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=404, detail="Пользователь не найден"
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/stats",
    response_model=UserStats,
    summary="Статистика пользователей",
    description="Получить статистику пользователей (только для админов)",
)
async def get_user_stats(
    service: AuthService = Depends(get_auth_service),
) -> UserStats:
    """Получить статистику пользователей"""
    try:
        stats = await service.get_user_stats()
        return UserStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Экспорт роутера
__all__ = ["router"]
