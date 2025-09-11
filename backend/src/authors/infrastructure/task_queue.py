"""
Очередь задач для авторов - инфраструктурный слой

Реализация фоновых задач с использованием Celery
"""

from __future__ import annotations
from typing import Optional
import logging

from ..domain.entities import AuthorEntity
from ..domain.interfaces import AuthorTaskQueueInterface

logger = logging.getLogger(__name__)


class AuthorCeleryTaskQueue(AuthorTaskQueueInterface):
    """Celery очередь задач для авторов."""

    def __init__(self, celery_app):
        self.celery = celery_app

    async def send_author_created_notification(self, author: AuthorEntity) -> None:
        """Отправить уведомление о создании автора."""
        try:
            # Отправляем задачу в Celery
            self.celery.send_task(
                'authors.notify_author_created',
                args=[author.to_dict()],
                queue='authors_notifications'
            )
            logger.info(f"Sent author created notification for VK ID: {author.vk_id}")
        except Exception as e:
            logger.error(f"Error sending author created notification: {e}")

    async def send_author_updated_notification(self, author: AuthorEntity) -> None:
        """Отправить уведомление об обновлении автора."""
        try:
            # Отправляем задачу в Celery
            self.celery.send_task(
                'authors.notify_author_updated',
                args=[author.to_dict()],
                queue='authors_notifications'
            )
            logger.info(f"Sent author updated notification for VK ID: {author.vk_id}")
        except Exception as e:
            logger.error(f"Error sending author updated notification: {e}")

    async def schedule_author_photo_update(self, vk_id: int) -> None:
        """Запланировать обновление фото автора."""
        try:
            # Отправляем задачу в Celery с задержкой
            self.celery.send_task(
                'authors.update_author_photo',
                args=[vk_id],
                queue='authors_photo_updates',
                countdown=300  # 5 минут задержки
            )
            logger.info(f"Scheduled photo update for VK ID: {vk_id}")
        except Exception as e:
            logger.error(f"Error scheduling author photo update: {e}")

    async def schedule_author_data_sync(self, vk_id: int) -> None:
        """Запланировать синхронизацию данных автора с VK API."""
        try:
            # Отправляем задачу в Celery
            self.celery.send_task(
                'authors.sync_author_data',
                args=[vk_id],
                queue='authors_data_sync'
            )
            logger.info(f"Scheduled data sync for VK ID: {vk_id}")
        except Exception as e:
            logger.error(f"Error scheduling author data sync: {e}")
