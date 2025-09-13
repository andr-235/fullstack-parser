"""
Базовые задачи Celery
"""

from typing import Any, Dict, List, Optional

from celery import Task
from celery.exceptions import Retry

from .celery_config import celery_app
from .logging import get_logger
from .redis_client import redis_client

logger = get_logger(__name__)


class BaseTask(Task):
    """Базовый класс для задач Celery"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Обработчик успешного выполнения"""
        logger.info(
            f"Task {self.name} completed successfully",
            task_id=task_id,
            args=args,
            kwargs=kwargs
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработчик ошибки выполнения"""
        logger.error(
            f"Task {self.name} failed",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            traceback=str(einfo)
        )
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Обработчик повторной попытки"""
        logger.warning(
            f"Task {self.name} retrying",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            retry_count=self.request.retries
        )


@celery_app.task(
    bind=True,
    base=BaseTask,
    name="common.health_check",
    queue="default"
)
def health_check_task(self) -> Dict[str, Any]:
    """Задача проверки здоровья системы"""
    try:
        # Проверка Redis
        redis_status = redis_client.ping()
        
        return {
            "status": "healthy",
            "redis_connected": redis_status,
            "task_id": self.request.id,
            "worker": self.request.hostname
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise


@celery_app.task(
    bind=True,
    base=BaseTask,
    name="common.cache_cleanup",
    queue="low_priority",
    max_retries=3,
    default_retry_delay=60
)
def cache_cleanup_task(self, pattern: str = "*", ttl_threshold: int = 3600) -> Dict[str, Any]:
    """Задача очистки кеша"""
    try:
        # Получаем все ключи по паттерну
        keys = redis_client.keys(pattern)
        
        cleaned_count = 0
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl > ttl_threshold:
                redis_client.delete(key)
                cleaned_count += 1
        
        return {
            "pattern": pattern,
            "keys_found": len(keys),
            "keys_cleaned": cleaned_count,
            "task_id": self.request.id
        }
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=BaseTask,
    name="common.send_notification",
    queue="notifications",
    max_retries=3,
    default_retry_delay=30
)
def send_notification_task(
    self,
    user_id: int,
    message: str,
    notification_type: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Задача отправки уведомления"""
    try:
        # Здесь должна быть логика отправки уведомления
        # Например, через WebSocket, email, push-уведомления
        
        notification_data = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "data": data or {},
            "timestamp": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем уведомление в Redis для истории
        redis_client.lpush(
            f"notifications:{user_id}",
            json.dumps(notification_data)
        )
        
        # Ограничиваем количество уведомлений в истории
        redis_client.ltrim(f"notifications:{user_id}", 0, 99)
        
        logger.info(
            "Notification sent",
            user_id=user_id,
            message=message,
            type=notification_type
        )
        
        return {
            "status": "sent",
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "task_id": self.request.id
        }
    except Exception as e:
        logger.error(f"Notification sending failed: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=BaseTask,
    name="common.batch_process",
    queue="default",
    max_retries=3,
    default_retry_delay=60
)
def batch_process_task(
    self,
    items: List[Dict[str, Any]],
    process_func: str,
    batch_size: int = 100
) -> Dict[str, Any]:
    """Задача пакетной обработки"""
    try:
        processed_count = 0
        failed_count = 0
        
        # Обрабатываем элементы батчами
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            try:
                # Здесь должна быть логика вызова функции обработки
                # process_func - это строка с именем функции
                logger.info(f"Processing batch {i//batch_size + 1}")
                
                # Имитация обработки
                for item in batch:
                    # Здесь должна быть реальная обработка
                    processed_count += 1
                
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                failed_count += len(batch)
        
        return {
            "total_items": len(items),
            "processed_count": processed_count,
            "failed_count": failed_count,
            "batch_size": batch_size,
            "task_id": self.request.id
        }
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=BaseTask,
    name="common.periodic_cleanup",
    queue="low_priority"
)
def periodic_cleanup_task(self) -> Dict[str, Any]:
    """Периодическая задача очистки"""
    try:
        cleanup_tasks = []
        
        # Очистка старых уведомлений
        cleanup_tasks.append({
            "type": "notifications",
            "pattern": "notifications:*",
            "ttl_threshold": 86400  # 24 часа
        })
        
        # Очистка временных данных
        cleanup_tasks.append({
            "type": "temp_data",
            "pattern": "temp:*",
            "ttl_threshold": 3600  # 1 час
        })
        
        # Очистка кеша
        cleanup_tasks.append({
            "type": "cache",
            "pattern": "cache:*",
            "ttl_threshold": 7200  # 2 часа
        })
        
        total_cleaned = 0
        for task in cleanup_tasks:
            result = cache_cleanup_task.delay(
                pattern=task["pattern"],
                ttl_threshold=task["ttl_threshold"]
            )
            total_cleaned += result.get()["keys_cleaned"]
        
        return {
            "status": "completed",
            "cleanup_tasks": len(cleanup_tasks),
            "total_cleaned": total_cleaned,
            "task_id": self.request.id
        }
    except Exception as e:
        logger.error(f"Periodic cleanup failed: {e}")
        raise


# Регистрируем периодические задачи
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Настройка периодических задач"""
    # Очистка каждые 6 часов
    sender.add_periodic_task(
        21600,  # 6 часов
        periodic_cleanup_task.s(),
        name="periodic_cleanup"
    )
    
    # Проверка здоровья каждые 5 минут
    sender.add_periodic_task(
        300,  # 5 минут
        health_check_task.s(),
        name="health_check"
    )
