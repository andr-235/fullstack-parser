"""
SQLAlchemy реализация репозитория пользователей

Реализует интерфейс UserRepositoryInterface с использованием SQLAlchemy
"""

from typing import List, Optional
from sqlalchemy import select, func, case, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from auth.domain.entities.user import User
from auth.domain.value_objects.user_id import UserId
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from auth.application.interfaces.user_repository import UserRepositoryInterface
# Импортируем UserModel из старого модуля auth
import sys
import os
# Добавляем путь к src в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', '..', '..', '..')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from auth.models import UserModel as SQLUserModel


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """
    SQLAlchemy реализация репозитория пользователей
    
    Реализует интерфейс UserRepositoryInterface с использованием SQLAlchemy
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.db_session.execute(
            select(SQLUserModel).where(SQLUserModel.id == user_id.value)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return self._model_to_entity(user_model)
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.db_session.execute(
            select(SQLUserModel).where(SQLUserModel.email == email.value)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return self._model_to_entity(user_model)
    
    async def save(self, user: User) -> User:
        """Сохранить пользователя"""
        if user.id.value == 0:
            # Создание нового пользователя
            user_model = SQLUserModel(
                email=user.email.value,
                full_name=user.full_name,
                hashed_password=user.hashed_password.hashed_value,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                login_attempts=user.login_attempts,
                locked_until=user.locked_until,
                email_verified=user.email_verified,
                email_verification_token=user.email_verification_token,
                email_verification_sent_at=user.email_verification_sent_at,
                password_reset_token=user.password_reset_token,
                password_reset_sent_at=user.password_reset_sent_at,
            )
            
            self.db_session.add(user_model)
            await self.db_session.commit()
            await self.db_session.refresh(user_model)
            
            # Обновляем ID в сущности
            return User(
                id=UserId(user_model.id),
                email=user.email,
                full_name=user.full_name,
                hashed_password=user.hashed_password,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                last_login=user.last_login,
                login_attempts=user.login_attempts,
                locked_until=user.locked_until,
                email_verified=user.email_verified,
                email_verification_token=user.email_verification_token,
                email_verification_sent_at=user.email_verification_sent_at,
                password_reset_token=user.password_reset_token,
                password_reset_sent_at=user.password_reset_sent_at,
                created_at=user_model.created_at,
                updated_at=user_model.updated_at,
            )
        else:
            # Обновление существующего пользователя
            result = await self.db_session.execute(
                select(SQLUserModel).where(SQLUserModel.id == user.id.value)
            )
            user_model = result.scalar_one_or_none()
            
            if not user_model:
                raise ValueError(f"User with id {user.id.value} not found")
            
            # Обновляем поля
            user_model.email = user.email.value
            user_model.full_name = user.full_name
            user_model.hashed_password = user.hashed_password.hashed_value
            user_model.is_active = user.is_active
            user_model.is_superuser = user.is_superuser
            user_model.last_login = user.last_login
            user_model.login_attempts = user.login_attempts
            user_model.locked_until = user.locked_until
            user_model.email_verified = user.email_verified
            user_model.email_verification_token = user.email_verification_token
            user_model.email_verification_sent_at = user.email_verification_sent_at
            user_model.password_reset_token = user.password_reset_token
            user_model.password_reset_sent_at = user.password_reset_sent_at
            user_model.updated_at = datetime.utcnow()
            
            await self.db_session.commit()
            await self.db_session.refresh(user_model)
            
            return self._model_to_entity(user_model)
    
    async def delete(self, user_id: UserId) -> bool:
        """Удалить пользователя"""
        result = await self.db_session.execute(
            select(SQLUserModel).where(SQLUserModel.id == user_id.value)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return False
        
        await self.db_session.delete(user_model)
        await self.db_session.commit()
        return True
    
    async def get_all(
        self,
        limit: int = 50,
        offset: int = 0,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[User]:
        """Получить список пользователей"""
        query = select(SQLUserModel)
        
        # Фильтры
        if is_active is not None:
            query = query.where(SQLUserModel.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    SQLUserModel.email.ilike(search_filter),
                    SQLUserModel.full_name.ilike(search_filter),
                )
            )
        
        # Сортировка и пагинация
        query = (
            query.order_by(desc(SQLUserModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.db_session.execute(query)
        user_models = result.scalars().all()
        
        return [self._model_to_entity(user_model) for user_model in user_models]
    
    async def exists_by_email(self, email: Email) -> bool:
        """Проверить существование пользователя по email"""
        result = await self.db_session.execute(
            select(func.count(SQLUserModel.id)).where(SQLUserModel.email == email.value)
        )
        count = result.scalar()
        return count > 0
    
    async def get_user_stats(self) -> dict:
        """Получить статистику пользователей"""
        # Общая статистика
        result = await self.db_session.execute(
            select(
                func.count(SQLUserModel.id).label("total_users"),
                func.sum(
                    case((SQLUserModel.is_active == True, 1), else_=0)
                ).label("active_users"),
                func.sum(
                    case((SQLUserModel.is_superuser == True, 1), else_=0)
                ).label("superusers"),
                func.count(
                    case(
                        (
                            SQLUserModel.created_at
                            >= datetime.utcnow().replace(
                                hour=0, minute=0, second=0, microsecond=0
                            ),
                            SQLUserModel.id,
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
        result = await self.db_session.execute(
            select(func.count(SQLUserModel.id)).where(
                SQLUserModel.created_at >= week_ago
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
    
    def _model_to_entity(self, user_model: SQLUserModel) -> User:
        """Преобразовать SQLAlchemy модель в доменную сущность"""
        return User(
            id=UserId(user_model.id),
            email=Email(user_model.email),
            full_name=user_model.full_name,
            hashed_password=Password.create_from_hash(user_model.hashed_password),
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            last_login=user_model.last_login,
            login_attempts=user_model.login_attempts,
            locked_until=user_model.locked_until,
            email_verified=user_model.email_verified,
            email_verification_token=user_model.email_verification_token,
            email_verification_sent_at=user_model.email_verification_sent_at,
            password_reset_token=user_model.password_reset_token,
            password_reset_sent_at=user_model.password_reset_sent_at,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
        )
