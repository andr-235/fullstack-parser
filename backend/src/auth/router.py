"""
Роутер аутентификации
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.user.exceptions import UserInactiveError, UserAlreadyExistsError

from .dependencies import get_auth_service, get_current_user
from .exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
)
from .schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordConfirmRequest,
    ResetPasswordRequest,
    SuccessResponse,
)
from .services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limiting - используем глобальный limiter из main.py
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    from src.common.logging import get_logger
    logger = get_logger()
    logger.info(f"Register request received for email: {register_data.email}")
    
    try:
        result = await auth_service.register(register_data)
        logger.info(f"Registration successful for email: {register_data.email}")
        return result
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    except Exception as e:
        from src.common.logging import get_logger
        logger = get_logger()
        logger.error(f"Unexpected error in register endpoint: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Вход в систему"""
    from src.common.logging import get_logger
    logger = get_logger()
    logger.info(f"[AuthRouter] Login request received for email: {login_data.email}")
    logger.info(f"[AuthRouter] Request URL: {request.url}")
    logger.info(f"[AuthRouter] Request method: {request.method}")
    try:
        result = await auth_service.login(login_data)
        logger.info(f"[AuthRouter] Login successful for email: {login_data.email}")
        return result
    except InvalidCredentialsError:
        logger.warning(f"[AuthRouter] Invalid credentials for email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except UserInactiveError:
        logger.warning(f"[AuthRouter] User account inactive for email: {login_data.email}")
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
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.status == "active",
        "is_superuser": current_user.is_superuser
    }
