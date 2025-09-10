"""
Сервис для работы с парсингом VK данных

Упрощенный сервис с объединенными компонентами
"""

import asyncio
import time
from typing import List, Optional, Dict, Any, Protocol, Union
from datetime import datetime
from uuid import uuid4

# VKAPIClient удален - используем VKAPIService
from .config import ParserConfig
from ..exceptions import ValidationError, ServiceUnavailableError
from ..vk_api.service import VKAPIService
from ..vk_api.dependencies import create_vk_api_service
from .group_parser import GroupParser, VKAPIServiceProtocol
from .models import TaskStatus, TaskPriority, ParsingTaskModel
from ..infrastructure.logging import get_loguru_logger

logger = get_loguru_logger("parser-service")


class TaskRepositoryProtocol(Protocol):
    """Протокол для репозитория задач"""

    async def create_task(self, task_data: Any) -> Any:
        """Создать задачу"""
        ...

    async def get_task(self, task_id: str) -> Optional[Any]:
        """Получить задачу по ID"""
        ...

    async def update_task(self, task_id: str, task_data: Any) -> Optional[Any]:
        """Обновить задачу"""
        ...

    async def get_tasks_by_status(self, status: str) -> List[Any]:
        """Получить задачи по статусу"""
        ...


# Обработчики ошибок (из error_handler.py)
class VKAPIErrorHandler:
    """Централизованный обработчик ошибок VK API"""

    def __init__(self):
        self._logger = get_loguru_logger("vk-api-error-handler")

    def handle_vk_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        group_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Обработать ошибку VK API"""
        error_type = type(error).__name__
        error_message = str(error)

        self._logger.warn(
            f"VK API Error: {error_type} - {error_message}",
            meta={
                "error_type": error_type,
                "error_message": error_message,
                "group_id": group_id,
                "context": context,
                "operation": "handle_vk_error",
            },
        )

        return {
            "group_id": group_id,
            "posts_found": 0,
            "comments_found": 0,
            "posts_saved": 0,
            "comments_saved": 0,
            "errors": [f"VK API Error: {str(error)}"],
            "duration_seconds": 0.0,
            "error_type": "api_error",
            "retry_recommended": True,
        }

    def should_retry(self, error: Exception) -> bool:
        """Определить, стоит ли повторить запрос после ошибки"""
        # Простая логика для retry
        return (
            "timeout" in str(error).lower() or "network" in str(error).lower()
        )

    def get_retry_delay(self, error: Exception, attempt: int) -> float:
        """Получить задержку перед повтором"""
        return min(2.0 * (2**attempt), 30.0)  # Максимум 30 секунд


class ServiceErrorHandler:
    """Обработчик ошибок сервиса"""

    def __init__(self):
        self._logger = get_loguru_logger("service-error-handler")

    def handle_validation_error(
        self, error: ValidationError, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Обработать ошибку валидации"""
        self._logger.warn(
            f"Validation Error: {str(error)}",
            meta={
                "error_type": "validation_error",
                "error_message": str(error),
                "field": getattr(error, "field", None),
                "context": context,
                "operation": "handle_validation_error",
            },
        )

        return {
            "success": False,
            "error": str(error),
            "error_type": "validation_error",
            "field": getattr(error, "field", None),
        }


# Task Manager (из task_manager.py)
class TaskManager:
    """Менеджер задач парсинга"""

    def __init__(self):
        self._logger = get_loguru_logger("task-manager")
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(
        self,
        group_ids: List[int],
        config: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Создать новую задачу парсинга"""
        try:
            self._validate_task_creation_params(group_ids, config, priority)
            task_id = str(uuid4())

            task = {
                "id": task_id,
                "group_ids": group_ids,
                "config": config,
                "status": TaskStatus.PENDING.value,
                "priority": priority.value,
                "progress": 0.0,
                "current_group": None,
                "groups_completed": 0,
                "groups_total": len(group_ids),
                "posts_found": 0,
                "comments_found": 0,
                "errors": [],
                "result": None,
                "created_at": datetime.utcnow(),
                "started_at": None,
                "completed_at": None,
            }

            self.tasks[task_id] = task
            self._logger.info(
                f"Created parsing task {task_id} for {len(group_ids)} groups"
            )
            return task_id

        except Exception as e:
            self._logger.error(f"Failed to create task: {str(e)}")
            raise

    def start_task(self, task_id: str) -> bool:
        """Запустить задачу"""
        task = self.tasks.get(task_id)
        if not task:
            raise ValidationError(
                f"Задача {task_id} не найдена", field="task_id"
            )

        if task["status"] != TaskStatus.PENDING.value:
            raise ValidationError(
                f"Задача {task_id} уже запущена или завершена", field="status"
            )

        task["status"] = TaskStatus.RUNNING.value
        task["started_at"] = datetime.utcnow()
        return True

    def complete_task(
        self, task_id: str, result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Завершить задачу успешно"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = TaskStatus.COMPLETED.value
        task["progress"] = 100.0
        task["completed_at"] = datetime.utcnow()
        task["result"] = result
        return True

    def fail_task(self, task_id: str, errors: List[str]) -> bool:
        """Завершить задачу с ошибкой"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["status"] = TaskStatus.FAILED.value
        task["completed_at"] = datetime.utcnow()
        task["errors"].extend(errors)
        return True

    def stop_task(self, task_id: str) -> bool:
        """Остановить задачу"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        if task["status"] in [
            TaskStatus.COMPLETED.value,
            TaskStatus.FAILED.value,
            TaskStatus.STOPPED.value,
        ]:
            return False

        task["status"] = TaskStatus.STOPPED.value
        task["completed_at"] = datetime.utcnow()
        return True

    def update_task_progress(
        self,
        task_id: str,
        groups_completed: int,
        posts_found: int,
        comments_found: int,
        current_group: Optional[int] = None,
    ) -> bool:
        """Обновить прогресс задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["groups_completed"] = groups_completed
        task["posts_found"] += posts_found
        task["comments_found"] += comments_found
        task["current_group"] = current_group

        if task["groups_total"] > 0:
            task["progress"] = (groups_completed / task["groups_total"]) * 100
            task["progress"] = min(task["progress"], 100.0)

        return True

    def add_task_error(self, task_id: str, error: str) -> bool:
        """Добавить ошибку к задаче"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task["errors"].append(error)
        return True

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить задачу по ID"""
        return self.tasks.get(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получить статус задачи"""
        task = self.tasks.get(task_id)
        if not task:
            return None

        duration = None
        if task["started_at"]:
            end_time = task["completed_at"] or datetime.utcnow()
            duration = int((end_time - task["started_at"]).total_seconds())

        return {
            "task_id": task["id"],
            "status": task["status"],
            "progress": task["progress"],
            "current_group": task["current_group"],
            "groups_completed": task["groups_completed"],
            "groups_total": task["groups_total"],
            "posts_found": task["posts_found"],
            "comments_found": task["comments_found"],
            "errors": task["errors"],
            "started_at": task["started_at"],
            "completed_at": task["completed_at"],
            "duration": duration,
        }

    def get_all_tasks(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Получить список задач"""
        tasks = list(self.tasks.values())

        if status_filter:
            tasks = [task for task in tasks if task["status"] == status_filter]

        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        return tasks[offset : offset + limit]

    def get_parser_state(self) -> Dict[str, Any]:
        """Получить общее состояние парсера"""
        active_tasks = sum(
            1
            for task in self.tasks.values()
            if task["status"] == TaskStatus.RUNNING.value
        )
        total_tasks = len(self.tasks)
        total_processed = sum(
            1
            for task in self.tasks.values()
            if task["status"]
            in [
                TaskStatus.COMPLETED.value,
                TaskStatus.FAILED.value,
                TaskStatus.STOPPED.value,
            ]
        )

        total_posts = sum(task["posts_found"] for task in self.tasks.values())
        total_comments = sum(
            task["comments_found"] for task in self.tasks.values()
        )

        return {
            "is_running": active_tasks > 0,
            "active_tasks": active_tasks,
            "queue_size": max(0, total_tasks - active_tasks),
            "total_tasks_processed": total_processed,
            "total_posts_found": total_posts,
            "total_comments_found": total_comments,
            "last_activity": None,
            "started_at": None,
            "uptime_seconds": 0,
            "overall_progress": 0.0,
        }

    def get_parsing_stats(self) -> Dict[str, Any]:
        """Получить статистику парсинга"""
        total_tasks = len(self.tasks)
        completed_tasks = sum(
            1
            for task in self.tasks.values()
            if task["status"] == TaskStatus.COMPLETED.value
        )
        failed_tasks = sum(
            1
            for task in self.tasks.values()
            if task["status"] == TaskStatus.FAILED.value
        )
        running_tasks = sum(
            1
            for task in self.tasks.values()
            if task["status"] == TaskStatus.RUNNING.value
        )

        total_posts = sum(task["posts_found"] for task in self.tasks.values())
        total_comments = sum(
            task["comments_found"] for task in self.tasks.values()
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "total_posts_found": total_posts,
            "total_comments_found": total_comments,
            "total_processing_time": 0,
            "average_task_duration": 0.0,
            "max_groups_per_request": 10000,
            "max_posts_per_request": 1000,
            "max_comments_per_request": 1000,
            "max_users_per_request": 1000,
        }

    def _validate_task_creation_params(
        self,
        group_ids: List[int],
        config: Dict[str, Any],
        priority: TaskPriority,
    ) -> None:
        """Валидация параметров создания задачи"""
        if not isinstance(group_ids, list) or not group_ids:
            raise ValueError("group_ids должен быть непустым списком")

        if len(group_ids) > 10000:
            raise ValueError(
                "group_ids не может содержать более 10000 элементов"
            )

        if len(group_ids) != len(set(group_ids)):
            raise ValueError("group_ids не должен содержать дубликаты")

        for group_id in group_ids:
            if not isinstance(group_id, int):
                raise ValueError("ID группы должен быть целым числом")

        if not isinstance(config, dict):
            raise ValueError("Конфигурация должна быть словарем")

        required_fields = ["max_posts", "max_comments_per_post"]
        for field in required_fields:
            if field not in config:
                raise ValueError(
                    f"Конфигурация должна содержать поле: {field}"
                )

        if not isinstance(priority, TaskPriority):
            raise ValueError("Неверный приоритет задачи")


class ParserService:
    """
    Упрощенный сервис для парсинга данных из VK

    Объединяет все компоненты в одном классе
    """

    def __init__(
        self,
        repository: Optional[TaskRepositoryProtocol] = None,
        vk_api_service: Optional[VKAPIServiceProtocol] = None,
    ):
        """
        Инициализация сервиса парсинга

        Args:
            repository: Репозиторий для работы с задачами
            vk_api_service: VK API сервис
        """
        self.repository = repository

        # Используем VK API сервис если передан, иначе создаем свой
        if vk_api_service:
            self.vk_api = vk_api_service
        else:
            # Создаем экземпляр VK API сервиса для внутренних вызовов
            from ..vk_api.dependencies import create_vk_api_service_sync

            self.vk_api = create_vk_api_service_sync()

        # Инициализируем объединенные компоненты
        self.task_manager = TaskManager()
        self.group_parser = GroupParser(self.vk_api)
        self.error_handler = ServiceErrorHandler()
        self.vk_error_handler = VKAPIErrorHandler()

        # Логгер для сервиса
        self._logger = get_loguru_logger("parser-service")

    async def start_parsing(
        self,
        group_ids: List[int],
        max_posts: int = 100,
        max_comments_per_post: int = 100,
        force_reparse: bool = False,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Запустить парсинг комментариев из групп VK

        Args:
            group_ids: Список ID групп VK
            max_posts: Максимум постов для обработки
            max_comments_per_post: Максимум комментариев на пост
            force_reparse: Принудительно перепарсить
            priority: Приоритет задачи

        Returns:
            Dict[str, Any]: Результат запуска задачи
        """
        try:
            # Валидация входных данных
            self._validate_parsing_params(
                group_ids, max_posts, max_comments_per_post, priority
            )

            # Подготавливаем конфигурацию
            config = {
                "max_posts": max_posts,
                "max_comments_per_post": max_comments_per_post,
                "force_reparse": force_reparse,
            }

            # Создаем задачу через TaskManager
            from .models import TaskPriority

            task_priority = TaskPriority(priority)
            task_id = self.task_manager.create_task(
                group_ids, config, task_priority
            )

            # Запускаем задачу
            self.task_manager.start_task(task_id)

            # Запускаем парсинг в фоновом режиме
            asyncio.create_task(self._execute_parsing_task(task_id))

            # Получаем данные задачи для ответа
            task = self.task_manager.get_task(task_id)
            if not task:
                raise ServiceUnavailableError("Не удалось создать задачу")

            return {
                "task_id": task_id,
                "status": "running",
                "group_ids": group_ids,
                "estimated_time": len(group_ids)
                * 30,  # Примерная оценка: 30 сек на группу
                "created_at": task["created_at"],
                "priority": priority,
            }

        except ValidationError:
            # Перебрасываем ValidationError без изменений
            raise
        except Exception as e:
            self._logger.error(
                f"Failed to start parsing: {str(e)}",
                meta={
                    "error": str(e),
                    "group_ids": group_ids,
                    "operation": "start_parsing",
                },
            )
            raise ServiceUnavailableError(
                f"Не удалось запустить парсинг: {str(e)}"
            )

    def _validate_parsing_params(
        self,
        group_ids: List[int],
        max_posts: int,
        max_comments_per_post: int,
        priority: str,
    ) -> None:
        """Валидация параметров парсинга"""
        try:
            # Валидация лимитов парсинга
            group_count = len(group_ids)

            if not isinstance(group_count, int) or group_count < 1:
                raise ValueError(
                    "Количество групп должно быть положительным целым числом"
                )

            if not isinstance(max_posts, int) or max_posts < 1:
                raise ValueError(
                    "max_posts должен быть положительным целым числом"
                )

            if (
                not isinstance(max_comments_per_post, int)
                or max_comments_per_post < 1
            ):
                raise ValueError(
                    "max_comments_per_post должен быть положительным целым числом"
                )

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
            max_possible_requests = (
                group_count * max_posts * max_comments_per_post
            )

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
        except ValueError as e:
            raise ValidationError(str(e), field="parsing_limits")

        if priority not in ["low", "normal", "high"]:
            raise ValidationError(
                "priority должен быть: low, normal, high", field="priority"
            )

    async def stop_parsing(
        self, task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Остановить парсинг

        Args:
            task_id: ID задачи для остановки (опционально)

        Returns:
            Dict[str, Any]: Результат остановки
        """
        if task_id:
            # Останавливаем конкретную задачу
            if not self.task_manager.get_task(task_id):
                raise ValidationError(
                    f"Задача {task_id} не найдена", field="task_id"
                )

            success = self.task_manager.stop_task(task_id)
            if not success:
                return {
                    "stopped_tasks": [],
                    "message": f"Задача {task_id} уже завершена",
                }

            return {
                "stopped_tasks": [task_id],
                "message": f"Задача {task_id} остановлена",
            }
        else:
            # Останавливаем все активные задачи
            all_tasks = self.task_manager.get_all_tasks()
            stopped_tasks = []

            for task in all_tasks:
                if task["status"] == "running":
                    if self.task_manager.stop_task(task["id"]):
                        stopped_tasks.append(task["id"])

            return {
                "stopped_tasks": stopped_tasks,
                "message": f"Остановлено {len(stopped_tasks)} задач",
            }

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить статус задачи

        Args:
            task_id: ID задачи

        Returns:
            Optional[Dict[str, Any]]: Статус задачи или None если не найдена
        """
        return self.task_manager.get_task_status(task_id)

    async def get_parser_state(self) -> Dict[str, Any]:
        """
        Получить общее состояние парсера

        Returns:
            Dict[str, Any]: Состояние парсера
        """
        return self.task_manager.get_parser_state()

    async def get_tasks_list(
        self,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить список задач

        Args:
            limit: Максимум задач
            offset: Смещение
            status_filter: Фильтр по статусу

        Returns:
            List[Dict[str, Any]]: Список задач
        """
        # Используем TaskManager (repository удален)
        return self.task_manager.get_all_tasks(limit, offset, status_filter)

    async def get_tasks_count(
        self, status_filter: Optional[str] = None
    ) -> int:
        """
        Получить общее количество задач

        Args:
            status_filter: Фильтр по статусу

        Returns:
            int: Общее количество задач
        """
        # Используем TaskManager (repository удален)
        all_tasks = self.task_manager.get_all_tasks()
        if status_filter:
            return len(
                [
                    task
                    for task in all_tasks
                    if task.get("status") == status_filter
                ]
            )
        return len(all_tasks)

    async def get_parsing_stats(self) -> Dict[str, Any]:
        """
        Получить статистику парсинга

        Returns:
            Dict[str, Any]: Статистика парсинга
        """
        return self.task_manager.get_parsing_stats()

    async def parse_group(
        self,
        group_id: int,
        max_posts: int = 100,
        max_comments_per_post: int = 100,
    ) -> Dict[str, Any]:
        """
        Парсинг конкретной группы VK

        Args:
            group_id: ID группы VK (должен быть VK ID, не ID из базы данных)
            max_posts: Максимум постов
            max_comments_per_post: Максимум комментариев на пост

        Returns:
            Dict[str, Any]: Результат парсинга
        """
        return await self.group_parser.parse_group(
            group_id, max_posts, max_comments_per_post
        )

    async def _execute_parsing_task(self, task_id: str) -> None:
        """
        Выполнить задачу парсинга в фоновом режиме

        Args:
            task_id: ID задачи для выполнения
        """
        try:
            task = self.task_manager.get_task(task_id)
            if not task:
                self._logger.error(f"Задача {task_id} не найдена")
                return

            group_ids = task["group_ids"]
            config = task["config"]

            self._logger.info(
                f"Начинаем парсинг задачи {task_id} для {len(group_ids)} групп"
            )

            # Парсим каждую группу
            consecutive_errors = 0
            max_consecutive_errors = (
                10  # Максимум ошибок подряд перед остановкой
            )

            for i, group_id in enumerate(group_ids):
                if task["status"] != "running":
                    self._logger.info(
                        f"Задача {task_id} остановлена, прерываем парсинг"
                    )
                    break

                try:
                    self._logger.info(
                        f"Парсинг группы {group_id} ({i+1}/{len(group_ids)})"
                    )

                    # Выполняем парсинг группы
                    group_result = await self.group_parser.parse_group(
                        group_id=group_id,
                        max_posts=config["max_posts"],
                        max_comments_per_post=config["max_comments_per_post"],
                    )

                    # Обновляем статистику задачи
                    self.task_manager.update_task_progress(
                        task_id=task_id,
                        groups_completed=i + 1,
                        posts_found=group_result["posts_found"],
                        comments_found=group_result["comments_found"],
                        current_group=group_id,
                    )

                    # Добавляем ошибки если есть
                    for error in group_result.get("errors", []):
                        self.task_manager.add_task_error(task_id, error)

                    consecutive_errors = (
                        0  # Сбрасываем счетчик ошибок при успехе
                    )

                    self._logger.info(
                        f"Группа {group_id} обработана: {group_result['posts_found']} постов, {group_result['comments_found']} комментариев"
                    )

                except Exception as e:
                    consecutive_errors += 1
                    error_msg = f"Ошибка парсинга группы {group_id}: {str(e)}"
                    self._logger.error(error_msg)
                    self.task_manager.add_task_error(task_id, error_msg)

                    # Если слишком много ошибок подряд, останавливаем парсинг
                    if consecutive_errors >= max_consecutive_errors:
                        self._logger.error(
                            f"Слишком много ошибок подряд ({consecutive_errors}), останавливаем парсинг"
                        )
                        self.task_manager.fail_task(
                            task_id,
                            [
                                f"Парсинг остановлен из-за {consecutive_errors} ошибок подряд"
                            ],
                        )
                        break

                # Добавляем задержку между группами для соблюдения rate limits
                if i < len(group_ids) - 1:  # Не ждем после последней группы
                    await asyncio.sleep(0.6)  # 600ms задержка между группами

            # Завершаем задачу
            if task["status"] == "running":
                self.task_manager.complete_task(task_id)
                self._logger.info(f"Задача {task_id} завершена успешно")

        except Exception as e:
            self._logger.error(
                f"Критическая ошибка выполнения задачи {task_id}: {str(e)}"
            )
            self.task_manager.fail_task(
                task_id, [f"Критическая ошибка: {str(e)}"]
            )


# Экспорт
__all__ = [
    "ParserService",
]
