"""
Модели для модуля Parser

Определяет SQLAlchemy модели и Pydantic модели для работы с задачами парсинга
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)
from sqlalchemy import (
    JSON,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from parser.constants import (
    TASK_PRIORITY_HIGH,
    TASK_PRIORITY_LOW,
    TASK_PRIORITY_NORMAL,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_STOPPED,
)


# Enums для типизации
class TaskStatus(str, Enum):
    """Статусы задач парсинга"""

    PENDING = TASK_STATUS_PENDING
    RUNNING = TASK_STATUS_RUNNING
    COMPLETED = TASK_STATUS_COMPLETED
    FAILED = TASK_STATUS_FAILED
    STOPPED = TASK_STATUS_STOPPED


class TaskPriority(str, Enum):
    """Приоритеты задач"""

    LOW = TASK_PRIORITY_LOW
    NORMAL = TASK_PRIORITY_NORMAL
    HIGH = TASK_PRIORITY_HIGH


# SQLAlchemy модель
from src.common.database import Base

class ParsingTaskModel(Base):
    """SQLAlchemy модель задачи парсинга"""

    __tablename__ = "parsing_tasks"

    # Первичный ключ
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
        comment="Уникальный идентификатор задачи",
    )

    # Основные поля задачи
    group_ids: Mapped[List[int]] = mapped_column(
        JSON, nullable=False, comment="Список ID групп для парсинга"
    )
    config: Mapped[Dict[str, Any]] = mapped_column(
        JSON, nullable=False, comment="Конфигурация парсинга"
    )

    # Статус и приоритет
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TASK_STATUS_PENDING,
        comment="Статус задачи",
    )
    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=TASK_PRIORITY_NORMAL,
        comment="Приоритет задачи",
    )

    # Прогресс выполнения
    progress: Mapped[int] = mapped_column(
        Integer, default=0, comment="Прогресс выполнения (0-100)"
    )
    current_group: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="Текущая обрабатываемая группа"
    )
    groups_completed: Mapped[int] = mapped_column(
        Integer, default=0, comment="Количество завершенных групп"
    )
    groups_total: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Общее количество групп"
    )

    # Результаты парсинга
    posts_found: Mapped[int] = mapped_column(
        Integer, default=0, comment="Найдено постов"
    )
    comments_found: Mapped[int] = mapped_column(
        Integer, default=0, comment="Найдено комментариев"
    )

    # Ошибки и результат
    errors: Mapped[List[str]] = mapped_column(
        JSON, default=list, comment="Список ошибок"
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, comment="Результат выполнения"
    )

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Время создания записи",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
        comment="Время последнего обновления записи",
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время начала выполнения",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Время завершения"
    )

    def __repr__(self) -> str:
        return (
            f"ParsingTaskModel(id={self.id!r}, status={self.status!r}, "
            f"progress={self.progress}%)"
        )


# Pydantic модели
class ParsingTask(BaseModel):
    """Pydantic модель задачи парсинга"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )

    # Основные поля
    task_id: str = Field(..., description="Уникальный идентификатор задачи")
    group_ids: List[int] = Field(..., min_length=1, description="Список ID групп для парсинга")
    config: Dict[str, Any] = Field(..., description="Конфигурация парсинга")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Статус задачи")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Приоритет задачи")

    # Прогресс выполнения
    progress: int = Field(default=0, ge=0, le=100, description="Прогресс выполнения (0-100)")
    current_group: Optional[int] = Field(default=None, description="Текущая обрабатываемая группа")
    groups_completed: int = Field(default=0, ge=0, description="Количество завершенных групп")
    groups_total: int = Field(..., description="Общее количество групп")

    # Результаты парсинга
    posts_found: int = Field(default=0, ge=0, description="Найдено постов")
    comments_found: int = Field(default=0, ge=0, description="Найдено комментариев")

    # Ошибки и результат
    errors: List[str] = Field(default_factory=list, description="Список ошибок")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Результат выполнения")

    # Временные метки
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Время создания")
    started_at: Optional[datetime] = Field(default=None, description="Время начала выполнения")
    completed_at: Optional[datetime] = Field(default=None, description="Время завершения")

    @computed_field
    def duration(self) -> Optional[float]:
        """Получить длительность выполнения"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None

    @computed_field
    def is_completed(self) -> bool:
        """Проверить завершена ли задача"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.STOPPED]

    @computed_field
    def is_running(self) -> bool:
        """Проверить выполняется ли задача"""
        return self.status == TaskStatus.RUNNING

# Экспорт
__all__ = [
    "TaskStatus",
    "TaskPriority",
    "ParsingTaskModel",
    "ParsingTask",
]
