"""
Задачи уведомлений
"""

import json
from typing import Any, Dict, List, Optional

from celery import Task
from celery.exceptions import Retry

from ..common.celery_config import celery_app
from ..common.logging import get_logger
from ..common.redis_client import redis_client

logger = get_logger(__name__)


class NotificationTask(Task):
    """Базовый класс для задач уведомлений"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Обработчик успешного выполнения"""
        logger.info(
            f"Notification task {self.name} completed successfully",
            task_id=task_id,
            args=args,
            kwargs=kwargs
        )
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Обработчик ошибки выполнения"""
        logger.error(
            f"Notification task {self.name} failed",
            task_id=task_id,
            args=args,
            kwargs=kwargs,
            error=str(exc),
            traceback=str(einfo)
        )


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="notifications.send_email",
    queue="notifications",
    max_retries=3,
    default_retry_delay=30
)
def send_email_task(
    self,
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> Dict[str, Any]:
    """Задача отправки email"""
    try:
        logger.info(f"Sending email to {to_email}")
        
        # Здесь должна быть логика отправки email
        # Например, через SMTP, SendGrid, AWS SES и т.д.
        
        # Имитация отправки
        email_data = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "sent_at": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем в Redis для истории
        redis_client.lpush(
            f"email_history:{to_email}",
            json.dumps(email_data)
        )
        
        # Ограничиваем историю
        redis_client.ltrim(f"email_history:{to_email}", 0, 99)
        
        logger.info(f"Email sent to {to_email}")
        
        return {
            "status": "sent",
            "to": to_email,
            "subject": subject,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Email sending failed to {to_email}: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="notifications.send_websocket",
    queue="notifications",
    max_retries=3,
    default_retry_delay=30
)
def send_websocket_task(
    self,
    user_id: int,
    message: str,
    notification_type: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Задача отправки WebSocket уведомления"""
    try:
        logger.info(f"Sending WebSocket notification to user {user_id}")
        
        # Здесь должна быть логика отправки через WebSocket
        # Например, через Socket.IO, FastAPI WebSocket и т.д.
        
        notification_data = {
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "data": data or {},
            "timestamp": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем в Redis для отправки через WebSocket
        redis_client.lpush(
            f"websocket_queue:{user_id}",
            json.dumps(notification_data)
        )
        
        # Сохраняем в истории уведомлений
        redis_client.lpush(
            f"notifications:{user_id}",
            json.dumps(notification_data)
        )
        
        # Ограничиваем историю
        redis_client.ltrim(f"notifications:{user_id}", 0, 99)
        
        logger.info(f"WebSocket notification queued for user {user_id}")
        
        return {
            "status": "queued",
            "user_id": user_id,
            "message": message,
            "type": notification_type,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"WebSocket notification failed for user {user_id}: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="notifications.send_push",
    queue="notifications",
    max_retries=3,
    default_retry_delay=30
)
def send_push_task(
    self,
    user_id: int,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Задача отправки push-уведомления"""
    try:
        logger.info(f"Sending push notification to user {user_id}")
        
        # Здесь должна быть логика отправки push-уведомлений
        # Например, через Firebase Cloud Messaging, Apple Push Notifications и т.д.
        
        push_data = {
            "user_id": user_id,
            "title": title,
            "body": body,
            "data": data or {},
            "sent_at": self.request.utcnow().isoformat(),
            "task_id": self.request.id
        }
        
        # Сохраняем в Redis для отправки
        redis_client.lpush(
            f"push_queue:{user_id}",
            json.dumps(push_data)
        )
        
        # Сохраняем в истории
        redis_client.lpush(
            f"push_history:{user_id}",
            json.dumps(push_data)
        )
        
        # Ограничиваем историю
        redis_client.ltrim(f"push_history:{user_id}", 0, 99)
        
        logger.info(f"Push notification queued for user {user_id}")
        
        return {
            "status": "queued",
            "user_id": user_id,
            "title": title,
            "body": body,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Push notification failed for user {user_id}: {e}")
        raise self.retry(exc=e, countdown=30)


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="notifications.send_bulk",
    queue="notifications",
    max_retries=3,
    default_retry_delay=60
)
def send_bulk_notification_task(
    self,
    user_ids: List[int],
    message: str,
    notification_type: str = "info",
    channels: List[str] = None
) -> Dict[str, Any]:
    """Задача массовой отправки уведомлений"""
    try:
        logger.info(f"Sending bulk notification to {len(user_ids)} users")
        
        if channels is None:
            channels = ["websocket"]
        
        results = []
        for user_id in user_ids:
            try:
                user_results = {}
                
                # Отправляем через WebSocket
                if "websocket" in channels:
                    ws_result = send_websocket_task.delay(
                        user_id=user_id,
                        message=message,
                        notification_type=notification_type
                    )
                    user_results["websocket"] = ws_result.id
                
                # Отправляем push-уведомление
                if "push" in channels:
                    push_result = send_push_task.delay(
                        user_id=user_id,
                        title=notification_type.title(),
                        body=message
                    )
                    user_results["push"] = push_result.id
                
                # Отправляем email
                if "email" in channels:
                    # Здесь должна быть логика получения email пользователя
                    email_result = send_email_task.delay(
                        to_email=f"user{user_id}@example.com",
                        subject=f"Notification: {notification_type.title()}",
                        body=message
                    )
                    user_results["email"] = email_result.id
                
                results.append({
                    "user_id": user_id,
                    "status": "queued",
                    "channels": user_results
                })
                
            except Exception as e:
                logger.error(f"Failed to send notification to user {user_id}: {e}")
                results.append({
                    "user_id": user_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        successful = len([r for r in results if r["status"] == "queued"])
        
        logger.info(
            f"Bulk notification completed",
            total_users=len(user_ids),
            successful=successful,
            failed=len(user_ids) - successful
        )
        
        return {
            "status": "completed",
            "total_users": len(user_ids),
            "successful": successful,
            "failed": len(user_ids) - successful,
            "results": results,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Bulk notification failed: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(
    bind=True,
    base=NotificationTask,
    name="notifications.cleanup_old_notifications",
    queue="low_priority",
    max_retries=3,
    default_retry_delay=60
)
def cleanup_old_notifications_task(
    self,
    days_old: int = 30
) -> Dict[str, Any]:
    """Задача очистки старых уведомлений"""
    try:
        logger.info(f"Cleaning up notifications older than {days_old} days")
        
        # Паттерны для поиска старых уведомлений
        patterns = [
            "notifications:*",
            "email_history:*",
            "push_history:*",
            "websocket_queue:*"
        ]
        
        total_cleaned = 0
        for pattern in patterns:
            keys = redis_client.keys(pattern)
            for key in keys:
                # Проверяем возраст данных
                ttl = redis_client.ttl(key)
                if ttl > days_old * 86400:  # Конвертируем дни в секунды
                    redis_client.delete(key)
                    total_cleaned += 1
        
        logger.info(
            f"Notification cleanup completed",
            days_old=days_old,
            keys_cleaned=total_cleaned
        )
        
        return {
            "status": "completed",
            "days_old": days_old,
            "keys_cleaned": total_cleaned,
            "task_id": self.request.id
        }
        
    except Exception as e:
        logger.error(f"Notification cleanup failed: {e}")
        raise self.retry(exc=e, countdown=60)
