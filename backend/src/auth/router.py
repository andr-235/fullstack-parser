"""
Роутер аутентификации
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    ChangePasswordRequest, ResetPasswordRequest, ResetPasswordConfirmRequest,
    LogoutRequest, SuccessResponse
)
from .dependencies import get_current_user, get_auth_service
from .services import AuthService
from .exceptions import InvalidCredentialsError, InvalidTokenError, TokenExpiredError
from user.domain.exceptions import UserInactiveError
from shared.infrastructure.logging import get_logger_with_correlation

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limiting
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
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


@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Запросить сброс пароля"""
    await auth_service.reset_password(reset_data)
    return SuccessResponse(message="Password reset email sent if account exists")


@router.post("/reset-password/confirm")
async def reset_password_confirm(
    confirm_data: ResetPasswordConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Подтвердить сброс пароля"""
    try:
        await auth_service.reset_password_confirm(confirm_data)
        return SuccessResponse(message="Password reset successfully")
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
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
        "id": current_user.id.value,
        "email": current_user.email.value,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser
    }
