"""
ParsingManager - сервис для управления задачами парсинга через ARQ

Принципы SOLID:
- Single Responsibility: только управление задачами парсинга
- Open/Closed: легко добавлять новые типы задач
- Liskov Substitution: можно заменить на другую систему очередей
- Interface Segregation: чистый интерфейс для управления задачами
- Dependency Inversion: зависит от абстракций (AsyncSession, ARQ)
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vk_group import VKGroup

logger = logging.getLogger(__name__)


class ParsingManager:
    """
    Сервис для управления задачами парсинга через ARQ.

    Предоставляет высокоуровневый интерфейс для:
    - Запуска задач парсинга групп
    - Отслеживания статуса задач
    - Управления очередью задач
    - Обработки результатов парсинга
    """

    def __init__(self, db: AsyncSession, arq_client=None):
        """
        Инициализация менеджера парсинга.

        Args:
            db: Асинхронная сессия базы данных
            arq_client: Клиент ARQ для работы с очередями (опционально)
        """
        self.db = db
        self.arq = arq_client

    async def start_parsing_task(
        self, group_id: int, config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Запустить задачу парсинга группы.

        Args:
            group_id: ID группы VK
            config: Конфигурация парсинга

        Returns:
            ID запущенной задачи
        """
        try:
            # Проверяем существование группы
            group = await self._get_group_by_vk_id(group_id)
            if not group:
                raise ValueError(f"Group with VK ID {group_id} not found")

            if not group.is_active:
                raise ValueError(f"Group {group_id} is not active")

            # Генерируем ID задачи
            task_id = str(uuid4())

            # Конфигурация по умолчанию
            default_config = {
                "max_posts": 100,
                "max_comments_per_post": 100,
                "force_reparse": False,
                "priority": "normal",
            }

            # Объединяем с пользовательской конфигурацией
            if config:
                default_config.update(config)

            logger.info(
                f"Starting parsing task for group {group_id}",
                task_id=task_id,
                group_id=group_id,
                config=default_config,
            )

            # Если есть ARQ клиент, отправляем задачу в очередь
            if self.arq:
                await self.arq.enqueue_job(
                    "parse_group",
                    group_id=group_id,
                    config=default_config,
                    task_id=task_id,
                )

                logger.info(
                    f"Task {task_id} enqueued for group {group_id}",
                    task_id=task_id,
                    group_id=group_id,
                )
            else:
                logger.warning(
                    "No ARQ client available, task will not be executed",
                    task_id=task_id,
                    group_id=group_id,
                )

            return task_id

        except Exception as e:
            logger.error(
                f"Error starting parsing task for group {group_id}: {e}"
            )
            raise

    async def get_parsing_status(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи парсинга.

        Args:
            task_id: ID задачи

        Returns:
            Информация о статусе задачи
        """
        try:
            if not self.arq:
                return {
                    "task_id": task_id,
                    "status": "unknown",
                    "message": "ARQ client not available",
                    "progress": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

            # Получаем информацию о задаче из ARQ
            task_info = await self.arq.get_job_info(task_id)

            if task_info:
                return {
                    "task_id": task_id,
                    "status": task_info.get("status", "unknown"),
                    "progress": task_info.get("progress", 0),
                    "result": task_info.get("result"),
                    "error": task_info.get("error"),
                    "created_at": task_info.get("created_at"),
                    "started_at": task_info.get("started_at"),
                    "finished_at": task_info.get("finished_at"),
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "not_found",
                    "message": "Task not found",
                    "progress": 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting status for task {task_id}: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "message": str(e),
                "progress": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

    async def cancel_parsing_task(self, task_id: str) -> bool:
        """
        Отменить задачу парсинга.

        Args:
            task_id: ID задачи

        Returns:
            True если задача отменена, False иначе
        """
        try:
            if not self.arq:
                logger.warning(
                    f"Cannot cancel task {task_id}: ARQ client not available"
                )
                return False

            # Отменяем задачу через ARQ
            success = await self.arq.cancel_job(task_id)

            if success:
                logger.info(f"Task {task_id} cancelled successfully")
            else:
                logger.warning(f"Failed to cancel task {task_id}")

            return success

        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False

    async def get_active_tasks(self) -> List[Dict[str, Any]]:
        """
        Получить список активных задач парсинга.

        Returns:
            Список активных задач
        """
        try:
            if not self.arq:
                logger.warning(
                    "Cannot get active tasks: ARQ client not available"
                )
                return []

            # Получаем все активные задачи
            active_jobs = await self.arq.get_active_jobs()

            tasks = []
            for job in active_jobs:
                tasks.append(
                    {
                        "task_id": job.get("job_id"),
                        "function": job.get("function"),
                        "args": job.get("args"),
                        "status": "running",
                        "created_at": job.get("created_at"),
                    }
                )

            logger.info(f"Found {len(tasks)} active tasks")
            return tasks

        except Exception as e:
            logger.error(f"Error getting active tasks: {e}")
            return []

    async def start_bulk_parsing(
        self, group_ids: List[int], config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Запустить парсинг нескольких групп.

        Args:
            group_ids: Список ID групп VK
            config: Конфигурация парсинга

        Returns:
            Результат запуска задач
        """
        try:
            if not group_ids:
                return {
                    "total_groups": 0,
                    "started_tasks": 0,
                    "failed_groups": [],
                    "tasks": [],
                }

            logger.info(f"Starting bulk parsing for {len(group_ids)} groups")

            started_tasks = []
            failed_groups = []

            for group_id in group_ids:
                try:
                    task_id = await self.start_parsing_task(group_id, config)
                    started_tasks.append(
                        {"group_id": group_id, "task_id": task_id}
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to start task for group {group_id}: {e}"
                    )
                    failed_groups.append(
                        {"group_id": group_id, "error": str(e)}
                    )

            result = {
                "total_groups": len(group_ids),
                "started_tasks": len(started_tasks),
                "failed_groups": failed_groups,
                "tasks": started_tasks,
                "success_rate": round(
                    len(started_tasks) / len(group_ids) * 100, 2
                ),
            }

            logger.info(
                f"Bulk parsing completed: {len(started_tasks)}/{len(group_ids)} tasks started",
                total_groups=len(group_ids),
                started_tasks=len(started_tasks),
                failed_groups=len(failed_groups),
            )

            return result

        except Exception as e:
            logger.error(f"Error in bulk parsing: {e}")
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """
        Получить статус системы парсинга.

        Returns:
            Информация о состоянии системы
        """
        try:
            # Получаем активные задачи
            active_tasks = await self.get_active_tasks()

            # Получаем информацию о ARQ
            arq_status = "available" if self.arq else "unavailable"

            # Получаем статистику по группам
            groups_query = select(VKGroup).where(VKGroup.is_active == True)
            groups_result = await self.db.execute(groups_query)
            active_groups = groups_result.scalars().all()

            status = {
                "arq_status": arq_status,
                "active_tasks_count": len(active_tasks),
                "active_groups_count": len(active_groups),
                "active_tasks": active_tasks[:10],  # Первые 10 задач
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            logger.info(
                "System status retrieved",
                arq_status=arq_status,
                active_tasks=len(active_tasks),
                active_groups=len(active_groups),
            )

            return status

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "arq_status": "error",
                "active_tasks_count": 0,
                "active_groups_count": 0,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _get_group_by_vk_id(self, vk_id: int) -> Optional[VKGroup]:
        """
        Получить группу по VK ID.

        Args:
            vk_id: VK ID группы

        Returns:
            Объект группы или None
        """
        try:
            query = select(VKGroup).where(VKGroup.vk_id == vk_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting group by VK ID {vk_id}: {e}")
            return None
