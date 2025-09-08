"""
Unit tests for ParserService

Tests cover all ParserService functionality including:
- Task creation and management
- Parsing operations
- Status tracking
- Error handling
- Statistics calculation
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from src.parser.service import ParserService
from src.parser.exceptions import (
    TaskNotFoundException,
    InvalidTaskDataException,
    ParsingException,
)
from src.exceptions import ValidationError, ServiceUnavailableError


class TestParserService:
    """Test suite for ParserService"""

    @pytest.fixture
    def service(self, mock_vk_api_service):
        """Create ParserService instance for testing"""
        return ParserService(vk_api_service=mock_vk_api_service)

    def test_init_with_vk_api_service(self, mock_vk_api_service):
        """Test service initialization with VK API service"""
        service = ParserService(vk_api_service=mock_vk_api_service)

        assert service.vk_api is mock_vk_api_service
        assert service.tasks == {}
        assert service.client is not None

    def test_init_without_vk_api_service(self):
        """Test service initialization without VK API service"""
        with patch(
            "src.vk_api.dependencies.create_vk_api_service_sync"
        ) as mock_create:
            mock_vk_api = Mock()
            mock_create.return_value = mock_vk_api

            service = ParserService()

            mock_create.assert_called_once()
            assert service.vk_api is mock_vk_api

    @pytest.mark.asyncio
    async def test_start_parsing_success(
        self, service, sample_group_ids, sample_parse_request_data
    ):
        """Test successful parsing start"""
        # Act
        result = await service.start_parsing(
            group_ids=sample_group_ids,
            max_posts=50,
            max_comments_per_post=100,
            force_reparse=False,
            priority="normal",
        )

        # Assert
        assert "task_id" in result
        assert result["status"] == "started"
        assert result["group_ids"] == sample_group_ids
        assert result["estimated_time"] == len(sample_group_ids) * 30

        # Check task was created
        task_id = result["task_id"]
        assert task_id in service.tasks
        task = service.tasks[task_id]

        assert task["status"] == "running"
        assert task["group_ids"] == sample_group_ids
        assert task["groups_total"] == len(sample_group_ids)
        assert task["started_at"] is not None

    @pytest.mark.asyncio
    async def test_start_parsing_empty_group_ids(self, service):
        """Test parsing start with empty group_ids"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.start_parsing(group_ids=[])

        assert "Необходимо указать хотя бы одну группу" in str(exc_info.value)
        assert exc_info.value.field == "group_ids"

    @pytest.mark.asyncio
    async def test_start_parsing_too_many_groups(self, service):
        """Test parsing start with too many groups"""
        group_ids = list(range(10001))  # 10001 groups (превышает лимит 10000)

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.start_parsing(group_ids=group_ids)

        assert "Максимум 10000 групп за один запрос" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_parsing_invalid_max_posts(
        self, service, sample_group_ids
    ):
        """Test parsing start with invalid max_posts"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.start_parsing(
                group_ids=sample_group_ids, max_posts=0
            )

        assert "max_posts должен быть от 1 до 1000" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_parsing_invalid_max_comments(
        self, service, sample_group_ids
    ):
        """Test parsing start with invalid max_comments_per_post"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.start_parsing(
                group_ids=sample_group_ids, max_comments_per_post=1500
            )

        assert "max_comments_per_post должен быть от 1 до 1000" in str(
            exc_info.value
        )

    @pytest.mark.asyncio
    async def test_start_parsing_invalid_priority(
        self, service, sample_group_ids
    ):
        """Test parsing start with invalid priority"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.start_parsing(
                group_ids=sample_group_ids, priority="urgent"
            )

        assert "priority должен быть: low, normal, high" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stop_parsing_specific_task(self, service, mock_task_id):
        """Test stopping specific parsing task"""
        # Setup - create a running task
        task_id = mock_task_id
        service.tasks[task_id] = {
            "id": task_id,
            "status": "running",
            "started_at": datetime.utcnow(),
            "completed_at": None,
        }

        # Act
        result = await service.stop_parsing(task_id=task_id)

        # Assert
        assert result["stopped_tasks"] == [task_id]
        assert result["message"] == f"Задача {task_id} остановлена"

        task = service.tasks[task_id]
        assert task["status"] == "stopped"
        assert task["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_stop_parsing_nonexistent_task(self, service, mock_task_id):
        """Test stopping nonexistent parsing task"""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await service.stop_parsing(task_id=mock_task_id)

        assert f"Задача {mock_task_id} не найдена" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stop_parsing_already_completed_task(
        self, service, mock_task_id
    ):
        """Test stopping already completed parsing task"""
        # Setup - create a completed task
        task_id = mock_task_id
        service.tasks[task_id] = {
            "id": task_id,
            "status": "completed",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
        }

        # Act
        result = await service.stop_parsing(task_id=task_id)

        # Assert
        assert result["stopped_tasks"] == []
        assert f"Задача {task_id} уже завершена" in result["message"]

    @pytest.mark.asyncio
    async def test_stop_parsing_all_tasks(self, service):
        """Test stopping all running parsing tasks"""
        # Setup - create multiple running tasks
        task_ids = [str(uuid4()) for _ in range(3)]
        for task_id in task_ids:
            service.tasks[task_id] = {
                "id": task_id,
                "status": "running",
                "started_at": datetime.utcnow(),
                "completed_at": None,
            }

        # Add a completed task that should not be stopped
        completed_task_id = str(uuid4())
        service.tasks[completed_task_id] = {
            "id": completed_task_id,
            "status": "completed",
            "started_at": datetime.utcnow(),
            "completed_at": datetime.utcnow(),
        }

        # Act
        result = await service.stop_parsing()

        # Assert
        assert len(result["stopped_tasks"]) == 3
        assert all(task_id in result["stopped_tasks"] for task_id in task_ids)
        assert completed_task_id not in result["stopped_tasks"]
        assert "Остановлено 3 задач" in result["message"]

    @pytest.mark.asyncio
    async def test_get_task_status_success(
        self, service, mock_task_id, sample_parse_status
    ):
        """Test getting task status successfully"""
        # Setup
        service.tasks[mock_task_id] = {
            "id": mock_task_id,
            "status": "running",
            "progress": 45.5,
            "current_group": 123456789,
            "groups_completed": 1,
            "groups_total": 2,
            "posts_found": 25,
            "comments_found": 150,
            "errors": ["Sample error"],
            "started_at": datetime.utcnow(),
            "completed_at": None,
        }

        # Act
        result = await service.get_task_status(mock_task_id)

        # Assert
        assert result is not None
        assert result["task_id"] == mock_task_id
        assert result["status"] == "running"
        assert result["progress"] == 45.5
        assert result["current_group"] == 123456789
        assert result["duration"] is not None

    @pytest.mark.asyncio
    async def test_get_task_status_nonexistent_task(
        self, service, mock_task_id
    ):
        """Test getting status of nonexistent task"""
        # Act
        result = await service.get_task_status(mock_task_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_parser_state(self, service):
        """Test getting parser state"""
        # Setup - create some tasks
        tasks_data = [
            {
                "status": "running",
                "posts_found": 10,
                "comments_found": 50,
                "started_at": datetime.utcnow(),
            },
            {
                "status": "completed",
                "posts_found": 20,
                "comments_found": 100,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
            },
            {
                "status": "failed",
                "posts_found": 5,
                "comments_found": 25,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
            },
        ]

        for i, task_data in enumerate(tasks_data):
            task_id = str(uuid4())
            service.tasks[task_id] = {"id": task_id, **task_data}

        # Act
        result = await service.get_parser_state()

        # Assert
        assert result["is_running"] is True
        assert result["active_tasks"] == 1
        assert result["queue_size"] == 2  # completed + failed
        assert result["total_tasks_processed"] == 2
        assert result["total_posts_found"] == 35
        assert result["total_comments_found"] == 175
        assert result["last_activity"] is not None

    @pytest.mark.asyncio
    async def test_get_tasks_list(self, service):
        """Test getting tasks list"""
        # Setup - create tasks
        tasks_data = [
            {"status": "running", "created_at": datetime.utcnow()},
            {
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(hours=1),
            },
            {
                "status": "failed",
                "created_at": datetime.utcnow() - timedelta(hours=2),
            },
        ]

        task_ids = []
        for task_data in tasks_data:
            task_id = str(uuid4())
            task_ids.append(task_id)
            service.tasks[task_id] = {"id": task_id, **task_data}

        # Act
        result = await service.get_tasks_list()

        # Assert
        assert len(result) == 3
        # Should be sorted by created_at desc (newest first)
        assert result[0]["id"] == task_ids[0]  # newest
        assert result[2]["id"] == task_ids[2]  # oldest

    @pytest.mark.asyncio
    async def test_get_tasks_list_with_filter(self, service):
        """Test getting tasks list with status filter"""
        # Setup - create tasks with different statuses
        service.tasks[str(uuid4())] = {
            "id": "1",
            "status": "running",
            "created_at": datetime.utcnow(),
        }
        service.tasks[str(uuid4())] = {
            "id": "2",
            "status": "completed",
            "created_at": datetime.utcnow(),
        }
        service.tasks[str(uuid4())] = {
            "id": "3",
            "status": "completed",
            "created_at": datetime.utcnow(),
        }

        # Act
        result = await service.get_tasks_list(status_filter="completed")

        # Assert
        assert len(result) == 2
        assert all(task["status"] == "completed" for task in result)

    @pytest.mark.asyncio
    async def test_get_tasks_list_with_pagination(self, service):
        """Test getting tasks list with pagination"""
        # Setup - create 5 tasks
        for i in range(5):
            task_id = str(uuid4())
            service.tasks[task_id] = {
                "id": task_id,
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(hours=i),
            }

        # Act
        result = await service.get_tasks_list(limit=2, offset=1)

        # Assert
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_parsing_stats(self, service):
        """Test getting parsing statistics"""
        # Setup - create tasks with different statuses and timing
        now = datetime.utcnow()
        tasks_data = [
            {
                "status": "completed",
                "posts_found": 10,
                "comments_found": 50,
                "started_at": now - timedelta(minutes=30),
                "completed_at": now - timedelta(minutes=25),
            },
            {
                "status": "completed",
                "posts_found": 20,
                "comments_found": 100,
                "started_at": now - timedelta(minutes=20),
                "completed_at": now - timedelta(minutes=15),
            },
            {
                "status": "failed",
                "posts_found": 5,
                "comments_found": 25,
                "started_at": now - timedelta(minutes=10),
                "completed_at": now - timedelta(minutes=8),
            },
            {
                "status": "running",
                "posts_found": 15,
                "comments_found": 75,
                "started_at": now - timedelta(minutes=5),
                "completed_at": None,
            },
        ]

        for task_data in tasks_data:
            task_id = str(uuid4())
            service.tasks[task_id] = {"id": task_id, **task_data}

        # Act
        result = await service.get_parsing_stats()

        # Assert
        assert result["total_tasks"] == 4
        assert result["completed_tasks"] == 2
        assert result["failed_tasks"] == 1
        assert result["running_tasks"] == 1
        assert result["total_posts_found"] == 50
        assert result["total_comments_found"] == 250
        assert result["total_processing_time"] == 120  # 2 minutes total
        assert result["average_task_duration"] == 60.0  # 1 minute average

    @pytest.mark.asyncio
    async def test_parse_group_success(
        self,
        service,
        mock_vk_api_service,
        sample_vk_group_info,
        sample_vk_post,
        sample_vk_comment,
    ):
        """Test successful group parsing"""
        # Setup mocks
        mock_vk_api_service.get_group_info.return_value = {
            "group": sample_vk_group_info
        }
        mock_vk_api_service.get_group_posts.return_value = {
            "posts": [sample_vk_post]
        }
        mock_vk_api_service.get_post_comments.return_value = {
            "comments": [sample_vk_comment]
        }

        # Act
        result = await service.parse_group(
            group_id=123456789, max_posts=10, max_comments_per_post=50
        )

        # Assert
        assert result["group_id"] == 123456789
        assert result["posts_found"] == 1
        assert result["comments_found"] == 1
        assert result["posts_saved"] == 1
        assert result["comments_saved"] == 1
        assert result["errors"] == []
        assert result["duration_seconds"] == 10.5

        # Verify API calls
        mock_vk_api_service.get_group_info.assert_called_once_with(123456789)
        mock_vk_api_service.get_group_posts.assert_called_once_with(
            group_id=123456789, count=10
        )

    @pytest.mark.asyncio
    async def test_parse_group_not_found(self, service, mock_vk_api_service):
        """Test parsing non-existent group"""
        # Setup mock
        mock_vk_api_service.get_group_info.return_value = {"group": None}

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.parse_group(group_id=123456789)

        assert "Группа 123456789 не найдена" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_group_vk_api_error(
        self, service, mock_vk_api_service
    ):
        """Test parsing group with VK API error"""
        # Setup mock to raise exception
        mock_vk_api_service.get_group_info.side_effect = Exception(
            "VK API Error"
        )

        # Act & Assert
        with pytest.raises(ServiceUnavailableError) as exc_info:
            await service.parse_group(group_id=123456789)

        assert "Ошибка парсинга группы 123456789" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_group_post_error_handling(
        self,
        service,
        mock_vk_api_service,
        sample_vk_group_info,
        sample_vk_post,
    ):
        """Test parsing group with post processing error"""
        # Setup mocks
        mock_vk_api_service.get_group_info.return_value = {
            "group": sample_vk_group_info
        }
        mock_vk_api_service.get_group_posts.return_value = {
            "posts": [sample_vk_post]
        }
        mock_vk_api_service.get_post_comments.side_effect = Exception(
            "Post comments error"
        )

        # Act
        result = await service.parse_group(group_id=123456789)

        # Assert
        assert result["posts_found"] == 1
        assert result["comments_found"] == 0
        assert result["posts_saved"] == 0  # No posts saved due to error
        assert result["comments_saved"] == 0
        assert len(result["errors"]) == 1
        assert "Ошибка обработки поста" in result["errors"][0]
