"""
Pydantic схемы для модуля Parser

Определяет входные и выходные модели данных для API парсера VK
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Annotated, Literal
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
)
from enum import Enum

from parser.models import TaskStatus, TaskPriority


class BaseParserModel(BaseModel):
    """Базовая модель для всех схем парсера"""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class ParseRequest(BaseParserModel):
    """Запрос на парсинг группы"""

    group_ids: Annotated[
        List[int],
        Field(
            ...,
            description="Список VK ID групп для парсинга (положительные числа)",
            min_length=1,
            max_length=100,
        ),
    ]
    max_posts: Annotated[
        Optional[int],
        Field(
            default=10,
            ge=1,
            le=1000,
            description="Максимум постов для обработки",
        ),
    ] = 10
    max_comments_per_post: Annotated[
        Optional[int],
        Field(
            default=100,
            ge=1,
            le=1000,
            description="Максимум комментариев на пост",
        ),
    ] = 100
    force_reparse: bool = Field(
        default=False,
        description="Принудительно перепарсить существующие данные",
    )
    priority: TaskPriority = Field(
        default=TaskPriority.NORMAL, description="Приоритет задачи"
    )

    @field_validator("group_ids", mode="after")
    @classmethod
    def validate_group_ids(cls, v: List[int]) -> List[int]:
        """Валидация ID групп VK"""
        if not isinstance(v, list):
            raise ValueError("group_ids должен быть списком")

        if not v:
            raise ValueError("group_ids не может быть пустым")

        if len(v) > 100:
            raise ValueError("group_ids не может содержать более 100 элементов")

        # Проверяем уникальность
        if len(v) != len(set(v)):
            raise ValueError("group_ids не должен содержать дубликаты")

        # Валидируем каждый ID
        for group_id in v:
            if not isinstance(group_id, int):
                raise ValueError("ID группы должен быть целым числом")

            if group_id <= 0:
                raise ValueError(f"ID группы {group_id} должен быть положительным числом")

            if group_id > 2_000_000_000:
                raise ValueError("ID группы превышает максимальное значение VK")

        return v


class ParseResponse(BaseParserModel):
    """Ответ на запрос парсинга"""

    task_id: str = Field(..., description="ID задачи парсинга")
    status: TaskStatus = Field(..., description="Статус задачи")
    group_ids: List[int] = Field(..., description="Обработанные группы")
    created_at: datetime = Field(..., description="Время создания задачи")
    priority: TaskPriority = Field(..., description="Приоритет задачи")


class ParseStatus(BaseParserModel):
    """Статус задачи парсинга"""

    task_id: str = Field(..., description="ID задачи")
    status: TaskStatus = Field(..., description="Текущий статус")
    progress: int = Field(default=0, ge=0, le=100, description="Прогресс выполнения (0-100)")
    current_group: Optional[int] = Field(default=None, description="Текущая обрабатываемая группа")
    groups_completed: int = Field(default=0, ge=0, description="Количество завершенных групп")
    groups_total: int = Field(default=1, ge=1, description="Общее количество групп")
    posts_found: int = Field(default=0, ge=0, description="Найдено постов")
    comments_found: int = Field(default=0, ge=0, description="Найдено комментариев")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")
    started_at: Optional[datetime] = Field(default=None, description="Время начала")
    completed_at: Optional[datetime] = Field(default=None, description="Время завершения")
    duration: Optional[float] = Field(default=None, ge=0, description="Длительность в секундах")
    priority: TaskPriority = Field(..., description="Приоритет задачи")

    @computed_field
    def is_completed(self) -> bool:
        """Проверить завершена ли задача"""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.STOPPED]

    @computed_field
    def is_running(self) -> bool:
        """Проверить выполняется ли задача"""
        return self.status == TaskStatus.RUNNING


class ParserState(BaseParserModel):
    """Общее состояние парсера"""

    is_running: bool = Field(..., description="Запущен ли парсер")
    active_tasks: int = Field(0, ge=0, description="Количество активных задач")
    total_tasks_processed: int = Field(0, ge=0, description="Всего обработано задач")
    total_posts_found: int = Field(0, ge=0, description="Всего найдено постов")
    total_comments_found: int = Field(0, ge=0, description="Всего найдено комментариев")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")


class StopParseRequest(BaseParserModel):
    """Запрос на остановку парсинга"""

    task_id: Optional[str] = Field(None, description="ID задачи для остановки (опционально)")


class StopParseResponse(BaseParserModel):
    """Ответ на остановку парсинга"""

    stopped_tasks: List[str] = Field(..., description="Остановленные задачи")
    message: str = Field(..., description="Сообщение о результате")


class VKGroupInfo(BaseParserModel):
    """Информация о группе VK"""

    id: int = Field(..., gt=0, description="ID группы в VK")
    name: str = Field(..., min_length=1, max_length=200, description="Название группы")
    screen_name: str = Field(..., min_length=1, max_length=100, description="Короткое имя группы")
    description: Optional[str] = Field(None, description="Описание группы")
    members_count: Optional[int] = Field(None, ge=0, description="Количество участников")
    is_closed: Optional[bool] = Field(None, description="Закрытая ли группа")


class VKPostInfo(BaseParserModel):
    """Информация о посте VK"""

    id: int = Field(..., gt=0, description="ID поста")
    text: str = Field(..., description="Текст поста")
    date: datetime = Field(..., description="Дата создания")
    likes: int = Field(default=0, ge=0, description="Количество лайков")
    reposts: int = Field(default=0, ge=0, description="Количество репостов")
    comments: int = Field(default=0, ge=0, description="Количество комментариев")


class VKCommentInfo(BaseParserModel):
    """Информация о комментарии VK"""

    id: int = Field(..., gt=0, description="ID комментария")
    text: str = Field(..., description="Текст комментария")
    date: datetime = Field(..., description="Дата создания")
    likes: int = Field(default=0, ge=0, description="Количество лайков")
    from_id: int = Field(..., description="ID автора комментария")


class ParseResult(BaseParserModel):
    """Результат парсинга"""

    group_id: int = Field(..., description="ID группы")
    posts_found: int = Field(0, ge=0, description="Найдено постов")
    comments_found: int = Field(0, ge=0, description="Найдено комментариев")
    posts_saved: int = Field(0, ge=0, description="Сохранено постов")
    comments_saved: int = Field(0, ge=0, description="Сохранено комментариев")
    errors: List[str] = Field(default_factory=list, description="Ошибки")
    duration_seconds: float = Field(0.0, ge=0, description="Время выполнения в секундах")
    success: bool = Field(..., description="Успешность выполнения")


class ParseTask(BaseParserModel):
    """Задача парсинга"""

    task_id: str = Field(..., description="ID задачи")
    group_ids: List[int] = Field(..., description="ID групп для парсинга")
    status: TaskStatus = Field(..., description="Статус задачи")
    priority: TaskPriority = Field(..., description="Приоритет задачи")
    progress: int = Field(default=0, ge=0, le=100, description="Прогресс выполнения")
    created_at: datetime = Field(..., description="Время создания")
    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")


class ParseTaskListResponse(BaseParserModel):
    """Ответ со списком задач"""

    tasks: List[ParseTask] = Field(..., description="Список задач")
    total: int = Field(..., ge=0, description="Общее количество задач")


class ParseStats(BaseParserModel):
    """Статистика парсера"""

    total_tasks: int = Field(0, ge=0, description="Всего задач")
    completed_tasks: int = Field(0, ge=0, description="Завершенных задач")
    failed_tasks: int = Field(0, ge=0, description="Неудачных задач")
    running_tasks: int = Field(0, ge=0, description="Выполняющихся задач")
    success_rate: float = Field(0.0, ge=0, le=100, description="Процент успеха")


class VKAPIError(BaseParserModel):
    """Ошибка VK API"""

    error_code: int = Field(..., description="Код ошибки")
    error_message: str = Field(..., description="Сообщение об ошибке")
    request_params: Optional[dict] = Field(None, description="Параметры запроса")


# Экспорт
__all__ = [
    "BaseParserModel",
    "ParseRequest",
    "ParseResponse", 
    "ParseStatus",
    "ParserState",
    "StopParseRequest",
    "StopParseResponse",
    "VKGroupInfo",
    "VKPostInfo",
    "VKCommentInfo",
    "ParseResult",
    "ParseTask",
    "ParseTaskListResponse",
    "ParseStats",
    "VKAPIError",
]