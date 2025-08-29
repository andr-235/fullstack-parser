"""
ParsingManager - DDD Application Service для управления задачами парсинга

Мигрирован из app/services/parsing_manager.py
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select

from app.models.vk_group import VKGroup


class ParsingManager:
    """
    DDD Application Service для управления задачами парсинга через ARQ.

    Предоставляет высокоуровневый интерфейс для:
    - Запуска задач парсинга групп
    - Отслеживания статуса задач
    - Управления очередью задач
    - Обработки результатов парсинга
    """

    def __init__(self, db=None, arq_client=None):
        """
        Инициализация менеджера парсинга.

        Args:
            db: Асинхронная сессия базы данных
            arq_client: Клиент ARQ для работы с очередями (опционально)
        """
        self.db = db
        self.arq = arq_client
        self.logger = logging.getLogger(__name__)

    # =============== МИГРАЦИЯ ParsingManager В DDD ===============

    async def start_parsing_task_ddd(
        self, group_id: int, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Запустить задачу парсинга группы (мигрировано из ParsingManager)

        Args:
            group_id: ID группы VK
            config: Конфигурация парсинга

        Returns:
            Результат запуска задачи
        """
        try:
            # Проверяем существование группы
            group = await self._get_group_by_vk_id_ddd(group_id)
            if not group:
                return {
                    "started": False,
                    "error": f"Group with VK ID {group_id} not found",
                    "group_id": group_id,
                }

            if not group.is_active:
                return {
                    "started": False,
                    "error": f"Group {group_id} is not active",
                    "group_id": group_id,
                }

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

            self.logger.info(
                f"Starting parsing task for group {group_id}",
                extra={
                    "task_id": task_id,
                    "group_id": group_id,
                    "config": default_config,
                },
            )

            # Если есть ARQ клиент, отправляем задачу в очередь
            if self.arq:
                await self.arq.enqueue_job(
                    "parse_group",
                    group_id=group_id,
                    config=default_config,
                    task_id=task_id,
                )

                self.logger.info(
                    f"Task {task_id} enqueued for group {group_id}",
                    extra={
                        "task_id": task_id,
                        "group_id": group_id,
                        "queue": "parse_group",
                    },
                )

                return {
                    "started": True,
                    "task_id": task_id,
                    "group_id": group_id,
                    "group_name": group.name,
                    "config": default_config,
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                    "status": "queued",
                }
            else:
                # Имитация запуска без ARQ
                return {
                    "started": True,
                    "task_id": task_id,
                    "group_id": group_id,
                    "group_name": group.name,
                    "config": default_config,
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "status": "running",
                    "note": "ARQ client not available - simulated start",
                }

        except Exception as e:
            self.logger.error(f"Error starting parsing task: {e}")
            return {
                "started": False,
                "error": str(e),
                "group_id": group_id,
            }

    async def get_parsing_status_ddd(self, task_id: str) -> Dict[str, Any]:
        """
        Получить статус задачи парсинга (мигрировано из ParsingManager)

        Args:
            task_id: ID задачи

        Returns:
            Статус задачи
        """
        try:
            if not self.arq:
                return {
                    "task_id": task_id,
                    "status": "unknown",
                    "error": "ARQ client not available",
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }

            # Получаем информацию о задаче из ARQ
            job_info = await self.arq.get_job_info(task_id)

            if not job_info:
                return {
                    "task_id": task_id,
                    "status": "not_found",
                    "message": "Task not found",
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }

            # Форматируем результат
            result = {
                "task_id": task_id,
                "status": job_info.get("status", "unknown"),
                "enqueued_at": job_info.get("enqueued_at"),
                "started_at": job_info.get("started_at"),
                "finished_at": job_info.get("finished_at"),
                "result": job_info.get("result"),
                "error": job_info.get("error"),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

            # Добавляем дополнительную информацию
            if result["status"] == "complete":
                result["duration_seconds"] = (
                    (
                        datetime.fromisoformat(result["finished_at"])
                        - datetime.fromisoformat(result["started_at"])
                    ).total_seconds()
                    if result["started_at"] and result["finished_at"]
                    else None
                )

            return result

        except Exception as e:
            self.logger.error(f"Error getting parsing status: {e}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

    async def cancel_parsing_task_ddd(self, task_id: str) -> Dict[str, Any]:
        """
        Отменить задачу парсинга (мигрировано из ParsingManager)

        Args:
            task_id: ID задачи

        Returns:
            Результат отмены
        """
        try:
            if not self.arq:
                return {
                    "cancelled": False,
                    "task_id": task_id,
                    "error": "ARQ client not available",
                }

            # Пытаемся отменить задачу
            success = await self.arq.abort_job(task_id)

            if success:
                self.logger.info(f"Task {task_id} cancelled successfully")
                return {
                    "cancelled": True,
                    "task_id": task_id,
                    "cancelled_at": datetime.now(timezone.utc).isoformat(),
                    "message": "Task cancelled successfully",
                }
            else:
                return {
                    "cancelled": False,
                    "task_id": task_id,
                    "error": "Task could not be cancelled (may be already completed or not found)",
                }

        except Exception as e:
            self.logger.error(f"Error cancelling parsing task: {e}")
            return {
                "cancelled": False,
                "task_id": task_id,
                "error": str(e),
            }

    async def get_active_tasks_ddd(self) -> Dict[str, Any]:
        """
        Получить список активных задач парсинга (мигрировано из ParsingManager)

        Returns:
            Список активных задач
        """
        try:
            if not self.arq:
                return {
                    "tasks": [],
                    "total": 0,
                    "error": "ARQ client not available",
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                }

            # Получаем активные задачи
            active_jobs = await self.arq.get_active_jobs()

            # Форматируем результат
            tasks = []
            for job in active_jobs:
                tasks.append(
                    {
                        "task_id": job.get("job_id"),
                        "function": job.get("function"),
                        "args": job.get("args", {}),
                        "enqueued_at": job.get("enqueued_at"),
                        "started_at": job.get("started_at"),
                    }
                )

            return {
                "tasks": tasks,
                "total": len(tasks),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting active tasks: {e}")
            return {
                "tasks": [],
                "total": 0,
                "error": str(e),
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }

    async def start_bulk_parsing_ddd(
        self, group_ids: List[int], config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Запустить массовый парсинг групп (мигрировано из ParsingManager)

        Args:
            group_ids: Список ID групп VK
            config: Конфигурация парсинга

        Returns:
            Результат запуска массового парсинга
        """
        try:
            if not group_ids:
                return {
                    "started": False,
                    "error": "No group IDs provided",
                    "total_groups": 0,
                }

            # Запускаем задачи для каждой группы
            started_tasks = []
            failed_groups = []

            for group_id in group_ids:
                try:
                    result = await self.start_parsing_task_ddd(
                        group_id, config
                    )
                    if result["started"]:
                        started_tasks.append(
                            {
                                "group_id": group_id,
                                "task_id": result["task_id"],
                                "status": result["status"],
                            }
                        )
                    else:
                        failed_groups.append(
                            {
                                "group_id": group_id,
                                "error": result.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    failed_groups.append(
                        {
                            "group_id": group_id,
                            "error": str(e),
                        }
                    )

            return {
                "started": True,
                "total_groups": len(group_ids),
                "successful_tasks": len(started_tasks),
                "failed_groups": len(failed_groups),
                "tasks": started_tasks,
                "failures": failed_groups,
                "bulk_started_at": datetime.now(timezone.utc).isoformat(),
                "message": f"Bulk parsing started: {len(started_tasks)}/{len(group_ids)} tasks",
            }

        except Exception as e:
            self.logger.error(f"Error starting bulk parsing: {e}")
            return {
                "started": False,
                "error": str(e),
                "total_groups": len(group_ids),
            }

    async def get_system_status_ddd(self) -> Dict[str, Any]:
        """
        Получить статус системы парсинга (мигрировано из ParsingManager)

        Returns:
            Статус системы
        """
        try:
            # Получаем информацию о группах
            total_groups = (
                await self.db.scalar(select(VKGroup)) if self.db else 0
            )
            active_groups = (
                await self.db.scalar(
                    select(VKGroup).where(VKGroup.is_active == True)
                )
                if self.db
                else 0
            )

            # Получаем информацию о задачах
            active_tasks = await self.get_active_tasks_ddd()

            # Формируем статус
            status = {
                "system": "parsing_manager",
                "status": "healthy" if self.arq else "degraded",
                "database_connected": self.db is not None,
                "arq_connected": self.arq is not None,
                "groups": {
                    "total": total_groups,
                    "active": active_groups,
                    "inactive": total_groups - active_groups,
                },
                "tasks": {
                    "active": active_tasks["total"],
                    "active_tasks": active_tasks["tasks"],
                },
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Добавляем предупреждения
            warnings = []
            if not self.arq:
                warnings.append(
                    "ARQ client not available - task queuing disabled"
                )
            if not self.db:
                warnings.append(
                    "Database not connected - group operations disabled"
                )

            if warnings:
                status["warnings"] = warnings

            return status

        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                "system": "parsing_manager",
                "status": "error",
                "error": str(e),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    # =============== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===============

    async def _get_group_by_vk_id_ddd(self, vk_id: int) -> Optional[VKGroup]:
        """
        Получить группу по VK ID
        """
        try:
            if not self.db:
                return None

            query = select(VKGroup).where(VKGroup.vk_id == vk_id)
            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            self.logger.error(f"Error getting group by VK ID {vk_id}: {e}")
            return None
