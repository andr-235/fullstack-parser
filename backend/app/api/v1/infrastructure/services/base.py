"""
Базовые классы для Infrastructure Services (DDD Infrastructure Layer)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta


class InfrastructureService(ABC):
    """Базовый класс для Infrastructure Services"""

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья сервиса"""
        pass


class CacheService(InfrastructureService):
    """
    Сервис кеширования (DDD Infrastructure Service)

    Предоставляет унифицированный интерфейс для работы с кешем,
    скрывая детали реализации (Redis, Memcached, etc.)
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кеш"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Удалить значение из кеша"""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        pass

    @abstractmethod
    async def expire(self, key: str, ttl: int) -> bool:
        """Установить время жизни ключа"""
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> int:
        """Удалить все ключи по паттерну"""
        pass


class ExternalAPIService(InfrastructureService):
    """
    Базовый класс для внешних API сервисов

    Предоставляет унифицированный интерфейс для работы с внешними API,
    включая обработку ошибок, retry логику и rate limiting.
    """

    @abstractmethod
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """GET запрос"""
        pass

    @abstractmethod
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """POST запрос"""
        pass

    @abstractmethod
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """PUT запрос"""
        pass

    @abstractmethod
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE запрос"""
        pass


class NotificationService(InfrastructureService):
    """
    Сервис уведомлений (DDD Infrastructure Service)

    Предоставляет унифицированный интерфейс для отправки уведомлений
    через различные каналы (email, SMS, push, etc.)
    """

    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Отправить email уведомление"""
        pass

    @abstractmethod
    async def send_sms(self, to: str, message: str) -> bool:
        """Отправить SMS уведомление"""
        pass

    @abstractmethod
    async def send_push_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Отправить push уведомление"""
        pass


class BackgroundTaskService(InfrastructureService):
    """
    Сервис фоновых задач (DDD Infrastructure Service)

    Предоставляет унифицированный интерфейс для выполнения задач в фоне,
    включая планирование, мониторинг и обработку результатов.
    """

    @abstractmethod
    async def enqueue_task(
        self,
        task_name: str,
        *args,
        priority: int = 0,
        delay: Optional[int] = None,
        **kwargs
    ) -> str:
        """Добавить задачу в очередь"""
        pass

    @abstractmethod
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Получить статус задачи"""
        pass

    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """Отменить задачу"""
        pass

    @abstractmethod
    async def get_failed_tasks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить список проваленных задач"""
        pass


class MonitoringService(InfrastructureService):
    """
    Сервис мониторинга (DDD Infrastructure Service)

    Предоставляет унифицированный интерфейс для сбора метрик,
    логирования и мониторинга системы.
    """

    @abstractmethod
    async def log_event(
        self,
        event_type: str,
        message: str,
        level: str = "info",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Залогировать событие"""
        pass

    @abstractmethod
    async def increment_counter(
        self,
        metric_name: str,
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Увеличить счетчик метрики"""
        pass

    @abstractmethod
    async def record_histogram(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Записать значение в гистограмму"""
        pass

    @abstractmethod
    async def record_gauge(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Записать значение в gauge"""
        pass
