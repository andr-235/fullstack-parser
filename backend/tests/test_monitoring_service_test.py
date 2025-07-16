"""
Тесты для сервиса автоматического мониторинга
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.vk_group import VKGroup
from app.services.monitoring_service import MonitoringService


@pytest.fixture
def mock_vk_service():
    """Мок VK сервиса"""
    return MagicMock()


@pytest.fixture
def mock_db():
    """Мок базы данных"""
    db = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def monitoring_service(mock_db, mock_vk_service):
    """Сервис мониторинга с моками"""
    return MonitoringService(db=mock_db, vk_service=mock_vk_service)


@pytest.fixture
def sample_group():
    """Тестовая группа"""
    group = VKGroup(
        id=1,
        vk_id=-123456,
        screen_name="test_group",
        name="Test Group",
        is_active=True,
        auto_monitoring_enabled=True,
        monitoring_interval_minutes=60,
        monitoring_priority=5,
        next_monitoring_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        monitoring_runs_count=0,
    )
    return group


class TestMonitoringService:
    """Тесты для MonitoringService"""

    @pytest.mark.asyncio
    async def test_get_groups_for_monitoring(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест получения групп для мониторинга"""
        # Настраиваем мок для async цепочки
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[sample_group])
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Выполняем тест
        groups = await monitoring_service.get_groups_for_monitoring()

        # Проверяем результат
        assert len(groups) == 1
        assert groups[0].id == sample_group.id
        assert groups[0].auto_monitoring_enabled is True

    @pytest.mark.asyncio
    async def test_schedule_group_monitoring(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест планирования следующего мониторинга группы"""
        # Выполняем тест
        await monitoring_service.schedule_group_monitoring(sample_group)

        # Проверяем, что время следующего мониторинга обновлено
        assert sample_group.next_monitoring_at is not None
        assert sample_group.next_monitoring_at > datetime.now(
            timezone.utc
        ).replace(tzinfo=None)

        # Проверяем, что commit был вызван
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_group_monitoring_success(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест успешного запуска мониторинга группы"""
        # Мокаем глобальную функцию enqueue_run_parsing_task
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "app.services.monitoring_service.enqueue_run_parsing_task",
                AsyncMock(),
            )

            # Выполняем тест
            result = await monitoring_service.start_group_monitoring(
                sample_group
            )

            # Проверяем результат
            assert result is True
            assert sample_group.monitoring_runs_count == 1
            assert sample_group.last_monitoring_success is not None
            assert sample_group.last_monitoring_error is None

    @pytest.mark.asyncio
    async def test_start_group_monitoring_failure(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест неудачного запуска мониторинга группы"""
        # Мокаем глобальную функцию enqueue_run_parsing_task чтобы он выбрасывал исключение
        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                "app.services.monitoring_service.enqueue_run_parsing_task",
                AsyncMock(side_effect=Exception("Test error")),
            )

            # Выполняем тест
            result = await monitoring_service.start_group_monitoring(
                sample_group
            )

            # Проверяем результат
            assert result is False
            assert sample_group.last_monitoring_error == "Test error"

    @pytest.mark.asyncio
    async def test_run_monitoring_cycle_empty(
        self, monitoring_service, mock_db
    ):
        """Тест цикла мониторинга без групп"""
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        stats = await monitoring_service.run_monitoring_cycle()
        assert stats["total_groups"] == 0
        assert stats["monitored_groups"] == 0
        assert stats["successful_runs"] == 0
        assert stats["failed_runs"] == 0

    @pytest.mark.asyncio
    async def test_run_monitoring_cycle_with_groups(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест цикла мониторинга с группами"""
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[sample_group])
        mock_result = AsyncMock()
        mock_result.scalars = MagicMock(return_value=mock_scalars)
        mock_db.execute = AsyncMock(return_value=mock_result)

        with pytest.MonkeyPatch().context() as m:
            m.setattr(
                monitoring_service,
                "start_group_monitoring",
                AsyncMock(return_value=True),
            )
            stats = await monitoring_service.run_monitoring_cycle()
            assert stats["total_groups"] == 1
            assert stats["monitored_groups"] == 1
            assert stats["successful_runs"] == 1
            assert stats["failed_runs"] == 0

    @pytest.mark.asyncio
    async def test_enable_group_monitoring(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест включения мониторинга группы"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_group)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await monitoring_service.enable_group_monitoring(
            group_id=1, interval_minutes=30, priority=8
        )
        assert result is True
        assert sample_group.auto_monitoring_enabled is True
        assert sample_group.monitoring_interval_minutes == 30
        assert sample_group.monitoring_priority == 8
        assert sample_group.next_monitoring_at is not None

    @pytest.mark.asyncio
    async def test_enable_group_monitoring_group_not_found(
        self, monitoring_service, mock_db
    ):
        """Тест включения мониторинга для несуществующей группы"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await monitoring_service.enable_group_monitoring(group_id=999)
        assert result is False

    @pytest.mark.asyncio
    async def test_disable_group_monitoring(
        self, monitoring_service, mock_db, sample_group
    ):
        """Тест отключения мониторинга группы"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=sample_group)
        mock_db.execute = AsyncMock(return_value=mock_result)

        result = await monitoring_service.disable_group_monitoring(group_id=1)
        assert result is True
        assert sample_group.auto_monitoring_enabled is False
        assert sample_group.next_monitoring_at is None

    @pytest.mark.asyncio
    async def test_get_monitoring_stats(self, monitoring_service, mock_db):
        """Тест получения статистики мониторинга"""
        # Настраиваем моки для разных запросов
        mock_scalars1 = MagicMock()
        mock_scalars1.all = MagicMock(
            return_value=[MagicMock() for _ in range(100)]
        )
        mock_result1 = AsyncMock()
        mock_result1.scalars = MagicMock(return_value=mock_scalars1)

        mock_scalars2 = MagicMock()
        mock_scalars2.all = MagicMock(
            return_value=[MagicMock() for _ in range(80)]
        )
        mock_result2 = AsyncMock()
        mock_result2.scalars = MagicMock(return_value=mock_scalars2)

        mock_scalars3 = MagicMock()
        mock_scalars3.all = MagicMock(
            return_value=[MagicMock() for _ in range(25)]
        )
        mock_result3 = AsyncMock()
        mock_result3.scalars = MagicMock(return_value=mock_scalars3)

        mock_scalars4 = MagicMock()
        mock_scalars4.all = MagicMock(
            return_value=[MagicMock() for _ in range(5)]
        )
        mock_result4 = AsyncMock()
        mock_result4.scalars = MagicMock(return_value=mock_scalars4)

        mock_result5 = AsyncMock()
        mock_result5.scalar = MagicMock(
            return_value=datetime.now(timezone.utc)
        )

        mock_db.execute = AsyncMock(
            side_effect=[
                mock_result1,
                mock_result2,
                mock_result3,
                mock_result4,
                mock_result5,
            ]
        )

        stats = await monitoring_service.get_monitoring_stats()
        assert stats["total_groups"] == 100
        assert stats["active_groups"] == 80
        assert stats["monitored_groups"] == 25
        assert stats["ready_for_monitoring"] == 5
        assert "next_monitoring_at" in stats
