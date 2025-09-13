"""
Domain Entity для пользователя

Содержит бизнес-логику пользователя
"""

from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from user.domain.value_objects.user_id import UserId
from user.domain.value_objects.user_status import UserStatus


class User(BaseModel):
    """Пользователь - основная domain entity"""

    id: UserId
    email: Email
    full_name: str
    hashed_password: Password
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def is_locked(self) -> bool:
        """Проверить заблокирован ли аккаунт"""
        return (
            self.locked_until and
            self.locked_until > datetime.utcnow()
        )

    def can_login(self) -> bool:
        """Проверить может ли пользователь войти"""
        return (
            self.status.can_login() and
            not self.is_locked()
        )

    def _copy(self, **kwargs) -> 'User':
        """Создать копию пользователя с изменениями"""
        return User(
            id=kwargs.get('id', self.id),
            email=kwargs.get('email', self.email),
            full_name=kwargs.get('full_name', self.full_name),
            hashed_password=kwargs.get('hashed_password', self.hashed_password),
            status=kwargs.get('status', self.status),
            is_superuser=kwargs.get('is_superuser', self.is_superuser),
            last_login=kwargs.get('last_login', self.last_login),
            login_attempts=kwargs.get('login_attempts', self.login_attempts),
            locked_until=kwargs.get('locked_until', self.locked_until),
            email_verified=kwargs.get('email_verified', self.email_verified),
            created_at=kwargs.get('created_at', self.created_at),
            updated_at=kwargs.get('updated_at', datetime.utcnow())
        )

    def increment_login_attempts(self) -> 'User':
        """Создать копию с увеличенным счетчиком попыток"""
        new_attempts = self.login_attempts + 1
        locked_until = None
        new_status = self.status

        # Блокировка после 5 попыток
        if new_attempts >= 5:
            locked_until = datetime.utcnow() + timedelta(minutes=15)
            new_status = UserStatus.LOCKED

        return self._copy(
            status=new_status,
            login_attempts=new_attempts,
            locked_until=locked_until
        )

    def reset_login_attempts(self) -> 'User':
        """Создать копию со сброшенными попытками"""
        return self._copy(
            status=UserStatus.ACTIVE,
            login_attempts=0,
            locked_until=None
        )

    def update_login_time(self) -> 'User':
        """Создать копию с обновленным временем входа"""
        return self._copy(
            last_login=datetime.utcnow(),
            login_attempts=0,
            locked_until=None
        )

    def change_password(self, new_hashed_password: str) -> 'User':
        """Создать копию с новым паролем"""
        return self._copy(
            hashed_password=Password.create_from_hash(new_hashed_password)
        )

    def update_profile(self, full_name: str, email: Email) -> 'User':
        """Создать копию с обновленным профилем"""
        return self._copy(
            email=email,
            full_name=full_name
        )

    class Config:
        frozen = True
