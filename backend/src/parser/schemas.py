"""
Pydantic схемы для модуля Parser

Определяет входные и выходные модели данных для API парсера VK
"""

from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

from ..pagination import PaginatedResponse


class ParseRequest(BaseModel):
    """Запрос на парсинг группы"""

    group_ids: List[int] = Field(..., description="Список ID групп VK для парсинга")
    max_posts: Optional[int] = Field(100, description="Максимум постов для обработки")
    max_comments_per_post: Optional[int] = Field(100, description="Максимум комментариев на пост")
    force_reparse: bool = Field(False, description="Принудительно перепарсить существующие данные")
    priority: str = Field("normal", description="Приоритет задачи: low, normal, high")


class ParseResponse(BaseModel):
    """Ответ на запрос парсинга"""

    task_id: str = Field(..., description="ID задачи парсинга")
    status: str = Field(..., description="Статус задачи")
    group_ids: List[int] = Field(..., description="Обработанные группы")
    estimated_time: Optional[int] = Field(None, description="Ожидаемое время выполнения в секундах")
    created_at: datetime = Field(..., description="Время создания задачи")


class ParseStatus(BaseModel):
    """Статус задачи парсинга"""

    task_id: str = Field(..., description="ID задачи")
    status: str = Field(..., description="Текущий статус")
    progress: float = Field(..., description="Прогресс выполнения (0-100)")
    current_group: Optional[int] = Field(None, description="Текущая обрабатываемая группа")
    groups_completed: int = Field(..., description="Количество завершенных групп")
    groups_total: int = Field(..., description="Общее количество групп")
    posts_found: int = Field(..., description="Найдено постов")
    comments_found: int = Field(..., description="Найдено комментариев")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")
    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    duration: Optional[int] = Field(None, description="Длительность в секундах")


class ParserState(BaseModel):
    """Общее состояние парсера"""

    is_running: bool = Field(..., description="Запущен ли парсер")
    active_tasks: int = Field(..., description="Количество активных задач")
    queue_size: int = Field(..., description="Размер очереди задач")
    total_tasks_processed: int = Field(..., description="Всего обработано задач")
    total_posts_found: int = Field(..., description="Всего найдено постов")
    total_comments_found: int = Field(..., description="Всего найдено комментариев")
    last_activity: Optional[datetime] = Field(None, description="Последняя активность")
    uptime_seconds: int = Field(..., description="Время работы в секундах")


class StopParseRequest(BaseModel):
    """Запрос на остановку парсинга"""

    task_id: Optional[str] = Field(None, description="ID задачи для остановки (опционально)")


class StopParseResponse(BaseModel):
    """Ответ на остановку парсинга"""

    stopped_tasks: List[str] = Field(..., description="Остановленные задачи")
    message: str = Field(..., description="Сообщение о результате")


class VKGroupInfo(BaseModel):
    """Информация о группе VK"""

    id: int = Field(..., description="ID группы в VK")
    name: str = Field(..., description="Название группы")
    screen_name: str = Field(..., description="Короткое имя группы")
    description: Optional[str] = Field(None, description="Описание группы")
    members_count: int = Field(..., description="Количество участников")
    photo_url: Optional[str] = Field(None, description="URL фото группы")
    is_closed: bool = Field(..., description="Закрыта ли группа")


class VKPostInfo(BaseModel):
    """Информация о посте VK"""

    id: int = Field(..., description="ID поста")
    text: str = Field(..., description="Текст поста")
    date: datetime = Field(..., description="Дата публикации")
    likes_count: int = Field(..., description="Количество лайков")
    comments_count: int = Field(..., description="Количество комментариев")
    author_id: int = Field(..., description="ID автора поста")


class VKCommentInfo(BaseModel):
    """Информация о комментарии VK"""

    id: int = Field(..., description="ID комментария")
    post_id: int = Field(..., description="ID поста")
    text: str = Field(..., description="Текст комментария")
    date: datetime = Field(..., description="Дата публикации")
    likes_count: int = Field(..., description="Количество лайков")
    author_id: int = Field(..., description="ID автора")
    author_name: Optional[str] = Field(None, description="Имя автора")


class ParseResult(BaseModel):
    """Результат парсинга группы"""

    group_id: int = Field(..., description="ID обработанной группы")
    posts_found: int = Field(..., description="Найдено постов")
    comments_found: int = Field(..., description="Найдено комментариев")
    posts_saved: int = Field(..., description="Сохранено постов")
    comments_saved: int = Field(..., description="Сохранено комментариев")
    errors: List[str] = Field(default_factory=list, description="Список ошибок")
    duration_seconds: float = Field(..., description="Время выполнения в секундах")


class ParseTask(BaseModel):
    """Задача парсинга"""

    id: str = Field(..., description="ID задачи")
    group_ids: List[int] = Field(..., description="Группы для обработки")
    config: Dict[str, Any] = Field(..., description="Конфигурация парсинга")
    status: str = Field(..., description="Статус задачи")
    created_at: datetime = Field(..., description="Время создания")
    started_at: Optional[datetime] = Field(None, description="Время начала")
    completed_at: Optional[datetime] = Field(None, description="Время завершения")
    progress: float = Field(..., description="Прогресс выполнения")
    result: Optional[ParseResult] = Field(None, description="Результат выполнения")


class ParseTaskListResponse(PaginatedResponse[ParseTask]):
    """Список задач парсинга"""
    pass


class ParseStats(BaseModel):
    """Статистика парсинга"""

    total_tasks: int = Field(..., description="Всего задач")
    completed_tasks: int = Field(..., description="Завершенных задач")
    failed_tasks: int = Field(..., description="Проваленных задач")
    running_tasks: int = Field(..., description="Запущенных задач")
    total_posts_found: int = Field(..., description="Всего найдено постов")
    total_comments_found: int = Field(..., description="Всего найдено комментариев")
    total_processing_time: int = Field(..., description="Общее время обработки в секундах")
    average_task_duration: float = Field(..., description="Средняя длительность задачи")


class VKAPIError(BaseModel):
    """Ошибка VK API"""

    error_code: int = Field(..., description="Код ошибки VK")
    error_msg: str = Field(..., description="Сообщение об ошибке")
    request_params: Optional[Dict[str, Any]] = Field(None, description="Параметры запроса")


# Экспорт всех схем
__all__ = [
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
