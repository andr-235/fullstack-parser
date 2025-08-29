"""
Application Service для системы мониторинга VK групп (DDD)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..domain.monitoring import (
    VKGroupMonitoring,
    MonitoringConfig,
    MonitoringResult,
    MonitoringStats,
    MonitoringStatus,
)
from .base import ApplicationService


class MonitoringApplicationService(ApplicationService):
    """Application Service для работы с мониторингом VK групп"""

    def __init__(self, monitoring_repository=None, vk_api_service=None):
        self.monitoring_repository = monitoring_repository
        self.vk_api_service = vk_api_service

    async def create_monitoring(
        self,
        group_id: int,
        group_name: str,
        owner_id: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> VKGroupMonitoring:
        """Создать мониторинг для VK группы"""
        # Проверить, не существует ли уже мониторинг для этой группы
        existing = await self.monitoring_repository.find_by_group_id(group_id)
        if existing:
            raise ValueError(f"Monitoring already exists for group {group_id}")

        # Создать конфигурацию
        monitoring_config = MonitoringConfig()
        if config:
            monitoring_config = MonitoringConfig(**config)

        # Создать мониторинг
        monitoring = VKGroupMonitoring(
            group_id=group_id,
            group_name=group_name,
            owner_id=owner_id,
        )
        monitoring.config = monitoring_config

        await self.monitoring_repository.save(monitoring)
        return monitoring

    async def get_monitoring(
        self, monitoring_id: str
    ) -> Optional[VKGroupMonitoring]:
        """Получить мониторинг по ID"""
        return await self.monitoring_repository.find_by_id(monitoring_id)

    async def get_monitoring_by_group(
        self, group_id: int
    ) -> Optional[VKGroupMonitoring]:
        """Получить мониторинг по ID группы VK"""
        return await self.monitoring_repository.find_by_group_id(group_id)

    async def get_user_monitorings(
        self,
        owner_id: str,
        page: int = 1,
        size: int = 20,
    ) -> Dict[str, Any]:
        """Получить список мониторингов пользователя"""
        monitorings = await self.monitoring_repository.find_by_owner(owner_id)

        # Пагинация
        total = len(monitorings)
        start_index = (page - 1) * size
        end_index = start_index + size
        paginated_monitorings = monitorings[start_index:end_index]

        return {
            "items": [m.to_dict() for m in paginated_monitorings],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "has_next": page * size < total,
            "has_prev": page > 1,
        }

    async def start_monitoring(self, monitoring_id: str) -> VKGroupMonitoring:
        """Запустить мониторинг"""
        monitoring = await self.monitoring_repository.find_by_id(monitoring_id)
        if not monitoring:
            raise ValueError(f"Monitoring with id {monitoring_id} not found")

        monitoring.start_monitoring()
        await self.monitoring_repository.save(monitoring)
        return monitoring

    async def pause_monitoring(self, monitoring_id: str) -> VKGroupMonitoring:
        """Приостановить мониторинг"""
        monitoring = await self.monitoring_repository.find_by_id(monitoring_id)
        if not monitoring:
            raise ValueError(f"Monitoring with id {monitoring_id} not found")

        monitoring.pause_monitoring()
        await self.monitoring_repository.save(monitoring)
        return monitoring

    async def stop_monitoring(self, monitoring_id: str) -> VKGroupMonitoring:
        """Остановить мониторинг"""
        monitoring = await self.monitoring_repository.find_by_id(monitoring_id)
        if not monitoring:
            raise ValueError(f"Monitoring with id {monitoring_id} not found")

        monitoring.stop_monitoring()
        await self.monitoring_repository.save(monitoring)
        return monitoring

    async def update_config(
        self, monitoring_id: str, config_updates: Dict[str, Any]
    ) -> VKGroupMonitoring:
        """Обновить конфигурацию мониторинга"""
        monitoring = await self.monitoring_repository.find_by_id(monitoring_id)
        if not monitoring:
            raise ValueError(f"Monitoring with id {monitoring_id} not found")

        # Создать новую конфигурацию на основе обновлений
        current_config = monitoring.config
        new_config_dict = {
            "interval_seconds": config_updates.get(
                "interval_seconds", current_config.interval_seconds
            ),
            "max_concurrent_groups": config_updates.get(
                "max_concurrent_groups", current_config.max_concurrent_groups
            ),
            "enable_auto_retry": config_updates.get(
                "enable_auto_retry", current_config.enable_auto_retry
            ),
            "max_retries": config_updates.get(
                "max_retries", current_config.max_retries
            ),
            "timeout_seconds": config_updates.get(
                "timeout_seconds", current_config.timeout_seconds
            ),
            "enable_notifications": config_updates.get(
                "enable_notifications", current_config.enable_notifications
            ),
            "notification_channels": config_updates.get(
                "notification_channels", current_config.notification_channels
            ),
        }

        new_config = MonitoringConfig(**new_config_dict)
        monitoring.update_config(new_config)
        await self.monitoring_repository.save(monitoring)
        return monitoring

    async def delete_monitoring(self, monitoring_id: str) -> bool:
        """Удалить мониторинг"""
        return await self.monitoring_repository.delete(monitoring_id)

    async def execute_monitoring_cycle(
        self, monitoring_id: str
    ) -> MonitoringResult:
        """Выполнить цикл мониторинга"""
        monitoring = await self.monitoring_repository.find_by_id(monitoring_id)
        if not monitoring:
            raise ValueError(f"Monitoring with id {monitoring_id} not found")

        if not monitoring.status.is_active():
            raise ValueError(f"Monitoring is not active: {monitoring.status}")

        # Выполнить мониторинг через VK API
        result = await self._perform_monitoring_cycle(monitoring)

        # Записать результат
        monitoring.record_cycle_result(result)
        await self.monitoring_repository.save(monitoring)

        return result

    async def get_system_stats(
        self, owner_id: Optional[str] = None
    ) -> MonitoringStats:
        """Получить статистику системы мониторинга"""
        # Получить все мониторинги (или только для пользователя)
        if owner_id:
            monitorings = await self.monitoring_repository.find_by_owner(
                owner_id
            )
        else:
            monitorings = await self.monitoring_repository.find_all()

        # Рассчитать статистику
        total_groups = len(monitorings)
        active_groups = len([m for m in monitorings if m.status.is_active()])
        paused_groups = len([m for m in monitorings if m.status.is_paused()])
        error_groups = len(
            [
                m
                for m in monitorings
                if m.status.status == MonitoringStatus.ERROR
            ]
        )

        # Статистика за сегодня
        today = datetime.utcnow().date()
        total_cycles_today = sum(m.total_cycles for m in monitorings)
        successful_cycles_today = sum(m.successful_cycles for m in monitorings)

        # Среднее время обработки (упрощенное)
        avg_processing_time = 0.0
        total_results = sum(1 for m in monitorings if m.last_result)
        if total_results > 0:
            total_time = sum(
                m.last_result.processing_time
                for m in monitorings
                if m.last_result
            )
            avg_processing_time = total_time / total_results

        # Общее количество найденных комментариев и постов
        total_comments = sum(
            m.last_result.comments_found
            for m in monitorings
            if m.last_result
            and m.last_cycle_at
            and m.last_cycle_at.date() == today
        )
        total_posts = sum(
            m.last_result.posts_found
            for m in monitorings
            if m.last_result
            and m.last_cycle_at
            and m.last_cycle_at.date() == today
        )

        return MonitoringStats(
            total_groups=total_groups,
            active_groups=active_groups,
            paused_groups=paused_groups,
            error_groups=error_groups,
            total_cycles_today=total_cycles_today,
            successful_cycles_today=successful_cycles_today,
            average_processing_time=avg_processing_time,
            total_comments_found_today=total_comments,
            total_posts_processed_today=total_posts,
        )

    async def bulk_start_monitoring(
        self, monitoring_ids: List[str]
    ) -> Dict[str, Any]:
        """Массовый запуск мониторинга"""
        successful = []
        failed = []

        for monitoring_id in monitoring_ids:
            try:
                monitoring = await self.start_monitoring(monitoring_id)
                successful.append(monitoring_id)
            except Exception as e:
                failed.append({"id": monitoring_id, "error": str(e)})

        return {
            "successful": successful,
            "failed": failed,
            "total_processed": len(monitoring_ids),
            "success_count": len(successful),
            "failure_count": len(failed),
        }

    async def bulk_stop_monitoring(
        self, monitoring_ids: List[str]
    ) -> Dict[str, Any]:
        """Массовая остановка мониторинга"""
        successful = []
        failed = []

        for monitoring_id in monitoring_ids:
            try:
                monitoring = await self.stop_monitoring(monitoring_id)
                successful.append(monitoring_id)
            except Exception as e:
                failed.append({"id": monitoring_id, "error": str(e)})

        return {
            "successful": successful,
            "failed": failed,
            "total_processed": len(monitoring_ids),
            "success_count": len(successful),
            "failure_count": len(failed),
        }

    async def _perform_monitoring_cycle(
        self, monitoring: VKGroupMonitoring
    ) -> MonitoringResult:
        """Выполнить цикл мониторинга через VK API"""
        start_time = datetime.utcnow()

        try:
            if not self.vk_api_service:
                raise ValueError("VK API service not configured")

            # Получить последние посты группы
            posts = await self.vk_api_service.get_group_posts(
                group_id=monitoring.group_id,
                count=10,  # последние 10 постов
                timeout=monitoring.config.timeout_seconds,
            )

            # Анализировать комментарии к постам
            total_comments = 0
            keywords_found = []

            for post in posts.get("items", []):
                post_id = post["id"]

                # Получить комментарии к посту
                comments = await self.vk_api_service.get_post_comments(
                    owner_id=-monitoring.group_id,  # отрицательный ID для групп
                    post_id=post_id,
                    count=100,
                    timeout=monitoring.config.timeout_seconds,
                )

                total_comments += len(comments.get("items", []))

                # Здесь можно добавить анализ ключевых слов
                # keywords_found.extend(await self._analyze_keywords_in_comments(comments))

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = MonitoringResult(
                group_id=monitoring.group_id,
                posts_found=len(posts.get("items", [])),
                comments_found=total_comments,
                keywords_found=keywords_found,
                processing_time=processing_time,
                started_at=start_time,
                completed_at=datetime.utcnow(),
            )

            result.mark_completed()
            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = MonitoringResult(
                group_id=monitoring.group_id,
                processing_time=processing_time,
                started_at=start_time,
                completed_at=datetime.utcnow(),
            )
            result.add_error(str(e))
            result.mark_completed()

            return result
