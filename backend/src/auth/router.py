"""
Роутер аутентификации - упрощенная версия
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.user.exceptions import UserInactiveError, UserAlreadyExistsError

from .dependencies import get_auth_service, get_current_user
from .exceptions import InvalidCredentialsError, InvalidTokenError, TokenExpiredError
from .schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    SuccessResponse,
)
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    try:
        return await auth_service.register(register_data)
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход в систему"""
    try:
        return await auth_service.login(login_data)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обновить access токен"""
    try:
        return await auth_service.refresh_token(refresh_data)
    except (InvalidTokenError, TokenExpiredError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Сменить пароль"""
    try:
        await auth_service.change_password(current_user, password_data)
        return SuccessResponse(message="Password changed successfully")
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Выход из системы"""
    await auth_service.logout(logout_data.refresh_token)
    return SuccessResponse(message="Logged out successfully")


@router.get("/me")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """Получить информацию о текущем пользователе"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.status == "active",
        "is_superuser": current_user.is_superuser
    }
