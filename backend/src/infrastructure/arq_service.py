"""
Сервис для работы с ARQ (асинхронными задачами)

Предоставляет унифицированный интерфейс для управления очередью задач
и интеграции с Redis через ARQ.
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings
from arq.jobs import Job

from ..config import config_service

logger = logging.getLogger(__name__)


class ARQService:
    """
    Сервис для управления асинхронными задачами через ARQ

    Обеспечивает:
    - Создание и управление пулом соединений Redis
    - Добавление задач в очередь
    - Получение статуса и результатов задач
    - Обработку ошибок и повторных попыток
    """

    def __init__(self):
        self._redis_pool: Optional[ArqRedis] = None
        self._is_initialized = False

    async def initialize(self) -> None:
        """
        Инициализация пула соединений Redis для ARQ

        Создает пул соединений на основе настроек из конфигурации
        """
        if self._is_initialized:
            logger.warning("ARQ service уже инициализирован")
            return

        try:
            # Получаем настройки Redis из конфигурации
            redis_url = config_service.redis_url

            # Создаем настройки Redis для ARQ
            redis_settings = RedisSettings.from_dsn(redis_url)

            # Создаем пул соединений
            self._redis_pool = await create_pool(
                redis_settings,
                default_queue_name=config_service.arq_queue_name,
            )

            self._is_initialized = True
            logger.info("✅ ARQ service успешно инициализирован")
            logger.info(f"📋 Очередь: {config_service.arq_queue_name}")
            logger.info(f"🔗 Redis: {redis_url}")

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ARQ service: {e}")
            raise

    async def close(self) -> None:
        """
        Закрытие пула соединений Redis
        """
        if self._redis_pool:
            await self._redis_pool.close()
            self._redis_pool = None
            self._is_initialized = False
            logger.info("🛑 ARQ service закрыт")

    async def enqueue_job(
        self,
        function_name: str,
        *args,
        job_id: Optional[str] = None,
        defer_until: Optional[datetime] = None,
        defer_by: Optional[Union[int, timedelta]] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        Добавление задачи в очередь

        Args:
            function_name: Имя функции для выполнения
            *args: Позиционные аргументы функции
            job_id: Уникальный ID задачи (опционально)
            defer_until: Отложить выполнение до указанного времени
            defer_by: Отложить выполнение на указанное время
            **kwargs: Именованные аргументы функции

        Returns:
            str: ID задачи или None в случае ошибки
        """
        if not self._is_initialized or not self._redis_pool:
            logger.error("ARQ service не инициализирован")
            return None

        try:
            # Подготавливаем параметры для enqueue_job
            enqueue_kwargs = {
                "function": function_name,
                "args": args,
                "kwargs": kwargs,
            }

            if job_id:
                enqueue_kwargs["_job_id"] = job_id

            if defer_until:
                enqueue_kwargs["_defer_until"] = defer_until

            if defer_by:
                enqueue_kwargs["_defer_by"] = defer_by

            # Добавляем задачу в очередь
            job = await self._redis_pool.enqueue_job(**enqueue_kwargs)

            logger.info(
                f"📝 Задача '{function_name}' добавлена в очередь (ID: {job.job_id})"
            )
            return job.job_id

        except Exception as e:
            logger.error(
                f"❌ Ошибка добавления задачи '{function_name}' в очередь: {e}"
            )
            return None

    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение статуса задачи по ID

        Args:
            job_id: ID задачи

        Returns:
            Dict с информацией о задаче или None если задача не найдена
        """
        if not self._is_initialized or not self._redis_pool:
            logger.error("ARQ service не инициализирован")
            return None

        try:
            job = Job(job_id=job_id, redis=self._redis_pool)
            job_info = await job.info()

            if job_info:
                return {
                    "job_id": job_id,
                    "status": job_info.status,
                    "result": job_info.result,
                    "error": job_info.error,
                    "created_at": job_info.created_at,
                    "started_at": job_info.started_at,
                    "finished_at": job_info.finished_at,
                    "function": job_info.function,
                    "args": job_info.args,
                    "kwargs": job_info.kwargs,
                }
            else:
                logger.warning(f"Задача с ID '{job_id}' не найдена")
                return None

        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса задачи '{job_id}': {e}")
            return None

    async def get_job_result(self, job_id: str) -> Optional[Any]:
        """
        Получение результата выполнения задачи

        Args:
            job_id: ID задачи

        Returns:
            Результат выполнения задачи или None
        """
        if not self._is_initialized or not self._redis_pool:
            logger.error("ARQ service не инициализирован")
            return None

        try:
            job = Job(job_id=job_id, redis=self._redis_pool)
            result = await job.result()

            if result is not None:
                logger.info(f"✅ Результат задачи '{job_id}' получен")
                return result
            else:
                logger.warning(f"Результат задачи '{job_id}' еще не готов")
                return None

        except Exception as e:
            logger.error(
                f"❌ Ошибка получения результата задачи '{job_id}': {e}"
            )
            return None

    async def abort_job(self, job_id: str) -> bool:
        """
        Отмена выполнения задачи

        Args:
            job_id: ID задачи

        Returns:
            True если задача успешно отменена, False в противном случае
        """
        if not self._is_initialized or not self._redis_pool:
            logger.error("ARQ service не инициализирован")
            return False

        try:
            job = Job(job_id=job_id, redis=self._redis_pool)
            aborted = await job.abort()

            if aborted:
                logger.info(f"🛑 Задача '{job_id}' успешно отменена")
            else:
                logger.warning(f"Не удалось отменить задачу '{job_id}'")

            return aborted

        except Exception as e:
            logger.error(f"❌ Ошибка отмены задачи '{job_id}': {e}")
            return False

    async def get_queue_info(self) -> Optional[Dict[str, Any]]:
        """
        Получение информации об очереди

        Returns:
            Dict с информацией об очереди или None в случае ошибки
        """
        if not self._is_initialized or not self._redis_pool:
            logger.error("ARQ service не инициализирован")
            return None

        try:
            # Получаем количество задач в очереди
            queued_jobs = await self._redis_pool.queued_jobs()

            # Получаем информацию о выполняемых задачах
            # Note: ARQ не предоставляет прямого способа получить выполняемые задачи,
            # поэтому возвращаем только информацию об очереди
            return {
                "queue_name": config_service.arq_queue_name,
                "queued_jobs_count": len(queued_jobs) if queued_jobs else 0,
                "max_jobs": config_service.arq_max_jobs,
                "job_timeout": config_service.arq_job_timeout,
                "max_tries": config_service.arq_max_tries,
            }

        except Exception as e:
            logger.error(f"❌ Ошибка получения информации об очереди: {e}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Проверка здоровья ARQ сервиса

        Returns:
            Dict с информацией о состоянии сервиса
        """
        # Явно типизируем details, чтобы избежать проблем mypy с вложенной индексацией
        details: Dict[str, Any] = {}
        health_info: Dict[str, Any] = {
            "service": "ARQ",
            "healthy": False,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        try:
            if not self._is_initialized:
                # Безопасно записываем ошибку в типизированный словарь details
                details["error"] = "Service not initialized"
                return health_info

            if not self._redis_pool:
                details["error"] = "Redis pool not available"
                return health_info

            # Проверяем соединение с Redis
            await self._redis_pool.ping()

            # Получаем информацию об очереди
            queue_info = await self.get_queue_info()

            health_info["healthy"] = True
            health_info["details"] = {
                "redis_connected": True,
                "queue_info": queue_info,
                "config": config_service.get_arq_config(),
            }

        except Exception as e:
            details["error"] = str(e)
            logger.error(f"❌ ARQ health check failed: {e}")

        return health_info


# Глобальный экземпляр ARQ сервиса
arq_service = ARQService()
