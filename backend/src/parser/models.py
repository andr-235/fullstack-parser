"""
Модели для модуля Parser

Определяет SQLAlchemy модели и Pydantic модели для работы с задачами парсинга
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any, Union, Self, Annotated
from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Integer,
    Text,
    ForeignKey,
    JSON,
    func,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    computed_field,
    field_validator,
)


class Base(DeclarativeBase):
    """Базовый класс для SQLAlchemy моделей"""

    pass


class TimestampMixin:
    """Миксин для полей времени создания и обновления."""

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


class SoftDeleteMixin:
    """Миксин для мягкого удаления."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=None,
        comment="Время мягкого удаления записи",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Флаг мягкого удаления",
    )


from ..database import get_db_session
from ..infrastructure.logging import get_loguru_logger
from .constants import (
    TASK_STATUS_PENDING,
    TASK_STATUS_RUNNING,
    TASK_STATUS_COMPLETED,
    TASK_STATUS_FAILED,
    TASK_STATUS_STOPPED,
    TASK_PRIORITY_LOW,
    TASK_PRIORITY_NORMAL,
    TASK_PRIORITY_HIGH,
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


# SQLAlchemy модели уже определены выше


class ParsingTaskModel(Base, TimestampMixin):
    """SQLAlchemy модель задачи парсинга"""

    __tablename__ = "parsing_tasks"

    # Первичный ключ с использованием UUID
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

    # Статус и приоритет с валидацией
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

    # Прогресс выполнения с ограничениями
    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="Прогресс выполнения (0-100)",
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

    # Временные метки выполнения
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время начала выполнения",
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="Время завершения"
    )

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index("idx_parsing_tasks_status", "status"),
        Index("idx_parsing_tasks_priority", "priority"),
        Index("idx_parsing_tasks_created_at", "created_at"),
        Index("idx_parsing_tasks_started_at", "started_at"),
        CheckConstraint(
            "progress >= 0 AND progress <= 100", name="ck_progress_range"
        ),
        CheckConstraint(
            "groups_completed >= 0", name="ck_groups_completed_positive"
        ),
        CheckConstraint("groups_total > 0", name="ck_groups_total_positive"),
        CheckConstraint("posts_found >= 0", name="ck_posts_found_positive"),
        CheckConstraint(
            "comments_found >= 0", name="ck_comments_found_positive"
        ),
    )

    def __repr__(self) -> str:
        return (
            f"ParsingTaskModel(id={self.id!r}, status={self.status!r}, "
            f"progress={self.progress}%)"
        )


# Pydantic модели
class ParsingTaskBase(BaseModel):
    """Базовая модель задачи парсинга."""

    group_ids: List[int] = Field(
        ..., min_length=1, description="Список ID групп для парсинга"
    )
    config: Dict[str, Any] = Field(..., description="Конфигурация парсинга")
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="Приоритет задачи"
    )


class ParsingTaskCreate(ParsingTaskBase):
    """Модель для создания задачи парсинга."""

    pass


class ParsingTaskUpdate(BaseModel):
    """Модель для обновления задачи парсинга."""

    status: Optional[TaskStatus] = Field(
        default=None, description="Статус задачи"
    )
    progress: Optional[float] = Field(
        default=None, ge=0, le=100, description="Прогресс выполнения (0-100)"
    )
    current_group: Optional[int] = Field(
        default=None, ge=0, description="Текущая обрабатываемая группа"
    )
    groups_completed: Optional[int] = Field(
        default=None, ge=0, description="Количество завершенных групп"
    )
    posts_found: Optional[int] = Field(
        default=None, ge=0, description="Найдено постов"
    )
    comments_found: Optional[int] = Field(
        default=None, ge=0, description="Найдено комментариев"
    )
    errors: Optional[List[str]] = Field(
        default=None, description="Список ошибок"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Результат выполнения"
    )


class ParsingTask(ParsingTaskBase):
    """
    Pydantic модель задачи парсинга

    Представляет задачу парсинга с её состоянием и результатами
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        # Включаем валидацию при присваивании
        revalidate_instances="always",
    )

    # Идентификатор и статус
    task_id: str = Field(
        ...,
        min_length=1,
        max_length=36,
        description="Уникальный идентификатор задачи",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, description="Статус задачи"
    )

    # Прогресс выполнения с валидацией
    progress: Annotated[
        float,
        Field(
            default=0.0,
            ge=0,
            le=100,
            description="Прогресс выполнения (0-100)",
        ),
    ]
    current_group: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Текущая обрабатываемая группа"
    )
    groups_completed: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Количество завершенных групп"
    )

    # Результаты парсинга
    posts_found: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Найдено постов"
    )
    comments_found: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Найдено комментариев"
    )

    # Ошибки и результат
    errors: List[str] = Field(
        default_factory=list, description="Список ошибок"
    )
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Результат выполнения"
    )

    # Временные метки
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Время создания"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Время начала выполнения"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Время завершения"
    )

    @computed_field
    def groups_total(self) -> int:
        """Общее количество групп для обработки"""
        return len(self.group_ids)

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Валидация ID задачи"""
        if not v or not v.strip():
            raise ValueError("ID задачи не может быть пустым")
        return v.strip()

    @field_validator("errors")
    @classmethod
    def validate_errors(cls, v: List[str]) -> List[str]:
        """Валидация списка ошибок"""
        if not isinstance(v, list):
            raise ValueError("Ошибки должны быть списком строк")
        return [str(error).strip() for error in v if str(error).strip()]

    @model_validator(mode="after")
    def validate_groups_completed(self) -> Self:
        """Валидация завершенных групп"""
        if self.groups_completed > len(self.group_ids):
            raise ValueError(
                "Завершенных групп не может быть больше общего количества"
            )
        return self

    @model_validator(mode="after")
    def validate_timestamps(self) -> Self:
        """Валидация временных меток"""
        if self.started_at and self.completed_at:
            if self.started_at > self.completed_at:
                raise ValueError(
                    "Время начала не может быть позже времени завершения"
                )
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь (совместимость с legacy кодом)"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParsingTask":
        """Создать из словаря (совместимость с legacy кодом)"""
        # Обработка legacy формата с полем "id" вместо "task_id"
        if "id" in data and "task_id" not in data:
            data = data.copy()
            data["task_id"] = data.pop("id")
        return cls.model_validate(data)

    def start(self) -> Self:
        """Запустить задачу"""
        return self.model_copy(
            update={
                "status": TaskStatus.RUNNING,
                "started_at": datetime.utcnow(),
            }
        )

    def complete(self, result: Optional[Dict[str, Any]] = None) -> Self:
        """Завершить задачу"""
        return self.model_copy(
            update={
                "status": TaskStatus.COMPLETED,
                "progress": 100.0,
                "completed_at": datetime.utcnow(),
                "result": result,
            }
        )

    def fail(self, errors: List[str]) -> Self:
        """Завершить задачу с ошибкой"""
        return self.model_copy(
            update={
                "status": TaskStatus.FAILED,
                "errors": errors,
                "completed_at": datetime.utcnow(),
            }
        )

    def stop(self) -> Self:
        """Остановить задачу"""
        return self.model_copy(
            update={
                "status": TaskStatus.STOPPED,
                "completed_at": datetime.utcnow(),
            }
        )

    def update_progress(
        self,
        groups_completed: int,
        posts_found: int,
        comments_found: int,
        current_group: Optional[int] = None,
    ) -> Self:
        """Обновить прогресс выполнения"""
        # Пересчитываем прогресс
        progress = 0.0
        total_groups = len(self.group_ids)
        if total_groups > 0:
            progress = (groups_completed / total_groups) * 100
            progress = min(progress, 100.0)

        return self.model_copy(
            update={
                "groups_completed": groups_completed,
                "posts_found": posts_found,
                "comments_found": comments_found,
                "current_group": current_group,
                "progress": progress,
            }
        )

    def add_error(self, error: str) -> Self:
        """Добавить ошибку"""
        new_errors = self.errors.copy()
        new_errors.append(error)
        return self.model_copy(update={"errors": new_errors})

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
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.STOPPED,
        ]

    @computed_field
    def is_running(self) -> bool:
        """Проверить выполняется ли задача"""
        return self.status == TaskStatus.RUNNING


class ParserRepository:
    """
    Репозиторий для работы с задачами парсинга

    Предоставляет интерфейс для хранения и получения задач парсинга
    с использованием современных паттернов SQLAlchemy 2.0
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._logger = get_loguru_logger("parser-repository")

    async def create_task(self, task_data: ParsingTaskCreate) -> ParsingTask:
        """Создать новую задачу парсинга."""
        from sqlalchemy import select

        try:
            self._logger.info(
                f"Creating parsing task for {len(task_data.group_ids)} groups",
                meta={
                    "group_count": len(task_data.group_ids),
                    "priority": task_data.priority.value,
                    "operation": "create_task",
                },
            )

            # Создаем SQLAlchemy модель
            task_model = ParsingTaskModel(
                group_ids=task_data.group_ids,
                config=task_data.config,
                priority=task_data.priority.value,
                groups_total=len(task_data.group_ids),
            )

            self.db.add(task_model)
            await self.db.commit()
            await self.db.refresh(task_model)

            self._logger.info(
                f"Successfully created task {task_model.id}",
                meta={
                    "task_id": task_model.id,
                    "operation": "create_task",
                },
            )

            return self._model_to_business(task_model)

        except Exception as e:
            self._logger.error(
                f"Failed to create parsing task: {str(e)}",
                meta={
                    "error": str(e),
                    "operation": "create_task",
                },
            )
            await self.db.rollback()
            raise

    async def save_task(self, task: ParsingTask) -> ParsingTask:
        """Сохранить задачу в БД (legacy метод для совместимости)"""
        # Конвертируем Pydantic модель в SQLAlchemy модель
        task_model = ParsingTaskModel(
            id=task.task_id,
            group_ids=task.group_ids,
            config=task.config,
            status=task.status.value,
            priority=task.priority.value,
            progress=int(task.progress),
            current_group=task.current_group,
            groups_completed=task.groups_completed,
            groups_total=task.groups_total,
            posts_found=task.posts_found,
            comments_found=task.comments_found,
            errors=task.errors,
            result=task.result,
            created_at=task.created_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
        )

        self.db.add(task_model)
        await self.db.commit()
        await self.db.refresh(task_model)

        return task

    async def get_task(self, task_id: str) -> Optional[ParsingTask]:
        """Получить задачу по ID."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(ParsingTaskModel).where(ParsingTaskModel.id == task_id)
        )
        task_model = result.scalar_one_or_none()

        if not task_model:
            return None

        return self._model_to_business(task_model)

    async def get_all_tasks(
        self, limit: int = 100, offset: int = 0
    ) -> List[ParsingTask]:
        """Получить все задачи с пагинацией"""
        from sqlalchemy import select, desc

        result = await self.db.execute(
            select(ParsingTaskModel)
            .order_by(desc(ParsingTaskModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        task_models = result.scalars().all()

        return [self._model_to_business(model) for model in task_models]

    async def get_tasks_by_status(
        self, status: TaskStatus
    ) -> List[ParsingTask]:
        """Получить задачи по статусу"""
        from sqlalchemy import select

        result = await self.db.execute(
            select(ParsingTaskModel).where(
                ParsingTaskModel.status == status.value
            )
        )
        task_models = result.scalars().all()

        return [self._model_to_business(model) for model in task_models]

    async def update_task(
        self, task_id: str, task_data: ParsingTaskUpdate
    ) -> Optional[ParsingTask]:
        """Обновить задачу."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(ParsingTaskModel).where(ParsingTaskModel.id == task_id)
        )
        task_model = result.scalar_one_or_none()

        if not task_model:
            return None

        # Обновляем только переданные поля
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and value is not None:
                setattr(task_model, field, value.value)
            elif field == "progress" and value is not None:
                setattr(task_model, field, int(value))
            else:
                setattr(task_model, field, value)

        await self.db.commit()
        await self.db.refresh(task_model)

        return self._model_to_business(task_model)

    async def update_task_legacy(self, task: ParsingTask) -> ParsingTask:
        """Обновить задачу (legacy метод для совместимости)."""
        from sqlalchemy import select

        result = await self.db.execute(
            select(ParsingTaskModel).where(ParsingTaskModel.id == task.task_id)
        )
        task_model = result.scalar_one_or_none()

        if not task_model:
            raise ValueError(f"Task {task.task_id} not found")

        # Обновляем поля через setattr для избежания проблем с типизацией
        setattr(task_model, "status", task.status.value)
        setattr(task_model, "priority", task.priority.value)
        setattr(task_model, "progress", int(task.progress))
        setattr(task_model, "current_group", task.current_group)
        setattr(task_model, "groups_completed", task.groups_completed)
        setattr(task_model, "posts_found", task.posts_found)
        setattr(task_model, "comments_found", task.comments_found)
        setattr(task_model, "errors", task.errors)
        setattr(task_model, "result", task.result)
        setattr(task_model, "started_at", task.started_at)
        setattr(task_model, "completed_at", task.completed_at)

        await self.db.commit()
        await self.db.refresh(task_model)

        return task

    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        from sqlalchemy import select, delete

        result = await self.db.execute(
            delete(ParsingTaskModel).where(ParsingTaskModel.id == task_id)
        )
        await self.db.commit()

        return result.rowcount > 0

    async def count_tasks_by_status(
        self, status: Optional[TaskStatus] = None
    ) -> int:
        """Подсчитать задачи по статусу"""
        from sqlalchemy import select, func

        query = select(func.count(ParsingTaskModel.id))
        if status:
            query = query.where(ParsingTaskModel.status == status.value)

        result = await self.db.execute(query)
        count = result.scalar()
        return count if count is not None else 0

    async def get_active_tasks(self) -> List[ParsingTask]:
        """Получить активные задачи"""
        return await self.get_tasks_by_status(TaskStatus.RUNNING)

    def _model_to_business(self, model: ParsingTaskModel) -> ParsingTask:
        """Конвертировать SQLAlchemy модель в Pydantic модель"""
        return ParsingTask.model_validate(
            {
                "task_id": str(model.id),
                "group_ids": list(model.group_ids) if model.group_ids else [],
                "config": dict(model.config) if model.config else {},
                "status": TaskStatus(model.status),
                "priority": TaskPriority(model.priority),
                "progress": float(model.progress),
                "current_group": (
                    int(model.current_group)
                    if model.current_group is not None
                    else None
                ),
                "groups_completed": int(model.groups_completed),
                "posts_found": int(model.posts_found),
                "comments_found": int(model.comments_found),
                "errors": list(model.errors) if model.errors else [],
                "created_at": model.created_at,
                "started_at": model.started_at,
                "completed_at": model.completed_at,
                "result": dict(model.result) if model.result else None,
            }
        )

    async def cleanup_old_tasks(self, days: int = 7) -> int:
        """
        Очистить старые завершенные задачи

        Args:
            days: Возраст задач для удаления в днях

        Returns:
            int: Количество удаленных задач
        """
        from datetime import timedelta
        from sqlalchemy import select, delete

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            delete(ParsingTaskModel)
            .where(
                ParsingTaskModel.status.in_(
                    [
                        TaskStatus.COMPLETED.value,
                        TaskStatus.FAILED.value,
                        TaskStatus.STOPPED.value,
                    ]
                )
            )
            .where(ParsingTaskModel.completed_at < cutoff_date)
        )
        await self.db.commit()

        return result.rowcount

    async def get_tasks_summary(self) -> Dict[str, Any]:
        """Получить сводку по задачам"""
        from sqlalchemy import select, func

        # Общее количество задач
        total_result = await self.db.execute(
            select(func.count(ParsingTaskModel.id))
        )
        total = total_result.scalar() or 0

        # Завершенные задачи
        completed_result = await self.db.execute(
            select(func.count(ParsingTaskModel.id)).where(
                ParsingTaskModel.status == TaskStatus.COMPLETED.value
            )
        )
        completed = completed_result.scalar() or 0

        # Неудачные задачи
        failed_result = await self.db.execute(
            select(func.count(ParsingTaskModel.id)).where(
                ParsingTaskModel.status == TaskStatus.FAILED.value
            )
        )
        failed = failed_result.scalar() or 0

        # Выполняющиеся задачи
        running_result = await self.db.execute(
            select(func.count(ParsingTaskModel.id)).where(
                ParsingTaskModel.status == TaskStatus.RUNNING.value
            )
        )
        running = running_result.scalar() or 0

        success_rate = 0.0
        if total > 0:
            success_rate = (completed / total) * 100

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,
            "success_rate": success_rate,
        }


# Экспорт
__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "TaskStatus",
    "TaskPriority",
    "ParsingTaskModel",
    "ParsingTaskBase",
    "ParsingTaskCreate",
    "ParsingTaskUpdate",
    "ParsingTask",
    "ParserRepository",
]
