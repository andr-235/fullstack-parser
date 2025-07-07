"""
Модель пользователя
"""

from __future__ import annotations

from app.models.base import BaseModel
from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column


class User(BaseModel):
    """Модель пользователя"""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str | None] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"
