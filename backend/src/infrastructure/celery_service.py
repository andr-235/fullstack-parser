"""
Сервис для работы с Celery (асинхронными задачами)

Замена ARQ - более надежная система очередей задач.
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from celery.result import AsyncResult
from celery import Celery

from ..config import config_service

logger = logging.getLogger(__name__)


class CeleryService:
    """
    Сервис для управления асинхронными задачами через Celery

    Обеспечивает:
    - Создание и управление соединениями Redis
    - Добавление задач в очередь
    - Получение статуса и результатов задач
    - Обработку ошибок и повторных попыток
    """

    def __init__(self):
        self._celery_app: Optional[Celery] = None
        self._is_initialized = False

    async def initialize(self, celery_app: Celery) -> None:
        """
        Инициализация Celery приложения

        Args:
            celery_app: Экземпляр Celery приложения
        """
        if self._is_initialized:
            logger.warning("Celery service уже инициализирован")
            return

        try:
            self._celery_app = celery_app
            self._is_initialized = True

            logger.info("✅ Celery service успешно инициализирован")
            logger.info(f"📋 Брокер: {celery_app.conf.broker_url}")
            logger.info(f"🔗 Backend: {celery_app.conf.result_backend}")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Celery service: {e}")
            raise

    async def close(self) -> None:
        """
        Закрытие соединений
        """
        if self._is_initialized:
            self._is_initialized = False
            logger.info("🛑 Celery service закрыт")

    def enqueue_job(
        self,
        task_name: str,
        *args,
        countdown: Optional[int] = None,
        eta: Optional[datetime] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Добавление задачи в очередь

        Args:
            task_name: Имя задачи
            *args: Позиционные аргументы
            countdown: Задержка в секундах
            eta: Точное время выполнения
            **kwargs: Именованные аргументы

        Returns:
            str: ID задачи или None в случае ошибки
        """
        if not self._is_initialized or not self._celery_app:
            logger.error("Celery service не инициализирован")
            return None

        try:
            # Подготавливаем параметры
            task_kwargs = {
                "args": args,
                "kwargs": kwargs,
            }

            if countdown:
                task_kwargs["countdown"] = countdown

            if eta:
                task_kwargs["eta"] = eta

            # Добавляем задачу в очередь
            result = self._celery_app.send_task(task_name, **task_kwargs)

            logger.info(
                f"📝 Задача '{task_name}' добавлена в очередь (ID: {result.id})"
            )
            return result.id

        except Exception as e:
            logger.error(
                f"❌ Ошибка добавления задачи '{task_name}' в очередь: {e}"
            )
            return None

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса задачи по ID

        Args:
            job_id: ID задачи

        Returns:
            Dict с информацией о задаче или None если задача не найдена
        """
        if not self._is_initialized or not self._celery_app:
            logger.error("Celery service не инициализирован")
            return None

        try:
            result = AsyncResult(job_id, app=self._celery_app)

            return {
                "job_id": job_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "error": str(result.result) if result.failed() else None,
                "current": result.info if result.info else None,
                "successful": result.successful(),
                "failed": result.failed(),
                "ready": result.ready(),
            }

        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса задачи '{job_id}': {e}")
            return None

    def get_job_result(self, job_id: str, timeout: int = 10) -> Optional[Any]:
        """
        Получение результата выполнения задачи

        Args:
            job_id: ID задачи
            timeout: Таймаут ожидания результата в секундах

        Returns:
            Результат выполнения задачи или None
        """
        if not self._is_initialized or not self._celery_app:
            logger.error("Celery service не инициализирован")
            return None

        try:
            result = AsyncResult(job_id, app=self._celery_app)

            if result.ready():
                return result.result
            else:
                logger.warning(f"Результат задачи '{job_id}' еще не готов")
                return None

        except Exception as e:
            logger.error(
                f"❌ Ошибка получения результата задачи '{job_id}': {e}"
            )
            return None

    def abort_job(self, job_id: str) -> bool:
        """
        Отмена выполнения задачи

        Args:
            job_id: ID задачи

        Returns:
            True если задача успешно отменена, False в противном случае
        """
        if not self._is_initialized or not self._celery_app:
            logger.error("Celery service не инициализирован")
            return False

        try:
            result = AsyncResult(job_id, app=self._celery_app)

            if result.ready():
                logger.warning(
                    f"Задача '{job_id}' уже завершена, отменить нельзя"
                )
                return False

            # Отменяем задачу
            result.revoke(terminate=True)

            logger.info(f"🛑 Задача '{job_id}' успешно отменена")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка отмены задачи '{job_id}': {e}")
            return False

    def get_queue_info(self) -> Optional[Dict[str, Any]]:
        """
        Получение информации об очередях

        Returns:
            Dict с информацией об очередях или None в случае ошибки
        """
        if not self._is_initialized or not self._celery_app:
            logger.error("Celery service не инициализирован")
            return None

        try:
            # Получаем информацию о зарегистрированных задачах
            tasks = list(self._celery_app.tasks.keys())

            return {
                "registered_tasks": tasks,
                "active_queues": (
                    list(self._celery_app.conf.task_queues.keys())
                    if hasattr(self._celery_app.conf, "task_queues")
                    else []
                ),
                "broker_url": self._celery_app.conf.broker_url,
                "result_backend": self._celery_app.conf.result_backend,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка получения информации об очередях: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья Celery сервиса

        Returns:
            Dict с информацией о состоянии сервиса
        """
        health_info: Dict[str, Any] = {
            "service": "Celery",
            "healthy": False,
            "timestamp": datetime.now().isoformat(),
            "details": {},
        }

        try:
            if not self._is_initialized:
                health_info["details"]["error"] = "Service not initialized"
                return health_info

            if not self._celery_app:
                health_info["details"]["error"] = "Celery app not available"
                return health_info

            # Получаем информацию об очередях
            queue_info = self.get_queue_info()

            health_info["healthy"] = True
            health_info["details"] = {
                "queue_info": queue_info,
                "broker_connected": True,
                "registered_tasks_count": (
                    len(self._celery_app.tasks)
                    if hasattr(self._celery_app, "tasks")
                    else 0
                ),
            }

        except Exception as e:
            health_info["details"]["error"] = str(e)
            logger.error(f"❌ Celery health check failed: {e}")

        return health_info


# Глобальный экземпляр Celery сервиса
celery_service = CeleryService()
