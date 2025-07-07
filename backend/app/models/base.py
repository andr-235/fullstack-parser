"""
Базовая модель для VK Comments Parser
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
import sqlalchemy as sa


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseModel(Base):
    """Базовая модель с общими полями: id, created_at, updated_at."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        comment="Время создания записи",
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Время последнего обновления записи",
    )
