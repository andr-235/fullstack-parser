"""
Тесты для ParsingManager

Тестирует все основные методы сервиса управления задачами парсинга
с использованием моков для изоляции от внешних зависимостей.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.parsing_manager import ParsingManager
from app.models.vk_group import VKGroup


@pytest.fixture
def mock_db():
    """Фикстура для мок базы данных"""
    return AsyncMock()


@pytest.fixture
def mock_arq_client():
    """Фикстура для мок ARQ клиента"""
    return AsyncMock()


@pytest.fixture
def parsing_manager(mock_db, mock_arq_client):
    """Фикстура для ParsingManager"""
    return ParsingManager(mock_db, mock_arq_client)


@pytest.fixture
def sample_vk_group():
    """Фикстура для примера VKGroup"""
    group = MagicMock(spec=VKGroup)
    group.id = 1
    group.vk_id = 123456789
    group.name = "Тестовая Группа"
    group.screen_name = "test_group"
    group.is_active = True
    group.member_count = 1000
    return group


class TestParsingManager:
    """Тесты для ParsingManager"""

    @pytest.mark.asyncio
    async def test_start_parsing_task_success(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест успешного запуска задачи парсинга"""
        # Настраиваем мок для получения группы
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_group_result

        # Настраиваем мок ARQ для успешного запуска
        mock_arq_client.enqueue_job.return_value = "task_123"

        # Вызываем метод
        task_id = await parsing_manager.start_parsing_task(
            group_id=123456789, config={"max_posts": 50, "force_reparse": True}
        )

        # Проверяем результат
        assert isinstance(task_id, str)
        assert len(task_id) > 0

        # Проверяем что ARQ был вызван с правильными параметрами
        mock_arq_client.enqueue_job.assert_called_once()
        call_args = mock_arq_client.enqueue_job.call_args
        assert call_args[0][0] == "parse_group"  # Имя функции
        assert call_args[0][1]["group_id"] == 123456789
        assert call_args[0][1]["config"]["max_posts"] == 50
        assert call_args[0][1]["config"]["force_reparse"] == True

    @pytest.mark.asyncio
    async def test_start_parsing_task_group_not_found(
        self, parsing_manager, mock_db
    ):
        """Тест запуска задачи для несуществующей группы"""
        # Настраиваем мок для None результата
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        # Проверяем что исключение пробрасывается
        with pytest.raises(ValueError, match="Group with VK ID 999 not found"):
            await parsing_manager.start_parsing_task(group_id=999)

    @pytest.mark.asyncio
    async def test_start_parsing_task_group_inactive(
        self, parsing_manager, mock_db, sample_vk_group
    ):
        """Тест запуска задачи для неактивной группы"""
        # Настраиваем группу как неактивную
        sample_vk_group.is_active = False

        # Настраиваем мок для получения группы
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_result

        # Проверяем что исключение пробрасывается
        with pytest.raises(ValueError, match="Group 123456789 is not active"):
            await parsing_manager.start_parsing_task(group_id=123456789)

    @pytest.mark.asyncio
    async def test_start_parsing_task_no_arq_client(
        self, parsing_manager, mock_db, sample_vk_group
    ):
        """Тест запуска задачи без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager_without_arq = ParsingManager(mock_db)

        # Настраиваем мок для получения группы
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_result

        # Вызываем метод
        task_id = await manager_without_arq.start_parsing_task(
            group_id=123456789
        )

        # Проверяем что задача создана, но не отправлена в очередь
        assert isinstance(task_id, str)
        assert len(task_id) > 0

    @pytest.mark.asyncio
    async def test_get_parsing_status_success(
        self, parsing_manager, mock_arq_client
    ):
        """Тест успешного получения статуса задачи"""
        # Настраиваем мок ARQ для успешного получения статуса
        mock_arq_client.get_job_info.return_value = {
            "job_id": "task_123",
            "status": "completed",
            "progress": 100,
            "result": {"posts_parsed": 10, "comments_found": 25},
            "created_at": "2024-01-15T12:00:00Z",
            "started_at": "2024-01-15T12:01:00Z",
            "finished_at": "2024-01-15T12:05:00Z",
        }

        # Вызываем метод
        status = await parsing_manager.get_parsing_status("task_123")

        # Проверяем результат
        assert status["task_id"] == "task_123"
        assert status["status"] == "completed"
        assert status["progress"] == 100
        assert status["result"]["posts_parsed"] == 10
        assert status["result"]["comments_found"] == 25

        # Проверяем что ARQ был вызван правильно
        mock_arq_client.get_job_info.assert_called_once_with("task_123")

    @pytest.mark.asyncio
    async def test_get_parsing_status_not_found(
        self, parsing_manager, mock_arq_client
    ):
        """Тест получения статуса несуществующей задачи"""
        # Настраиваем мок ARQ для None результата
        mock_arq_client.get_job_info.return_value = None

        # Вызываем метод
        status = await parsing_manager.get_parsing_status("nonexistent_task")

        # Проверяем результат
        assert status["task_id"] == "nonexistent_task"
        assert status["status"] == "not_found"
        assert status["progress"] == 0

    @pytest.mark.asyncio
    async def test_get_parsing_status_no_arq_client(self, parsing_manager):
        """Тест получения статуса без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager_without_arq = ParsingManager(mock_db)

        # Вызываем метод
        status = await manager_without_arq.get_parsing_status("task_123")

        # Проверяем результат
        assert status["task_id"] == "task_123"
        assert status["status"] == "unknown"
        assert status["message"] == "ARQ client not available"
        assert status["progress"] == 0

    @pytest.mark.asyncio
    async def test_cancel_parsing_task_success(
        self, parsing_manager, mock_arq_client
    ):
        """Тест успешной отмены задачи"""
        # Настраиваем мок ARQ для успешной отмены
        mock_arq_client.cancel_job.return_value = True

        # Вызываем метод
        success = await parsing_manager.cancel_parsing_task("task_123")

        # Проверяем результат
        assert success == True

        # Проверяем что ARQ был вызван правильно
        mock_arq_client.cancel_job.assert_called_once_with("task_123")

    @pytest.mark.asyncio
    async def test_cancel_parsing_task_failure(
        self, parsing_manager, mock_arq_client
    ):
        """Тест неудачной отмены задачи"""
        # Настраиваем мок ARQ для неудачной отмены
        mock_arq_client.cancel_job.return_value = False

        # Вызываем метод
        success = await parsing_manager.cancel_parsing_task("task_123")

        # Проверяем результат
        assert success == False

    @pytest.mark.asyncio
    async def test_cancel_parsing_task_no_arq_client(self, parsing_manager):
        """Тест отмены задачи без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager_without_arq = ParsingManager(mock_db)

        # Вызываем метод
        success = await manager_without_arq.cancel_parsing_task("task_123")

        # Проверяем результат
        assert success == False

    @pytest.mark.asyncio
    async def test_get_active_tasks_success(
        self, parsing_manager, mock_arq_client
    ):
        """Тест успешного получения активных задач"""
        # Настраиваем мок ARQ для активных задач
        mock_arq_client.get_active_jobs.return_value = [
            {
                "job_id": "task_1",
                "function": "parse_group",
                "args": {"group_id": 123456789},
                "created_at": "2024-01-15T12:00:00Z",
            },
            {
                "job_id": "task_2",
                "function": "parse_group",
                "args": {"group_id": 987654321},
                "created_at": "2024-01-15T12:05:00Z",
            },
        ]

        # Вызываем метод
        active_tasks = await parsing_manager.get_active_tasks()

        # Проверяем результат
        assert len(active_tasks) == 2
        assert active_tasks[0]["task_id"] == "task_1"
        assert active_tasks[0]["function"] == "parse_group"
        assert active_tasks[1]["task_id"] == "task_2"

    @pytest.mark.asyncio
    async def test_get_active_tasks_no_arq_client(self, parsing_manager):
        """Тест получения активных задач без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager_without_arq = ParsingManager(mock_db)

        # Вызываем метод
        active_tasks = await manager_without_arq.get_active_tasks()

        # Проверяем результат
        assert len(active_tasks) == 0

    @pytest.mark.asyncio
    async def test_start_bulk_parsing_success(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест успешного массового запуска парсинга"""
        # Настраиваем мок для получения групп
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = sample_vk_group

        # Создаем вторую группу
        group2 = MagicMock(spec=VKGroup)
        group2.id = 2
        group2.vk_id = 987654321
        group2.name = "Вторая Группа"
        group2.is_active = True

        mock_group_result2 = MagicMock()
        mock_group_result2.scalar_one_or_none.return_value = group2

        # Настраиваем последовательные вызовы
        mock_db.execute.side_effect = [mock_group_result, mock_group_result2]

        # Настраиваем мок ARQ для успешного запуска задач
        mock_arq_client.enqueue_job.side_effect = ["task_1", "task_2"]

        # Вызываем метод
        result = await parsing_manager.start_bulk_parsing(
            group_ids=[123456789, 987654321], config={"max_posts": 25}
        )

        # Проверяем результат
        assert result["total_groups"] == 2
        assert result["started_tasks"] == 2
        assert result["failed_groups"] == []
        assert len(result["tasks"]) == 2
        assert result["success_rate"] == 100.0

    @pytest.mark.asyncio
    async def test_start_bulk_parsing_partial_failure(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест массового запуска с частичными неудачами"""
        # Настраиваем мок для первой группы
        mock_group_result = MagicMock()
        mock_group_result.scalar_one_or_none.return_value = sample_vk_group

        # Вторая группа не найдена
        mock_group_result2 = MagicMock()
        mock_group_result2.scalar_one_or_none.return_value = None

        # Настраиваем последовательные вызовы
        mock_db.execute.side_effect = [mock_group_result, mock_group_result2]

        # Настраиваем мок ARQ для успешного запуска первой задачи
        mock_arq_client.enqueue_job.return_value = "task_1"

        # Вызываем метод
        result = await parsing_manager.start_bulk_parsing(
            group_ids=[123456789, 999999999]
        )

        # Проверяем результат
        assert result["total_groups"] == 2
        assert result["started_tasks"] == 1
        assert len(result["failed_groups"]) == 1
        assert result["failed_groups"][0]["group_id"] == 999999999
        assert result["success_rate"] == 50.0

    @pytest.mark.asyncio
    async def test_start_bulk_parsing_empty_list(
        self, parsing_manager, mock_arq_client
    ):
        """Тест массового запуска с пустым списком групп"""
        # Вызываем метод с пустым списком
        result = await parsing_manager.start_bulk_parsing(group_ids=[])

        # Проверяем результат
        assert result["total_groups"] == 0
        assert result["started_tasks"] == 0
        assert result["failed_groups"] == []
        assert result["tasks"] == []

        # Проверяем что ARQ не был вызван
        mock_arq_client.enqueue_job.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_system_status_success(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест успешного получения статуса системы"""
        # Настраиваем мок для получения групп
        mock_groups_result = MagicMock()
        mock_groups_result.scalars.return_value.all.return_value = [
            sample_vk_group
        ]

        # Настраиваем мок ARQ для активных задач
        mock_arq_client.get_active_jobs.return_value = [
            {
                "job_id": "task_1",
                "function": "parse_group",
                "args": {"group_id": 123456789},
                "created_at": "2024-01-15T12:00:00Z",
            }
        ]

        mock_db.execute.return_value = mock_groups_result

        # Вызываем метод
        status = await parsing_manager.get_system_status()

        # Проверяем результат
        assert status["arq_status"] == "available"
        assert status["active_tasks_count"] == 1
        assert status["active_groups_count"] == 1
        assert len(status["active_tasks"]) == 1
        assert "timestamp" in status

    @pytest.mark.asyncio
    async def test_get_system_status_no_arq_client(
        self, parsing_manager, mock_db, sample_vk_group
    ):
        """Тест получения статуса системы без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager_without_arq = ParsingManager(mock_db)

        # Настраиваем мок для получения групп
        mock_groups_result = MagicMock()
        mock_groups_result.scalars.return_value.all.return_value = [
            sample_vk_group
        ]
        mock_db.execute.return_value = mock_groups_result

        # Вызываем метод
        status = await manager_without_arq.get_system_status()

        # Проверяем результат
        assert status["arq_status"] == "unavailable"
        assert status["active_tasks_count"] == 0
        assert status["active_groups_count"] == 1

    @pytest.mark.asyncio
    async def test_database_error_handling(self, parsing_manager, mock_db):
        """Тест обработки ошибок базы данных"""
        # Настраиваем мок для выброса исключения
        mock_db.execute.side_effect = Exception("Database connection error")

        # Проверяем что исключения пробрасываются для всех методов
        with pytest.raises(Exception, match="Database connection error"):
            await parsing_manager.start_parsing_task(group_id=123456789)

        with pytest.raises(Exception, match="Database connection error"):
            await parsing_manager.start_bulk_parsing(group_ids=[123456789])

        with pytest.raises(Exception, match="Database connection error"):
            await parsing_manager.get_system_status()

    def test_manager_initialization(
        self, parsing_manager, mock_db, mock_arq_client
    ):
        """Тест инициализации менеджера"""
        # Проверяем что менеджер правильно инициализирован
        assert parsing_manager.db == mock_db
        assert parsing_manager.arq == mock_arq_client
        assert hasattr(parsing_manager, "start_parsing_task")
        assert hasattr(parsing_manager, "get_parsing_status")
        assert hasattr(parsing_manager, "cancel_parsing_task")
        assert hasattr(parsing_manager, "get_active_tasks")
        assert hasattr(parsing_manager, "start_bulk_parsing")
        assert hasattr(parsing_manager, "get_system_status")

    def test_manager_initialization_without_arq(self, mock_db):
        """Тест инициализации менеджера без ARQ клиента"""
        # Создаем менеджер без ARQ клиента
        manager = ParsingManager(mock_db)

        # Проверяем что ARQ клиент равен None
        assert manager.arq is None
        assert manager.db == mock_db

    @pytest.mark.asyncio
    async def test_task_id_generation(
        self, parsing_manager, mock_db, sample_vk_group
    ):
        """Тест генерации ID задач"""
        # Настраиваем мок для получения группы
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_result

        # Вызываем метод дважды
        task_id1 = await parsing_manager.start_parsing_task(group_id=123456789)
        task_id2 = await parsing_manager.start_parsing_task(group_id=123456789)

        # Проверяем что ID уникальны
        assert isinstance(task_id1, str)
        assert isinstance(task_id2, str)
        assert task_id1 != task_id2
        assert len(task_id1) > 0
        assert len(task_id2) > 0

    @pytest.mark.asyncio
    async def test_arq_error_handling(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест обработки ошибок ARQ"""
        # Настраиваем мок для получения группы
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_result

        # Настраиваем мок ARQ для выброса исключения
        mock_arq_client.enqueue_job.side_effect = Exception(
            "ARQ connection error"
        )

        # Проверяем что исключения пробрасываются
        with pytest.raises(Exception, match="ARQ connection error"):
            await parsing_manager.start_parsing_task(group_id=123456789)

        with pytest.raises(Exception, match="ARQ connection error"):
            await parsing_manager.start_bulk_parsing(group_ids=[123456789])

    @pytest.mark.asyncio
    async def test_config_default_values(
        self, parsing_manager, mock_db, mock_arq_client, sample_vk_group
    ):
        """Тест установки значений конфигурации по умолчанию"""
        # Настраиваем моки
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_vk_group
        mock_db.execute.return_value = mock_result

        mock_arq_client.enqueue_job.return_value = "task_123"

        # Вызываем метод без конфигурации
        await parsing_manager.start_parsing_task(group_id=123456789)

        # Проверяем что ARQ был вызван с конфигурацией по умолчанию
        call_args = mock_arq_client.enqueue_job.call_args
        config = call_args[0][1]["config"]

        assert "max_posts" in config
        assert "max_comments_per_post" in config
        assert "force_reparse" in config
        assert "priority" in config
        assert config["max_posts"] == 100  # Значение по умолчанию
        assert config["priority"] == "normal"  # Значение по умолчанию
