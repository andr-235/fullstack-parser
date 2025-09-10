"""
Pydantic схемы для модуля Parser

Определяет входные и выходные модели данных для API парсера VK
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any, Dict, Annotated, Literal, Union
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
    computed_field,
    ValidationInfo,
)
from enum import Enum

from ..pagination import PaginatedResponse
from .models import TaskStatus, TaskPriority


class BaseParserModel(BaseModel):
    """Базовая модель для всех схем парсера."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
        use_enum_values=True,
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()},
        # Включаем строгую валидацию
        revalidate_instances="always",
        # Включаем валидацию при создании
        validate_default=True,
    )


class ParseRequest(BaseParserModel):
    """Запрос на парсинг группы"""

    group_ids: Annotated[
        List[int],
        Field(
            ...,
            description="Список VK ID групп для парсинга (положительные числа)",
            min_length=1,
            max_length=10000,
        ),
    ]
    max_posts: Annotated[
        Optional[int],
        Field(
            default=100,
            ge=1,
            le=1000,
            description="Максимум постов для обработки",
        ),
    ] = 100
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
        """Валидация ID групп VK."""
        if not isinstance(v, list):
            raise ValueError("group_ids должен быть списком")

        if not v:
            raise ValueError("group_ids не может быть пустым")

        if len(v) > 10000:
            raise ValueError(
                "group_ids не может содержать более 10000 элементов"
            )

        # Проверяем уникальность
        if len(v) != len(set(v)):
            raise ValueError("group_ids не должен содержать дубликаты")

        # Валидируем каждый ID
        for group_id in v:
            if not isinstance(group_id, int):
                raise ValueError("ID группы должен быть целым числом")

            # VK group ID должны быть положительными числами (как хранятся в БД)
            # Отрицательные числа - это внутренние ID БД, которые не должны использоваться
            if group_id <= 0:
                raise ValueError(
                    f"ID группы {group_id} должен быть положительным числом (VK group ID). "
                    f"Отрицательные числа - это внутренние ID базы данных. Используйте VK ID группы."
                )

            if group_id > 2_000_000_000:
                raise ValueError(
                    "ID группы превышает максимальное значение VK"
                )

        return v

    @field_validator("max_posts", mode="after")
    @classmethod
    def validate_max_posts(cls, v: Optional[int]) -> Optional[int]:
        """Валидация максимального количества постов."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError("max_posts должен быть целым числом")

            if v < 1:
                raise ValueError("max_posts должен быть не менее 1")

            if v > 1000:
                raise ValueError("max_posts не может быть больше 1000")

        return v

    @field_validator("max_comments_per_post", mode="after")
    @classmethod
    def validate_max_comments(cls, v: Optional[int]) -> Optional[int]:
        """Валидация максимального количества комментариев."""
        if v is not None:
            if not isinstance(v, int):
                raise ValueError(
                    "max_comments_per_post должен быть целым числом"
                )

            if v < 1:
                raise ValueError(
                    "max_comments_per_post должен быть не менее 1"
                )

            if v > 1000:
                raise ValueError(
                    "max_comments_per_post не может быть больше 1000"
                )

        return v

    @model_validator(mode="after")
    def validate_limits(self) -> "ParseRequest":
        """Валидация лимитов и общего объема данных."""
        group_count = len(self.group_ids)
        max_posts = self.max_posts or 100
        max_comments_per_post = self.max_comments_per_post or 100

        # Импортируем настройки для получения лимитов
        from .config import parser_settings

        # Проверяем общий лимит запросов с реалистичным расчетом
        # Используем средние значения для более точной оценки
        avg_posts = min(max_posts, parser_settings.avg_posts_per_group)
        avg_comments = min(
            max_comments_per_post, parser_settings.avg_comments_per_post
        )

        # Реалистичная оценка: не все группы имеют посты, не все посты имеют комментарии
        estimated_requests = group_count * avg_posts * avg_comments

        # Максимально возможное количество запросов (worst case)
        max_possible_requests = group_count * max_posts * max_comments_per_post

        # Проверяем максимально возможное количество запросов
        if max_possible_requests > parser_settings.max_total_requests:
            raise ValueError(
                f"Слишком большой объем данных для обработки: {max_possible_requests:,} запросов. "
                f"Максимум: {parser_settings.max_total_requests:,}"
            )

        # Предупреждение для больших объемов
        if estimated_requests > parser_settings.max_total_requests_warning:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Большой объем данных для парсинга: ~{estimated_requests:,.0f} запросов "
                f"(максимум: {parser_settings.max_total_requests:,})"
            )

        return self


class ParseResponse(BaseParserModel):
    """Ответ на запрос парсинга"""

    task_id: str = Field(..., description="ID задачи парсинга")
    status: TaskStatus = Field(..., description="Статус задачи")
    group_ids: List[int] = Field(..., description="Обработанные группы")
    estimated_time: Optional[int] = Field(
        None, ge=0, description="Ожидаемое время выполнения в секундах"
    )
    created_at: datetime = Field(..., description="Время создания задачи")
    priority: TaskPriority = Field(..., description="Приоритет задачи")


class ParseStatus(BaseParserModel):
    """Статус задачи парсинга"""

    task_id: Annotated[
        str, Field(..., min_length=1, max_length=36, description="ID задачи")
    ]
    status: TaskStatus = Field(..., description="Текущий статус")
    progress: Annotated[
        float,
        Field(
            default=0.0,
            ge=0,
            le=100,
            description="Прогресс выполнения (0-100)",
        ),
    ] = 0.0
    current_group: Optional[Annotated[int, Field(ge=0)]] = Field(
        default=None, description="Текущая обрабатываемая группа"
    )
    groups_completed: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Количество завершенных групп"
    )
    groups_total: Annotated[int, Field(ge=1)] = Field(
        default=1, description="Общее количество групп"
    )
    posts_found: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Найдено постов"
    )
    comments_found: Annotated[int, Field(ge=0)] = Field(
        default=0, description="Найдено комментариев"
    )
    errors: List[str] = Field(
        default_factory=list, description="Список ошибок"
    )
    started_at: Optional[datetime] = Field(
        default=None, description="Время начала"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Время завершения"
    )
    duration: Optional[Annotated[float, Field(ge=0)]] = Field(
        default=None, description="Длительность в секундах"
    )
    priority: TaskPriority = Field(..., description="Приоритет задачи")

    @field_validator("groups_completed", mode="after")
    @classmethod
    def validate_groups_completed(cls, v: int, info: ValidationInfo) -> int:
        """Валидация завершенных групп."""
        if not isinstance(v, int):
            raise ValueError("groups_completed должен быть целым числом")

        if v < 0:
            raise ValueError("groups_completed должен быть неотрицательным")

        # Проверяем, что завершенных групп не больше общего количества
        if hasattr(info, "data") and "groups_total" in info.data:
            groups_total = info.data["groups_total"]
            if v > groups_total:
                raise ValueError(
                    f"Завершенных групп ({v}) не может быть больше общего количества ({groups_total})"
                )

        return v

    @field_validator("progress", mode="after")
    @classmethod
    def validate_progress(cls, v: float) -> float:
        """Валидация прогресса."""
        if not isinstance(v, (int, float)):
            raise ValueError("progress должен быть числом")

        if v < 0.0 or v > 100.0:
            raise ValueError(
                "progress должен быть в диапазоне от 0.0 до 100.0"
            )

        return float(v)

    @field_validator("task_id", mode="after")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Валидация ID задачи."""
        if not isinstance(v, str):
            raise ValueError("task_id должен быть строкой")

        v = v.strip()
        if not v:
            raise ValueError("task_id не может быть пустым")

        if len(v) > 36:
            raise ValueError("task_id не может быть длиннее 36 символов")

        return v

    @field_validator("errors", mode="after")
    @classmethod
    def validate_errors(cls, v: List[str]) -> List[str]:
        """Валидация списка ошибок."""
        if not isinstance(v, list):
            raise ValueError("Ошибки должны быть списком строк")

        return [str(error).strip() for error in v if str(error).strip()]

    @model_validator(mode="after")
    def validate_timestamps(self) -> "ParseStatus":
        """Валидация временных меток."""
        if (
            self.started_at
            and self.completed_at
            and self.started_at > self.completed_at
        ):
            raise ValueError("started_at не может быть позже completed_at")

        return self

    @computed_field
    def is_completed(self) -> bool:
        """Проверить завершена ли задача."""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.STOPPED,
        ]

    @computed_field
    def is_running(self) -> bool:
        """Проверить выполняется ли задача."""
        return self.status == TaskStatus.RUNNING

    @computed_field
    def completion_rate(self) -> float:
        """Получить процент завершения."""
        if self.groups_total == 0:
            return 0.0
        return (self.groups_completed / self.groups_total) * 100


class ParserState(BaseParserModel):
    """Общее состояние парсера"""

    is_running: bool = Field(..., description="Запущен ли парсер")
    active_tasks: int = Field(0, ge=0, description="Количество активных задач")
    queue_size: int = Field(0, ge=0, description="Размер очереди задач")
    total_tasks_processed: int = Field(
        0, ge=0, description="Всего обработано задач"
    )
    total_posts_found: int = Field(0, ge=0, description="Всего найдено постов")
    total_comments_found: int = Field(
        0, ge=0, description="Всего найдено комментариев"
    )
    last_activity: Optional[datetime] = Field(
        None, description="Последняя активность"
    )
    started_at: Optional[datetime] = Field(
        None, description="Время начала парсинга"
    )
    uptime_seconds: int = Field(0, ge=0, description="Время работы в секундах")
    overall_progress: float = Field(
        0.0, ge=0, le=100, description="Общий прогресс парсинга (0-100)"
    )


class StopParseRequest(BaseParserModel):
    """Запрос на остановку парсинга"""

    task_id: Optional[str] = Field(
        None, description="ID задачи для остановки (опционально)"
    )


class StopParseResponse(BaseParserModel):
    """Ответ на остановку парсинга"""

    stopped_tasks: List[str] = Field(..., description="Остановленные задачи")
    message: str = Field(..., description="Сообщение о результате")


class VKGroupInfo(BaseParserModel):
    """Информация о группе VK"""

    id: int = Field(..., gt=0, description="ID группы в VK")
    name: str = Field(
        ..., min_length=1, max_length=200, description="Название группы"
    )
    screen_name: str = Field(
        ..., min_length=1, max_length=100, description="Короткое имя группы"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Описание группы"
    )
    members_count: int = Field(..., ge=0, description="Количество участников")
    photo_url: Optional[str] = Field(
        None, max_length=500, description="URL фото группы"
    )
    is_closed: bool = Field(..., description="Закрыта ли группа")

    @field_validator("screen_name", mode="after")
    @classmethod
    def validate_screen_name(cls, v: str) -> str:
        """Валидация короткого имени группы."""
        if not isinstance(v, str):
            raise ValueError("screen_name должен быть строкой")

        v = v.strip()
        if not v:
            raise ValueError("screen_name не может быть пустым")

        if len(v) > 100:
            raise ValueError("screen_name не может быть длиннее 100 символов")

        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError(
                "Короткое имя группы может содержать только буквы, цифры, _ и -"
            )

        return v

    @field_validator("photo_url", mode="after")
    @classmethod
    def validate_photo_url(cls, v: Optional[str]) -> Optional[str]:
        """Валидация URL фото."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("photo_url должен быть строкой")

            v = v.strip()
            if v and len(v) > 500:
                raise ValueError(
                    "photo_url не может быть длиннее 500 символов"
                )

            if v and not v.startswith(("http://", "https://")):
                raise ValueError(
                    "URL фото должен начинаться с http:// или https://"
                )

        return v


class VKPostInfo(BaseParserModel):
    """Информация о посте VK"""

    id: int = Field(..., gt=0, description="ID поста")
    text: str = Field(..., max_length=10000, description="Текст поста")
    date: datetime = Field(..., description="Дата публикации")
    likes_count: int = Field(..., ge=0, description="Количество лайков")
    comments_count: int = Field(
        ..., ge=0, description="Количество комментариев"
    )
    author_id: int = Field(..., description="ID автора поста")

    @field_validator("text", mode="after")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Валидация текста поста."""
        if not isinstance(v, str):
            raise ValueError("text должен быть строкой")

        v = v.strip()
        if not v:
            raise ValueError("Текст поста не может быть пустым")

        if len(v) > 10000:
            raise ValueError(
                "Текст поста не может быть длиннее 10000 символов"
            )

        return v


class VKCommentInfo(BaseParserModel):
    """Информация о комментарии VK"""

    id: int = Field(..., gt=0, description="ID комментария")
    post_id: int = Field(..., gt=0, description="ID поста")
    text: str = Field(..., max_length=5000, description="Текст комментария")
    date: datetime = Field(..., description="Дата публикации")
    likes_count: int = Field(..., ge=0, description="Количество лайков")
    author_id: int = Field(..., description="ID автора")
    author_name: Optional[str] = Field(
        None, max_length=200, description="Имя автора"
    )

    @field_validator("text", mode="after")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Валидация текста комментария."""
        if not isinstance(v, str):
            raise ValueError("text должен быть строкой")

        v = v.strip()
        if not v:
            raise ValueError("Текст комментария не может быть пустым")

        if len(v) > 5000:
            raise ValueError(
                "Текст комментария не может быть длиннее 5000 символов"
            )

        return v


class ParseResult(BaseParserModel):
    """Результат парсинга группы"""

    group_id: int = Field(..., gt=0, description="ID обработанной группы")
    posts_found: int = Field(..., ge=0, description="Найдено постов")
    comments_found: int = Field(..., ge=0, description="Найдено комментариев")
    posts_saved: int = Field(..., ge=0, description="Сохранено постов")
    comments_saved: int = Field(
        ..., ge=0, description="Сохранено комментариев"
    )
    errors: List[str] = Field(
        default_factory=list, description="Список ошибок"
    )
    duration_seconds: float = Field(
        ..., ge=0, description="Время выполнения в секундах"
    )

    @model_validator(mode="after")
    def validate_saved_counts(self) -> "ParseResult":
        """Валидация количества сохраненных данных."""
        if not isinstance(self.posts_saved, int) or self.posts_saved < 0:
            raise ValueError(
                "posts_saved должен быть неотрицательным целым числом"
            )

        if not isinstance(self.comments_saved, int) or self.comments_saved < 0:
            raise ValueError(
                "comments_saved должен быть неотрицательным целым числом"
            )

        if not isinstance(self.posts_found, int) or self.posts_found < 0:
            raise ValueError(
                "posts_found должен быть неотрицательным целым числом"
            )

        if not isinstance(self.comments_found, int) or self.comments_found < 0:
            raise ValueError(
                "comments_found должен быть неотрицательным целым числом"
            )

        if self.posts_saved > self.posts_found:
            raise ValueError("Сохранено постов не может быть больше найденных")

        if self.comments_saved > self.comments_found:
            raise ValueError(
                "Сохранено комментариев не может быть больше найденных"
            )

        return self

    @computed_field
    def success_rate(self) -> float:
        """Процент успешно сохраненных данных."""
        total_found = self.posts_found + self.comments_found
        total_saved = self.posts_saved + self.comments_saved

        if total_found == 0:
            return 100.0 if not self.errors else 0.0

        return (total_saved / total_found) * 100


class ParseTask(BaseParserModel):
    """Задача парсинга"""

    id: str = Field(..., description="ID задачи")
    group_ids: List[int] = Field(..., description="Группы для обработки")
    config: Dict[str, Any] = Field(..., description="Конфигурация парсинга")
    status: TaskStatus = Field(..., description="Статус задачи")
    priority: TaskPriority = Field(..., description="Приоритет задачи")
    created_at: datetime = Field(..., description="Время создания")
    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(
        None, description="Время завершения"
    )
    progress: float = Field(
        0.0, ge=0, le=100, description="Прогресс выполнения"
    )
    result: Optional[ParseResult] = Field(
        None, description="Результат выполнения"
    )


class ParseTaskListResponse(PaginatedResponse[ParseTask]):
    """Список задач парсинга"""

    pass


class ParseStats(BaseParserModel):
    """Статистика парсинга"""

    total_tasks: int = Field(..., description="Всего задач")
    completed_tasks: int = Field(..., description="Завершенных задач")
    failed_tasks: int = Field(..., description="Проваленных задач")
    running_tasks: int = Field(..., description="Запущенных задач")
    total_posts_found: int = Field(..., description="Всего найдено постов")
    total_comments_found: int = Field(
        ..., description="Всего найдено комментариев"
    )
    total_processing_time: int = Field(
        ..., description="Общее время обработки в секундах"
    )
    average_task_duration: float = Field(
        ..., description="Средняя длительность задачи"
    )
    # Лимиты парсинга
    max_groups_per_request: int = Field(
        ..., description="Максимум групп за один запрос"
    )
    max_posts_per_request: int = Field(
        ..., description="Максимум постов за запрос"
    )
    max_comments_per_request: int = Field(
        ..., description="Максимум комментариев за запрос"
    )
    max_users_per_request: int = Field(
        ..., description="Максимум пользователей за запрос"
    )


class VKAPIError(BaseParserModel):
    """Ошибка VK API"""

    error_code: int = Field(..., description="Код ошибки VK")
    error_msg: str = Field(..., description="Сообщение об ошибке")
    request_params: Optional[Dict[str, Any]] = Field(
        None, description="Параметры запроса"
    )


# Валидаторы (из validators.py)
class VKAPIValidators:
    """Специализированные валидаторы для VK API"""

    @staticmethod
    def validate_api_response(
        response: Dict[str, Any], required_fields: List[str]
    ) -> Dict[str, Any]:
        """Валидация ответа VK API"""
        if not isinstance(response, dict):
            raise ValueError("Ответ API должен быть словарем")

        for field in required_fields:
            if field not in response:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        return response

    @staticmethod
    def validate_error_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """Валидация ответа с ошибкой VK API"""
        if not isinstance(response, dict):
            raise ValueError("Ответ с ошибкой должен быть словарем")

        if "error" not in response:
            raise ValueError("Ответ с ошибкой должен содержать поле 'error'")

        error = response["error"]
        if not isinstance(error, dict):
            raise ValueError("Поле 'error' должно быть словарем")

        required_error_fields = ["error_code", "error_msg"]
        for field in required_error_fields:
            if field not in error:
                raise ValueError(f"Ошибка должна содержать поле: {field}")

        return response


# Экспорт всех схем
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
    "VKAPIValidators",
]
