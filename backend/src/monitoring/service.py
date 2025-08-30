"""
Сервис для работы с мониторингом групп VK

Содержит бизнес-логику для операций мониторинга и управления задачами
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import asyncio
import uuid

from ..exceptions import (
    ValidationError,
    NotFoundError,
    ServiceUnavailableError,
)
from .models import MonitoringRepository, MonitoringTask
from ..parser.client import VKAPIClient


class MonitoringService:
    """
    Сервис для мониторинга групп VK

    Реализует бизнес-логику для автоматического мониторинга групп VK,
    планирования задач и управления результатами
    """

    def __init__(
        self,
        repository: MonitoringRepository,
        parser_client: VKAPIClient = None,
    ):
        self.repository = repository
        self.parser_client = parser_client or VKAPIClient()
        self._active_tasks = {}  # task_id -> asyncio.Task
        self._monitoring_queue = asyncio.Queue(maxsize=1000)

    async def create_monitoring(
        self,
        group_id: int,
        group_name: str,
        owner_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Создать новый мониторинг группы

        Args:
            group_id: ID группы VK
            group_name: Название группы
            owner_id: ID владельца
            config: Конфигурация мониторинга

        Returns:
            Dict[str, Any]: Созданный мониторинг
        """
        # Валидация входных данных
        if not group_name or not group_name.strip():
            raise ValidationError(
                "Название группы обязательно", field="group_name"
            )

        if not owner_id or not owner_id.strip():
            raise ValidationError("ID владельца обязателен", field="owner_id")

        # Проверяем, что мониторинг для этой группы не существует
        existing = await self.repository.get_by_group_id(group_id)
        if existing:
            raise ValidationError(
                f"Мониторинг для группы {group_id} уже существует",
                field="group_id",
            )

        # Создаем конфигурацию по умолчанию
        default_config = {
            "interval_minutes": 5,
            "max_concurrent_groups": 10,
            "enable_auto_retry": True,
            "max_retries": 3,
            "timeout_seconds": 30,
            "enable_notifications": False,
            "notification_channels": [],
        }

        if config:
            default_config.update(config)

        # Создаем мониторинг
        monitoring_data = {
            "id": str(uuid.uuid4()),
            "group_id": group_id,
            "group_name": group_name.strip(),
            "owner_id": owner_id.strip(),
            "status": "active",
            "config": default_config,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_run_at": None,
            "next_run_at": datetime.utcnow(),
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "average_processing_time": 0.0,
        }

        monitoring = await self.repository.create(monitoring_data)

        # Запускаем задачу мониторинга
        await self._schedule_monitoring_task(monitoring["id"])

        return monitoring

    async def get_monitoring(
        self, monitoring_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получить мониторинг по ID

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Optional[Dict[str, Any]]: Мониторинг или None
        """
        return await self.repository.get_by_id(monitoring_id)

    async def get_user_monitorings(
        self,
        owner_id: str,
        limit: int = 50,
        offset: int = 0,
        status_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получить мониторинги пользователя

        Args:
            owner_id: ID владельца
            limit: Максимум записей
            offset: Смещение
            status_filter: Фильтр по статусу

        Returns:
            List[Dict[str, Any]]: Список мониторингов
        """
        return await self.repository.get_by_owner(
            owner_id=owner_id,
            limit=limit,
            offset=offset,
            status_filter=status_filter,
        )

    async def update_monitoring(
        self, monitoring_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновить мониторинг

        Args:
            monitoring_id: ID мониторинга
            update_data: Данные для обновления

        Returns:
            Dict[str, Any]: Обновленный мониторинг
        """
        # Проверяем существование
        monitoring = await self.repository.get_by_id(monitoring_id)
        if not monitoring:
            raise NotFoundError("Мониторинг", monitoring_id)

        # Валидация статуса
        if "status" in update_data:
            valid_statuses = ["active", "paused", "stopped"]
            if update_data["status"] not in valid_statuses:
                raise ValidationError(
                    f"Неверный статус. Допустимые: {', '.join(valid_statuses)}",
                    field="status",
                )

        # Обновляем данные
        monitoring["updated_at"] = datetime.utcnow()
        monitoring.update(update_data)

        # Сохраняем
        updated = await self.repository.update(monitoring_id, update_data)

        # Перепланируем задачу если статус изменился
        if "status" in update_data:
            if update_data["status"] == "active":
                await self._schedule_monitoring_task(monitoring_id)
            else:
                await self._cancel_monitoring_task(monitoring_id)

        return updated

    async def delete_monitoring(self, monitoring_id: str) -> bool:
        """
        Удалить мониторинг

        Args:
            monitoring_id: ID мониторинга

        Returns:
            bool: True если удален
        """
        # Отменяем задачу
        await self._cancel_monitoring_task(monitoring_id)

        # Удаляем из репозитория
        return await self.repository.delete(monitoring_id)

    async def start_monitoring(self, monitoring_id: str) -> Dict[str, Any]:
        """
        Запустить мониторинг

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Dict[str, Any]: Результат запуска
        """
        return await self.update_monitoring(
            monitoring_id, {"status": "active"}
        )

    async def stop_monitoring(self, monitoring_id: str) -> Dict[str, Any]:
        """
        Остановить мониторинг

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Dict[str, Any]: Результат остановки
        """
        return await self.update_monitoring(
            monitoring_id, {"status": "stopped"}
        )

    async def pause_monitoring(self, monitoring_id: str) -> Dict[str, Any]:
        """
        Приостановить мониторинг

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Dict[str, Any]: Результат приостановки
        """
        return await self.update_monitoring(
            monitoring_id, {"status": "paused"}
        )

    async def bulk_action(
        self,
        monitoring_ids: List[str],
        action: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Массовое действие с мониторингами

        Args:
            monitoring_ids: Список ID мониторингов
            action: Действие (start, stop, pause, resume)
            reason: Причина действия

        Returns:
            Dict[str, Any]: Результат массового действия
        """
        valid_actions = ["start", "stop", "pause", "resume"]
        if action not in valid_actions:
            raise ValidationError(
                f"Неверное действие. Допустимые: {', '.join(valid_actions)}",
                field="action",
            )

        successful = 0
        errors = []

        for monitoring_id in monitoring_ids:
            try:
                if action == "start":
                    await self.start_monitoring(monitoring_id)
                elif action == "stop":
                    await self.stop_monitoring(monitoring_id)
                elif action == "pause":
                    await self.pause_monitoring(monitoring_id)
                elif action == "resume":
                    await self.start_monitoring(monitoring_id)

                successful += 1
            except Exception as e:
                errors.append(
                    {"monitoring_id": monitoring_id, "error": str(e)}
                )

        return {
            "successful": successful,
            "failed": len(errors),
            "errors": errors,
        }

    async def run_monitoring_cycle(self, monitoring_id: str) -> Dict[str, Any]:
        """
        Выполнить цикл мониторинга

        Args:
            monitoring_id: ID мониторинга

        Returns:
            Dict[str, Any]: Результат мониторинга
        """
        monitoring = await self.repository.get_by_id(monitoring_id)
        if not monitoring:
            raise NotFoundError("Мониторинг", monitoring_id)

        if monitoring["status"] != "active":
            raise ValidationError("Мониторинг не активен")

        started_at = datetime.utcnow()

        try:
            # Выполняем парсинг группы
            result = await self.parser_client.get_wall_posts(
                owner_id=str(monitoring["group_id"]),
                count=100,  # Ограничиваем для мониторинга
            )

            posts_found = len(result.get("items", []))
            comments_found = 0

            # Для каждого поста получаем комментарии
            for post in result.get("items", [])[:10]:  # Первые 10 постов
                try:
                    comments = await self.parser_client.get_comments(
                        owner_id=str(monitoring["group_id"]),
                        post_id=str(post["id"]),
                        count=50,
                    )
                    comments_found += len(comments.get("items", []))
                except Exception:
                    # Игнорируем ошибки отдельных постов
                    pass

            completed_at = datetime.utcnow()
            processing_time = (completed_at - started_at).total_seconds()

            # Создаем результат
            result_data = {
                "monitoring_id": monitoring_id,
                "group_id": monitoring["group_id"],
                "posts_found": posts_found,
                "comments_found": comments_found,
                "keywords_found": [],  # Заглушка для ключевых слов
                "processing_time": processing_time,
                "errors": [],
                "started_at": started_at,
                "completed_at": completed_at,
            }

            await self.repository.create_result(result_data)

            # Обновляем статистику мониторинга
            await self._update_monitoring_stats(
                monitoring_id, True, processing_time
            )

            # Перепланируем следующий запуск
            await self._schedule_monitoring_task(monitoring_id)

            return result_data

        except Exception as e:
            # Обновляем статистику с ошибкой
            await self._update_monitoring_stats(monitoring_id, False, 0)

            # Создаем результат с ошибкой
            error_result = {
                "monitoring_id": monitoring_id,
                "group_id": monitoring["group_id"],
                "posts_found": 0,
                "comments_found": 0,
                "keywords_found": [],
                "processing_time": (
                    datetime.utcnow() - started_at
                ).total_seconds(),
                "errors": [str(e)],
                "started_at": started_at,
                "completed_at": datetime.utcnow(),
            }

            await self.repository.create_result(error_result)

            # Перепланируем следующий запуск (с задержкой при ошибке)
            await self._schedule_monitoring_task(
                monitoring_id, delay_minutes=5
            )

            raise ServiceUnavailableError(f"Ошибка мониторинга: {str(e)}")

    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """
        Получить общую статистику мониторинга

        Returns:
            Dict[str, Any]: Статистика мониторинга
        """
        return await self.repository.get_stats()

    async def get_monitoring_health(self) -> Dict[str, Any]:
        """
        Проверить здоровье системы мониторинга

        Returns:
            Dict[str, Any]: Состояние здоровья
        """
        active_tasks = len(
            [t for t in self._active_tasks.values() if not t.done()]
        )
        pending_tasks = self._monitoring_queue.qsize()

        # Считаем неудачные задачи за последний час
        failed_last_hour = await self.repository.count_failed_last_hour()

        return {
            "is_healthy": True,  # Заглушка
            "active_monitorings": active_tasks,
            "pending_tasks": pending_tasks,
            "failed_tasks_last_hour": failed_last_hour,
            "average_response_time": 5.0,  # Заглушка
            "redis_connected": True,  # Заглушка
            "database_connected": True,  # Заглушка
            "last_health_check": datetime.utcnow(),
        }

    async def _schedule_monitoring_task(
        self, monitoring_id: str, delay_minutes: Optional[int] = None
    ):
        """
        Запланировать задачу мониторинга

        Args:
            monitoring_id: ID мониторинга
            delay_minutes: Задержка в минутах
        """
        monitoring = await self.repository.get_by_id(monitoring_id)
        if not monitoring or monitoring["status"] != "active":
            return

        # Отменяем предыдущую задачу
        await self._cancel_monitoring_task(monitoring_id)

        # Вычисляем задержку
        if delay_minutes is None:
            delay_minutes = monitoring["config"]["interval_minutes"]

        delay_seconds = delay_minutes * 60

        # Создаем задачу
        task = asyncio.create_task(
            self._delayed_monitoring_task(monitoring_id, delay_seconds)
        )
        self._active_tasks[monitoring_id] = task

        # Обновляем время следующего запуска
        next_run = datetime.utcnow() + timedelta(seconds=delay_seconds)
        await self.repository.update(monitoring_id, {"next_run_at": next_run})

    async def _cancel_monitoring_task(self, monitoring_id: str):
        """
        Отменить задачу мониторинга

        Args:
            monitoring_id: ID мониторинга
        """
        if monitoring_id in self._active_tasks:
            self._active_tasks[monitoring_id].cancel()
            del self._active_tasks[monitoring_id]

    async def _delayed_monitoring_task(self, monitoring_id: str, delay: int):
        """
        Отложенная задача мониторинга

        Args:
            monitoring_id: ID мониторинга
            delay: Задержка в секундах
        """
        try:
            await asyncio.sleep(delay)
            await self.run_monitoring_cycle(monitoring_id)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Логируем ошибку
            print(f"Error in monitoring task {monitoring_id}: {e}")

    async def _update_monitoring_stats(
        self, monitoring_id: str, success: bool, processing_time: float
    ):
        """
        Обновить статистику мониторинга

        Args:
            monitoring_id: ID мониторинга
            success: Успешность выполнения
            processing_time: Время обработки
        """
        monitoring = await self.repository.get_by_id(monitoring_id)
        if not monitoring:
            return

        # Обновляем счетчики
        monitoring["total_runs"] += 1
        monitoring["last_run_at"] = datetime.utcnow()

        if success:
            monitoring["successful_runs"] += 1
        else:
            monitoring["failed_runs"] += 1

        # Обновляем среднее время обработки
        if monitoring["average_processing_time"] == 0:
            monitoring["average_processing_time"] = processing_time
        else:
            total_time = monitoring["average_processing_time"] * (
                monitoring["total_runs"] - 1
            )
            monitoring["average_processing_time"] = (
                total_time + processing_time
            ) / monitoring["total_runs"]

        await self.repository.update(
            monitoring_id,
            {
                "total_runs": monitoring["total_runs"],
                "successful_runs": monitoring["successful_runs"],
                "failed_runs": monitoring["failed_runs"],
                "average_processing_time": monitoring[
                    "average_processing_time"
                ],
                "last_run_at": monitoring["last_run_at"],
            },
        )


# Экспорт
__all__ = [
    "MonitoringService",
]
