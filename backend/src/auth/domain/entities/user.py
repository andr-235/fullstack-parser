"""
Доменная сущность User

Представляет пользователя в доменной модели
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from auth.domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class User:
    """
    Доменная сущность пользователя
    
    Инкапсулирует бизнес-логику и правила пользователя
    """
    
    id: UserId
    email: Email
    full_name: str
    hashed_password: Password
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_sent_at: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_sent_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Валидация после инициализации"""
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        if self.updated_at is None:
            object.__setattr__(self, 'updated_at', datetime.utcnow())
    
    def is_locked(self) -> bool:
        """Проверить заблокирован ли аккаунт"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def can_login(self) -> bool:
        """Проверить может ли пользователь войти в систему"""
        return self.is_active and not self.is_locked()
    
    def increment_login_attempts(self) -> 'User':
        """Увеличить счетчик неудачных попыток входа"""
        from datetime import timedelta
        
        new_attempts = self.login_attempts + 1
        locked_until = None
        
        # Блокируем после 5 попыток на 15 минут
        if new_attempts >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            last_login=self.last_login,
            login_attempts=new_attempts,
            locked_until=locked_until,
            email_verified=self.email_verified,
            email_verification_token=self.email_verification_token,
            email_verification_sent_at=self.email_verification_sent_at,
            password_reset_token=self.password_reset_token,
            password_reset_sent_at=self.password_reset_sent_at,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
    
    def reset_login_attempts(self) -> 'User':
        """Сбросить счетчик неудачных попыток входа"""
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            last_login=self.last_login,
            login_attempts=0,
            locked_until=None,
            email_verified=self.email_verified,
            email_verification_token=self.email_verification_token,
            email_verification_sent_at=self.email_verification_sent_at,
            password_reset_token=self.password_reset_token,
            password_reset_sent_at=self.password_reset_sent_at,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
    
    def update_last_login(self) -> 'User':
        """Обновить время последнего входа"""
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            last_login=datetime.utcnow(),
            login_attempts=self.login_attempts,
            locked_until=self.locked_until,
            email_verified=self.email_verified,
            email_verification_token=self.email_verification_token,
            email_verification_sent_at=self.email_verification_sent_at,
            password_reset_token=self.password_reset_token,
            password_reset_sent_at=self.password_reset_sent_at,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
    
    def change_password(self, new_password: Password) -> 'User':
        """Изменить пароль"""
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=new_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            last_login=self.last_login,
            login_attempts=self.login_attempts,
            locked_until=self.locked_until,
            email_verified=self.email_verified,
            email_verification_token=self.email_verification_token,
            email_verification_sent_at=self.email_verification_sent_at,
            password_reset_token=self.password_reset_token,
            password_reset_sent_at=self.password_reset_sent_at,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
    
    def verify_email(self) -> 'User':
        """Подтвердить email"""
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            last_login=self.last_login,
            login_attempts=self.login_attempts,
            locked_until=self.locked_until,
            email_verified=True,
            email_verification_token=None,
            email_verification_sent_at=self.email_verification_sent_at,
            password_reset_token=self.password_reset_token,
            password_reset_sent_at=self.password_reset_sent_at,
            created_at=self.created_at,
            updated_at=datetime.utcnow()
        )
