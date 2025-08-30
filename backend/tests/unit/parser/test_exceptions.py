"""
Unit tests for Parser exception classes

Tests cover all custom exception classes including:
- TaskNotFoundException
- InvalidTaskDataException
- ParsingException
- VKAPILimitExceededException
- VKAPITimeoutException
- ParserServiceUnavailableException
- TaskAlreadyRunningException
- TaskQueueFullException
- InvalidGroupIdException
- GroupNotFoundException
- PostNotFoundException
- ParserConfigurationException
- ParserTimeoutException
- ParserResourceLimitException
- ParserDataValidationException
- ParserExternalServiceException
"""

import pytest
from src.parser.exceptions import (
    TaskNotFoundException,
    InvalidTaskDataException,
    ParsingException,
    VKAPILimitExceededException,
    VKAPITimeoutException,
    ParserServiceUnavailableException,
    TaskAlreadyRunningException,
    TaskQueueFullException,
    InvalidGroupIdException,
    GroupNotFoundException,
    PostNotFoundException,
    ParserConfigurationException,
    ParserTimeoutException,
    ParserResourceLimitException,
    ParserDataValidationException,
    ParserExternalServiceException,
)
from src.exceptions import APIError


class TestTaskNotFoundException:
    """Test suite for TaskNotFoundException"""

    def test_exception_creation(self):
        """Test exception creation with task_id"""
        task_id = "test-task-123"
        exc = TaskNotFoundException(task_id)

        assert isinstance(exc, APIError)
        assert exc.status_code == 404
        assert f"Задача с ID {task_id} не найдена" in str(exc.detail)
        assert exc.error_code == "TASK_NOT_FOUND"
        assert exc.details == {"task_id": task_id}

    def test_exception_inheritance(self):
        """Test that exception inherits from APIException"""
        exc = TaskNotFoundException("test-task")

        assert isinstance(exc, APIError)
        assert isinstance(exc, Exception)


class TestInvalidTaskDataException:
    """Test suite for InvalidTaskDataException"""

    def test_exception_with_field_and_value(self):
        """Test exception creation with field and value"""
        field = "group_ids"
        value = "invalid_value"
        exc = InvalidTaskDataException(field, value)

        assert exc.status_code == 422
        assert f"Неверное значение поля '{field}': {value}" in exc.detail
        assert exc.error_code == "INVALID_TASK_DATA"
        assert exc.details == {"field": field, "value": value}

    def test_exception_with_field_only(self):
        """Test exception creation with field only"""
        field = "max_posts"
        exc = InvalidTaskDataException(field)

        assert exc.status_code == 422
        assert f"Неверное значение поля '{field}'" in exc.detail
        assert exc.error_code == "INVALID_TASK_DATA"
        assert exc.details == {"field": field, "value": None}


class TestParsingException:
    """Test suite for ParsingException"""

    def test_exception_with_group_id(self):
        """Test exception creation with group_id"""
        message = "Network timeout"
        group_id = 123456789
        exc = ParsingException(message, group_id)

        assert exc.status_code == 500
        assert f"Ошибка парсинга: {message}" in exc.detail
        assert exc.error_code == "PARSING_ERROR"
        assert exc.details == {"message": message, "group_id": group_id}

    def test_exception_without_group_id(self):
        """Test exception creation without group_id"""
        message = "Generic parsing error"
        exc = ParsingException(message)

        assert exc.status_code == 500
        assert f"Ошибка парсинга: {message}" in exc.detail
        assert exc.error_code == "PARSING_ERROR"
        assert exc.details == {"message": message}
        assert "group_id" not in exc.details


class TestVKAPILimitExceededException:
    """Test suite for VKAPILimitExceededException"""

    def test_exception_with_retry_after(self):
        """Test exception creation with retry_after"""
        retry_after = 60
        exc = VKAPILimitExceededException(retry_after)

        assert exc.status_code == 429
        assert "Превышен лимит запросов к VK API" in exc.detail
        assert exc.error_code == "VK_API_LIMIT_EXCEEDED"
        assert exc.details == {"retry_after": retry_after}

    def test_exception_without_retry_after(self):
        """Test exception creation without retry_after"""
        exc = VKAPILimitExceededException()

        assert exc.status_code == 429
        assert "Превышен лимит запросов к VK API" in exc.detail
        assert exc.error_code == "VK_API_LIMIT_EXCEEDED"
        assert exc.details == {}


class TestVKAPITimeoutException:
    """Test suite for VKAPITimeoutException"""

    def test_exception_with_timeout(self):
        """Test exception creation with timeout"""
        timeout = 30
        exc = VKAPITimeoutException(timeout)

        assert exc.status_code == 504
        assert "Превышено время ожидания ответа от VK API" in exc.detail
        assert exc.error_code == "VK_API_TIMEOUT"
        assert exc.details == {"timeout": timeout}

    def test_exception_without_timeout(self):
        """Test exception creation without timeout"""
        exc = VKAPITimeoutException()

        assert exc.status_code == 504
        assert "Превышено время ожидания ответа от VK API" in exc.detail
        assert exc.error_code == "VK_API_TIMEOUT"
        assert exc.details == {}


class TestParserServiceUnavailableException:
    """Test suite for ParserServiceUnavailableException"""

    def test_exception_with_custom_service(self):
        """Test exception creation with custom service name"""
        service_name = "custom_parser"
        exc = ParserServiceUnavailableException(service_name)

        assert exc.status_code == 503
        assert f"Сервис {service_name} временно недоступен" in exc.detail
        assert exc.error_code == "PARSER_SERVICE_UNAVAILABLE"
        assert exc.details == {"service": service_name}

    def test_exception_with_default_service(self):
        """Test exception creation with default service name"""
        exc = ParserServiceUnavailableException()

        assert exc.status_code == 503
        assert "Сервис parser временно недоступен" in exc.detail
        assert exc.error_code == "PARSER_SERVICE_UNAVAILABLE"
        assert exc.details == {"service": "parser"}


class TestTaskAlreadyRunningException:
    """Test suite for TaskAlreadyRunningException"""

    def test_exception_creation(self):
        """Test exception creation"""
        task_id = "running-task-123"
        exc = TaskAlreadyRunningException(task_id)

        assert exc.status_code == 409
        assert f"Задача {task_id} уже выполняется" in exc.detail
        assert exc.error_code == "TASK_ALREADY_RUNNING"
        assert exc.details == {"task_id": task_id}


class TestTaskQueueFullException:
    """Test suite for TaskQueueFullException"""

    def test_exception_creation(self):
        """Test exception creation"""
        queue_size = 100
        exc = TaskQueueFullException(queue_size)

        assert exc.status_code == 503
        assert "Очередь задач переполнена" in exc.detail
        assert exc.error_code == "TASK_QUEUE_FULL"
        assert exc.details == {"queue_size": queue_size}


class TestInvalidGroupIdException:
    """Test suite for InvalidGroupIdException"""

    def test_exception_creation(self):
        """Test exception creation"""
        group_id = -123
        exc = InvalidGroupIdException(group_id)

        assert exc.status_code == 422
        assert f"Неверный ID группы VK: {group_id}" in exc.detail
        assert exc.error_code == "INVALID_GROUP_ID"
        assert exc.details == {"group_id": group_id}


class TestGroupNotFoundException:
    """Test suite for GroupNotFoundException"""

    def test_exception_creation(self):
        """Test exception creation"""
        group_id = 123456789
        exc = GroupNotFoundException(group_id)

        assert exc.status_code == 404
        assert f"Группа VK с ID {group_id} не найдена" in exc.detail
        assert exc.error_code == "GROUP_NOT_FOUND"
        assert exc.details == {"group_id": group_id}


class TestPostNotFoundException:
    """Test suite for PostNotFoundException"""

    def test_exception_creation(self):
        """Test exception creation"""
        post_id = "post-123"
        exc = PostNotFoundException(post_id)

        assert exc.status_code == 404
        assert f"Пост VK с ID {post_id} не найден" in exc.detail
        assert exc.error_code == "POST_NOT_FOUND"
        assert exc.details == {"post_id": post_id}


class TestParserConfigurationException:
    """Test suite for ParserConfigurationException"""

    def test_exception_creation(self):
        """Test exception creation"""
        config_key = "api_timeout"
        message = "Invalid timeout value"
        exc = ParserConfigurationException(config_key, message)

        assert exc.status_code == 500
        assert f"Ошибка конфигурации парсера: {message}" in exc.detail
        assert exc.error_code == "PARSER_CONFIGURATION_ERROR"
        assert exc.details == {"config_key": config_key, "message": message}


class TestParserTimeoutException:
    """Test suite for ParserTimeoutException"""

    def test_exception_with_task_id(self):
        """Test exception creation with task_id"""
        timeout = 300
        task_id = "task-123"
        exc = ParserTimeoutException(timeout, task_id)

        assert exc.status_code == 504
        assert "Превышено время выполнения задачи парсинга" in exc.detail
        assert exc.error_code == "PARSER_TIMEOUT"
        assert exc.details == {"timeout": timeout, "task_id": task_id}

    def test_exception_without_task_id(self):
        """Test exception creation without task_id"""
        timeout = 300
        exc = ParserTimeoutException(timeout)

        assert exc.status_code == 504
        assert "Превышено время выполнения задачи парсинга" in exc.detail
        assert exc.error_code == "PARSER_TIMEOUT"
        assert exc.details == {"timeout": timeout}
        assert "task_id" not in exc.details


class TestParserResourceLimitException:
    """Test suite for ParserResourceLimitException"""

    def test_exception_creation(self):
        """Test exception creation"""
        resource = "memory"
        limit = 1024
        current = 1200
        exc = ParserResourceLimitException(resource, limit, current)

        assert exc.status_code == 507
        assert (
            f"Превышен лимит ресурса '{resource}': {current}/{limit}"
            in exc.detail
        )
        assert exc.error_code == "PARSER_RESOURCE_LIMIT"
        assert exc.details == {
            "resource": resource,
            "limit": limit,
            "current": current,
        }


class TestParserDataValidationException:
    """Test suite for ParserDataValidationException"""

    def test_exception_creation(self):
        """Test exception creation"""
        data_type = "VKPost"
        errors = ["Missing required field 'id'", "Invalid date format"]
        exc = ParserDataValidationException(data_type, errors)

        assert exc.status_code == 422
        assert f"Ошибка валидации данных типа '{data_type}'" in exc.detail
        assert exc.error_code == "PARSER_DATA_VALIDATION_ERROR"
        assert exc.details == {
            "data_type": data_type,
            "validation_errors": errors,
        }


class TestParserExternalServiceException:
    """Test suite for ParserExternalServiceException"""

    def test_exception_creation(self):
        """Test exception creation"""
        service_name = "VK API"
        error_message = "Connection refused"
        exc = ParserExternalServiceException(service_name, error_message)

        assert exc.status_code == 502
        assert (
            f"Ошибка внешнего сервиса '{service_name}': {error_message}"
            in exc.detail
        )
        assert exc.error_code == "PARSER_EXTERNAL_SERVICE_ERROR"
        assert exc.details == {
            "service": service_name,
            "error_message": error_message,
        }


class TestExceptionInheritance:
    """Test suite for exception inheritance"""

    def test_all_exceptions_inherit_from_api_exception(self):
        """Test that all parser exceptions inherit from APIException"""
        exceptions = [
            TaskNotFoundException("test"),
            InvalidTaskDataException("field"),
            ParsingException("error"),
            VKAPILimitExceededException(),
            VKAPITimeoutException(),
            ParserServiceUnavailableException(),
            TaskAlreadyRunningException("task"),
            TaskQueueFullException(10),
            InvalidGroupIdException(123),
            GroupNotFoundException(123),
            PostNotFoundException("post"),
            ParserConfigurationException("key", "msg"),
            ParserTimeoutException(30),
            ParserResourceLimitException("cpu", 100, 120),
            ParserDataValidationException("type", ["error"]),
            ParserExternalServiceException("service", "error"),
        ]

        for exc in exceptions:
            assert isinstance(exc, APIError)
            assert isinstance(exc, Exception)


class TestExceptionAttributes:
    """Test suite for exception attributes"""

    def test_exception_status_codes(self):
        """Test that exceptions have correct status codes"""
        test_cases = [
            (TaskNotFoundException("test"), 404),
            (InvalidTaskDataException("field"), 422),
            (ParsingException("error"), 500),
            (VKAPILimitExceededException(), 429),
            (VKAPITimeoutException(), 504),
            (ParserServiceUnavailableException(), 503),
            (TaskAlreadyRunningException("task"), 409),
            (TaskQueueFullException(10), 503),
            (InvalidGroupIdException(123), 422),
            (GroupNotFoundException(123), 404),
            (PostNotFoundException("post"), 404),
            (ParserConfigurationException("key", "msg"), 500),
            (ParserTimeoutException(30), 504),
            (ParserResourceLimitException("cpu", 100, 120), 507),
            (ParserDataValidationException("type", ["error"]), 422),
            (ParserExternalServiceException("service", "error"), 502),
        ]

        for exc, expected_status in test_cases:
            assert exc.status_code == expected_status

    def test_exception_error_codes(self):
        """Test that exceptions have correct error codes"""
        test_cases = [
            (TaskNotFoundException("test"), "TASK_NOT_FOUND"),
            (InvalidTaskDataException("field"), "INVALID_TASK_DATA"),
            (ParsingException("error"), "PARSING_ERROR"),
            (VKAPILimitExceededException(), "VK_API_LIMIT_EXCEEDED"),
            (VKAPITimeoutException(), "VK_API_TIMEOUT"),
            (
                ParserServiceUnavailableException(),
                "PARSER_SERVICE_UNAVAILABLE",
            ),
            (TaskAlreadyRunningException("task"), "TASK_ALREADY_RUNNING"),
            (TaskQueueFullException(10), "TASK_QUEUE_FULL"),
            (InvalidGroupIdException(123), "INVALID_GROUP_ID"),
            (GroupNotFoundException(123), "GROUP_NOT_FOUND"),
            (PostNotFoundException("post"), "POST_NOT_FOUND"),
            (
                ParserConfigurationException("key", "msg"),
                "PARSER_CONFIGURATION_ERROR",
            ),
            (ParserTimeoutException(30), "PARSER_TIMEOUT"),
            (
                ParserResourceLimitException("cpu", 100, 120),
                "PARSER_RESOURCE_LIMIT",
            ),
            (
                ParserDataValidationException("type", ["error"]),
                "PARSER_DATA_VALIDATION_ERROR",
            ),
            (
                ParserExternalServiceException("service", "error"),
                "PARSER_EXTERNAL_SERVICE_ERROR",
            ),
        ]

        for exc, expected_code in test_cases:
            assert exc.error_code == expected_code
