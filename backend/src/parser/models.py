"""
Модели для модуля Parser

Определяет репозиторий и модели для работы с задачами парсинга
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..database import get_db_session


class ParsingTask:
    """
    Модель задачи парсинга

    Представляет задачу парсинга с её состоянием и результатами
    """

    def __init__(
        self,
        task_id: str,
        group_ids: List[int],
        config: Dict[str, Any],
        status: str = "pending",
    ):
        self.task_id = task_id
        self.group_ids = group_ids
        self.config = config
        self.status = status
        self.progress = 0.0
        self.current_group = None
        self.groups_completed = 0
        self.groups_total = len(group_ids)
        self.posts_found = 0
        self.comments_found = 0
        self.errors = []
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь"""
        return {
            "id": self.task_id,
            "group_ids": self.group_ids,
            "config": self.config,
            "status": self.status,
            "progress": self.progress,
            "current_group": self.current_group,
            "groups_completed": self.groups_completed,
            "groups_total": self.groups_total,
            "posts_found": self.posts_found,
            "comments_found": self.comments_found,
            "errors": self.errors,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ParsingTask":
        """Создать из словаря"""
        task = cls(
            task_id=data["id"],
            group_ids=data["group_ids"],
            config=data["config"],
            status=data["status"],
        )

        task.progress = data.get("progress", 0.0)
        task.current_group = data.get("current_group")
        task.groups_completed = data.get("groups_completed", 0)
        task.posts_found = data.get("posts_found", 0)
        task.comments_found = data.get("comments_found", 0)
        task.errors = data.get("errors", [])
        task.created_at = data.get("created_at", datetime.utcnow())
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")

        return task

    def start(self):
        """Запустить задачу"""
        self.status = "running"
        self.started_at = datetime.utcnow()

    def complete(self, result: Optional[Dict[str, Any]] = None):
        """Завершить задачу"""
        self.status = "completed"
        self.progress = 100.0
        self.completed_at = datetime.utcnow()
        self.result = result

    def fail(self, errors: List[str]):
        """Завершить задачу с ошибкой"""
        self.status = "failed"
        self.errors = errors
        self.completed_at = datetime.utcnow()

    def stop(self):
        """Остановить задачу"""
        self.status = "stopped"
        self.completed_at = datetime.utcnow()

    def update_progress(
        self,
        groups_completed: int,
        posts_found: int,
        comments_found: int,
        current_group: Optional[int] = None,
    ):
        """Обновить прогресс выполнения"""
        self.groups_completed = groups_completed
        self.posts_found = posts_found
        self.comments_found = comments_found
        self.current_group = current_group

        # Пересчитываем прогресс
        if self.groups_total > 0:
            self.progress = (groups_completed / self.groups_total) * 100
            self.progress = min(self.progress, 100.0)

    def add_error(self, error: str):
        """Добавить ошибку"""
        self.errors.append(error)

    @property
    def duration(self) -> Optional[float]:
        """Получить длительность выполнения"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None

    @property
    def is_completed(self) -> bool:
        """Проверить завершена ли задача"""
        return self.status in ["completed", "failed", "stopped"]

    @property
    def is_running(self) -> bool:
        """Проверить выполняется ли задача"""
        return self.status == "running"


class ParserRepository:
    """
    Репозиторий для работы с задачами парсинга

    Предоставляет интерфейс для хранения и получения задач парсинга
    """

    def __init__(self, db=None):
        # В реальном приложении здесь будет работа с БД
        # Пока используем in-memory хранение для простоты
        self.tasks = {}  # task_id -> ParsingTask
        self.db = db

    async def save_task(self, task: ParsingTask) -> ParsingTask:
        """Сохранить задачу"""
        self.tasks[task.task_id] = task
        return task

    async def get_task(self, task_id: str) -> Optional[ParsingTask]:
        """Получить задачу по ID"""
        return self.tasks.get(task_id)

    async def get_all_tasks(self) -> List[ParsingTask]:
        """Получить все задачи"""
        return list(self.tasks.values())

    async def get_tasks_by_status(self, status: str) -> List[ParsingTask]:
        """Получить задачи по статусу"""
        return [task for task in self.tasks.values() if task.status == status]

    async def delete_task(self, task_id: str) -> bool:
        """Удалить задачу"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    async def count_tasks_by_status(self, status: Optional[str] = None) -> int:
        """Подсчитать задачи по статусу"""
        if status:
            return len(
                [task for task in self.tasks.values() if task.status == status]
            )
        return len(self.tasks)

    async def get_active_tasks(self) -> List[ParsingTask]:
        """Получить активные задачи"""
        return [task for task in self.tasks.values() if task.is_running]

    async def cleanup_old_tasks(self, days: int = 7) -> int:
        """
        Очистить старые завершенные задачи

        Args:
            days: Возраст задач для удаления в днях

        Returns:
            int: Количество удаленных задач
        """
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        tasks_to_delete = []

        for task_id, task in self.tasks.items():
            if (
                task.is_completed
                and task.completed_at
                and task.completed_at < cutoff_date
            ):
                tasks_to_delete.append(task_id)

        for task_id in tasks_to_delete:
            del self.tasks[task_id]

        return len(tasks_to_delete)

    async def get_tasks_summary(self) -> Dict[str, Any]:
        """Получить сводку по задачам"""
        total = len(self.tasks)
        completed = len(
            [t for t in self.tasks.values() if t.status == "completed"]
        )
        failed = len([t for t in self.tasks.values() if t.status == "failed"])
        running = len(
            [t for t in self.tasks.values() if t.status == "running"]
        )

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "running_tasks": running,
            "success_rate": (completed / total * 100) if total > 0 else 0,
        }


# Функции для создания репозитория
async def get_parser_repository(db=None) -> ParserRepository:
    """Создать репозиторий парсера"""
    return ParserRepository(db)


# Экспорт
__all__ = [
    "ParsingTask",
    "ParserRepository",
    "get_parser_repository",
]
