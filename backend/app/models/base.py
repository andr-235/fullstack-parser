"""
Базовая модель для VK Comments Parser
"""

from datetime import datetime

from app.core.database import Base
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class BaseModel(Base):
    """Базовая модель с общими полями: id, created_at, updated_at."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
