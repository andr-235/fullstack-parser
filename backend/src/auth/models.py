"""
Модели для модуля Auth

Определяет репозиторий и модели для работы с пользователями
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db_session
from ..models import BaseModel


class UserModel(BaseModel):
    """
    SQLAlchemy модель пользователя

    Представляет пользователя в базе данных
    """

    __tablename__ = "users"

    # Основная информация
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(512), nullable=False)

    # Статусы и роли
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Дополнительные поля
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Email верификация
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(512), nullable=True)
    email_verification_sent_at = Column(DateTime, nullable=True)

    # Сброс пароля
    password_reset_token = Column(String(512), nullable=True)
    password_reset_sent_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<UserModel(id={self.id}, email='{self.email}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "last_login": self.last_login,
            "email_verified": self.email_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "login_attempts": self.login_attempts,
            "locked_until": self.locked_until,
        }

    def is_locked(self) -> bool:
        """Проверить заблокирован ли аккаунт"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def increment_login_attempts(self):
        """Увеличить счетчик неудачных попыток входа"""
        self.login_attempts = (self.login_attempts or 0) + 1

    def reset_login_attempts(self):
        """Сбросить счетчик неудачных попыток входа"""
        self.login_attempts = 0
        self.locked_until = None

    def lock_account(self, duration_minutes: int = 15):
        """Заблокировать аккаунт"""
        from datetime import timedelta

        self.locked_until = datetime.utcnow() + timedelta(
            minutes=duration_minutes
        )


class AuthToken:
    """
    Модель токена аутентификации

    Представляет JWT токен в памяти (для кеширования)
    """

    def __init__(
        self,
        token_hash: str,
        user_id: int,
        token_type: str,
        expires_at: datetime,
        created_at: Optional[datetime] = None,
    ):
        self.token_hash = token_hash
        self.user_id = user_id
        self.token_type = token_type
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()

    def is_expired(self) -> bool:
        """Проверить истек ли токен"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "token_hash": self.token_hash,
            "user_id": self.user_id,
            "token_type": self.token_type,
            "expires_at": self.expires_at,
            "created_at": self.created_at,
        }


class UserRepository:
    """
    Репозиторий для работы с пользователями

    Предоставляет интерфейс для хранения и получения пользователей
    """

    def __init__(self, db=None):
        self.db = db

    async def get_db(self):
        """Получить сессию БД"""
        return self.db or get_db_session()

    async def create(self, user_data: Dict[str, Any]) -> UserModel:
        """
        Создать нового пользователя

        Args:
            user_data: Данные пользователя

        Returns:
            UserModel: Созданный пользователь
        """
        db = await self.get_db()

        user = UserModel(
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=user_data["hashed_password"],
            is_active=user_data.get("is_active", True),
            is_superuser=user_data.get("is_superuser", False),
            email_verified=user_data.get("email_verified", False),
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """
        Получить пользователя по ID

        Args:
            user_id: ID пользователя

        Returns:
            Optional[UserModel]: Пользователь или None
        """
        db = await self.get_db()
        result = await db.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        """
        Получить пользователя по email

        Args:
            email: Email пользователя

        Returns:
            Optional[UserModel]: Пользователь или None
        """
        db = await self.get_db()
        result = await db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[UserModel]:
        """
        Получить всех пользователей

        Args:
            limit: Максимум пользователей
            offset: Смещение
            is_active: Фильтр по активности
            search: Поиск по email или имени

        Returns:
            List[UserModel]: Список пользователей
        """
        db = await self.get_db()
        query = select(UserModel)

        # Фильтры
        if is_active is not None:
            query = query.where(UserModel.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    UserModel.email.ilike(search_filter),
                    UserModel.full_name.ilike(search_filter),
                )
            )

        # Сортировка и пагинация
        query = (
            query.order_by(desc(UserModel.created_at))
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(query)
        return list(result.scalars().all())

    async def update(
        self, user_id: int, update_data: Dict[str, Any]
    ) -> UserModel:
        """
        Обновить пользователя

        Args:
            user_id: ID пользователя
            update_data: Данные для обновления

        Returns:
            UserModel: Обновленный пользователь
        """
        db = await self.get_db()

        # Получаем пользователя
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Обновляем поля
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(user)
        return user

    async def delete(self, user_id: int) -> bool:
        """
        Удалить пользователя

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если пользователь удален
        """
        db = await self.get_db()

        user = await self.get_by_id(user_id)
        if not user:
            return False

        await db.delete(user)
        await db.commit()
        return True

    async def update_last_login(self, user_id: int) -> bool:
        """
        Обновить время последнего входа

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если обновлено
        """
        return (
            await self.update(user_id, {"last_login": datetime.utcnow()})
            is not None
        )

    async def increment_login_attempts(
        self, user_id: int
    ) -> Optional[UserModel]:
        """
        Увеличить счетчик неудачных попыток входа

        Args:
            user_id: ID пользователя

        Returns:
            Optional[UserModel]: Обновленный пользователь
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        user.increment_login_attempts()
        await self.update(user_id, {"login_attempts": user.login_attempts})
        return user

    async def reset_login_attempts(self, user_id: int) -> bool:
        """
        Сбросить счетчик неудачных попыток входа

        Args:
            user_id: ID пользователя

        Returns:
            bool: True если сброшено
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.reset_login_attempts()
        update_data = {"login_attempts": 0, "locked_until": None}
        return await self.update(user_id, update_data) is not None

    async def get_stats(self) -> Dict[str, Any]:
        """
        Получить статистику пользователей

        Returns:
            Dict[str, Any]: Статистика
        """
        db = await self.get_db()

        # Общая статистика
        result = await db.execute(
            select(
                func.count(UserModel.id).label("total_users"),
                func.sum(
                    case((UserModel.is_active == True, 1), else_=0)
                ).label("active_users"),
                func.sum(
                    case((UserModel.is_superuser == True, 1), else_=0)
                ).label("superusers"),
                func.count(
                    case(
                        (
                            UserModel.created_at
                            >= datetime.utcnow().replace(
                                hour=0, minute=0, second=0, microsecond=0
                            ),
                            UserModel.id,
                        )
                    )
                ).label("new_users_today"),
            )
        )

        stats = result.first()
        if not stats:
            return {
                "total_users": 0,
                "active_users": 0,
                "superusers": 0,
                "new_users_today": 0,
                "new_users_week": 0,
            }

        # Новые пользователи за неделю
        week_ago = datetime.utcnow() - timedelta(days=7)
        result = await db.execute(
            select(func.count(UserModel.id)).where(
                UserModel.created_at >= week_ago
            )
        )
        new_users_week = result.scalar() or 0

        return {
            "total_users": stats.total_users or 0,
            "active_users": stats.active_users or 0,
            "superusers": stats.superusers or 0,
            "new_users_today": stats.new_users_today or 0,
            "new_users_week": new_users_week,
        }


# Функции для создания репозитория
async def get_user_repository(db=None) -> UserRepository:
    """Создать репозиторий пользователей"""
    return UserRepository(db)


# Импорты (для работы с БД)
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    DateTime,
    select,
    desc,
    or_,
    func,
    case,
)
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta


# Экспорт
__all__ = [
    "UserModel",
    "AuthToken",
    "UserRepository",
    "get_user_repository",
]
