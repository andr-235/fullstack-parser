"""
Сервис аутентификации
"""

from typing import Optional

from src.common.logging import get_logger
from src.user.exceptions import UserAlreadyExistsError, UserInactiveError

from ...domain import (
    IAuthenticationService,
    IUnitOfWork,
    ITokenService,
    IPasswordService,
    IEventService,
    ICacheService,
    User,
    UserStatus,
    SecurityEventType,
    TooManyLoginAttemptsError,
    InvalidCredentialsError,
)
from ...schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)


class AuthenticationService(IAuthenticationService):
    """Сервис аутентификации"""
    
    def __init__(
        self,
        unit_of_work: IUnitOfWork,
        token_service: ITokenService,
        password_service: IPasswordService,
        event_service: Optional[IEventService] = None,
        cache_service: Optional[ICacheService] = None,
        max_login_attempts: int = 5,
        login_attempts_ttl: int = 900
    ):
        self.unit_of_work = unit_of_work
        self.token_service = token_service
        self.password_service = password_service
        self.event_service = event_service
        self.cache_service = cache_service
        self.max_login_attempts = max_login_attempts
        self.login_attempts_ttl = login_attempts_ttl
        self.logger = get_logger()
    
    async def register(self, request: RegisterRequest) -> RegisterResponse:
        """Регистрация нового пользователя"""
        async with self.unit_of_work as uow:
            try:
                self.logger.info(f"Starting registration for email: {request.email}")
                
                # Проверяем, существует ли пользователь
                existing_user = await uow.users.get_by_email(request.email)
                if existing_user:
                    raise UserAlreadyExistsError(request.email)
                
                # Хешируем пароль
                hashed_password = await self.password_service.hash_password(request.password)
                
                # Создаем пользователя
                user_data = {
                    "email": request.email,
                    "full_name": request.full_name,
                    "hashed_password": hashed_password,
                    "status": UserStatus.ACTIVE.value,
                    "is_superuser": False,
                    "email_verified": False
                }
                
                self.logger.info(f"Creating user for email: {request.email}")
                user = await uow.users.create(user_data)
                await uow.commit()
                self.logger.info(f"User created successfully with ID: {user.id}")
                
            except Exception as e:
                await uow.rollback()
                self.logger.error(f"Error in register method: {e}")
                raise
        
        # Создаем токены
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser
        }
        
        access_token = await self.token_service.create_access_token(token_data)
        refresh_token = await self.token_service.create_refresh_token(token_data)
        
        # Кэшируем данные пользователя
        if self.cache_service:
            await self._cache_user_data(user)
        
        # Логируем событие
        if self.event_service:
            await self.event_service.log_security_event(
                SecurityEventType.USER_REGISTERED.value,
                str(user.id),
                {"email": user.email}
            )
        
        return RegisterResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 минут
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_superuser": user.is_superuser
            }
        )
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        """Вход в систему"""
        # Проверяем попытки входа
        await self._check_login_attempts(request.email)
        
        async with self.unit_of_work as uow:
            # Получаем пользователя
            user = await uow.users.get_by_email(request.email)
            
            # Защита от timing attacks
            if not user:
                await self._record_failed_login_attempt(request.email)
                raise InvalidCredentialsError()
            
            # Проверяем пароль
            is_valid = await self.password_service.verify_password(
                request.password, user.hashed_password
            )
            if not is_valid:
                await self._record_failed_login_attempt(request.email)
                raise InvalidCredentialsError()
            
            # Проверяем активность
            if user.status != UserStatus.ACTIVE.value:
                raise UserInactiveError(user.id)
            
            # Сбрасываем счетчик попыток
            await self._reset_login_attempts(request.email)
            
            # Создаем токены
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "is_superuser": user.is_superuser
            }
            
            access_token = await self.token_service.create_access_token(token_data)
            refresh_token = await self.token_service.create_refresh_token(token_data)
            
            # Кэшируем данные пользователя
            if self.cache_service:
                await self._cache_user_data(user)
            
            # Обновляем время последнего входа
            user.last_login = "now()"  # SQL функция
            await uow.users.update(user)
            await uow.commit()
            
            # Логируем событие
            if self.event_service:
                await self.event_service.log_security_event(
                    SecurityEventType.USER_LOGIN.value,
                    str(user.id),
                    {"email": user.email}
                )
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=30 * 60,  # 30 минут
                user={
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_superuser": user.is_superuser
                }
            )
    
    async def logout(self, refresh_token: Optional[str] = None) -> None:
        """Выход из системы"""
        try:
            if refresh_token:
                await self.token_service.revoke_token(refresh_token)
                
                # Логируем событие
                if self.event_service:
                    token_data = await self.token_service.validate_token(refresh_token)
                    if token_data:
                        await self.event_service.log_security_event(
                            SecurityEventType.USER_LOGOUT.value,
                            token_data.get("sub", "unknown"),
                            {"email": token_data.get("email", "unknown")}
                        )
        except Exception as e:
            self.logger.error(f"Error during logout: {e}")
    
    async def _check_login_attempts(self, email: str) -> None:
        """Проверить количество попыток входа"""
        if not self.cache_service:
            return
        
        attempts_key = f"login_attempts:{email}"
        attempts = await self.cache_service.get(attempts_key) or 0
        attempts = int(attempts) if attempts else 0
        
        if attempts >= self.max_login_attempts:
            self.logger.warning(f"Too many login attempts for {email}")
            raise TooManyLoginAttemptsError(email, attempts)
    
    async def _record_failed_login_attempt(self, email: str) -> None:
        """Записать неудачную попытку входа"""
        if not self.cache_service:
            return
        
        attempts_key = f"login_attempts:{email}"
        attempts = await self.cache_service.get(attempts_key) or 0
        attempts = int(attempts) if attempts else 0
        
        await self.cache_service.set(
            attempts_key, 
            attempts + 1, 
            ttl=self.login_attempts_ttl
        )
    
    async def _reset_login_attempts(self, email: str) -> None:
        """Сбросить счетчик попыток входа"""
        if not self.cache_service:
            return
        
        attempts_key = f"login_attempts:{email}"
        await self.cache_service.delete(attempts_key)
    
    async def _cache_user_data(self, user: User) -> None:
        """Кэшировать данные пользователя"""
        if not self.cache_service:
            return
        
        cache_key = f"user:{user.id}"
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.status == UserStatus.ACTIVE.value
        }
        await self.cache_service.set(cache_key, user_data)
