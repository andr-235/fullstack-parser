"""
Infrastructure модель для пользователя (DDD)

SQLAlchemy модель для работы с пользователями в Infrastructure Layer
"""

from typing import Any, Dict

from sqlalchemy import Boolean, Column, String

from .base import BaseModel


class UserModel(BaseModel):
    """Infrastructure модель пользователя"""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    def to_domain_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для Domain Entity"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "hashed_password": self.hashed_password,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_domain_dict(cls, data: Dict[str, Any]) -> "UserModel":
        """Создать модель из словаря Domain Entity"""
        model = cls()
        model.email = data.get("email")
        model.full_name = data.get("full_name")
        model.hashed_password = data.get("hashed_password")
        model.is_active = data.get("is_active", True)
        model.is_superuser = data.get("is_superuser", False)
        return model

    def update_from_domain_dict(self, data: Dict[str, Any]) -> None:
        """Обновить модель из словаря Domain Entity"""
        if "email" in data:
            self.email = data["email"]
        if "full_name" in data:
            self.full_name = data["full_name"]
        if "hashed_password" in data:
            self.hashed_password = data["hashed_password"]
        if "is_active" in data:
            self.is_active = data["is_active"]
        if "is_superuser" in data:
            self.is_superuser = data["is_superuser"]

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email}')>"
