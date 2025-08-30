"""
Улучшенные схемы ошибок для API v1 с DDD архитектурой

Этот модуль содержит кастомные исключения API, интегрированные
с DDD архитектурой и enterprise-grade error handling.
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional, List
from datetime import datetime


class APIError(HTTPException):
    """Базовый класс для API ошибок с DDD интеграцией"""

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        field: Optional[str] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.error_code = error_code
        self.details = details or {}
        self.field = field
        self.suggestions = suggestions or []
        self.timestamp = datetime.utcnow()

        super().__init__(status_code=status_code, detail=message)

    @property
    def message(self) -> str:
        """Получить сообщение об ошибке"""
        return self.detail

    @property
    def error_type(self) -> str:
        """Получить тип ошибки из details"""
        return self.details.get("error_type", "unknown")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для сериализации"""
        return {
            "code": self.error_code,
            "message": self.detail,
            "details": self.details,
            "field": self.field,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp.isoformat(),
            "status_code": self.status_code,
        }


class ValidationError(APIError):
    """Ошибка валидации с DDD интеграцией"""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        expected_type: Optional[str] = None,
    ):
        details = {}
        suggestions = []

        if field:
            details["field"] = field
            suggestions.append(f"Проверьте поле '{field}'")
        if value is not None:
            details["provided_value"] = value
        if expected_type:
            details["expected_type"] = expected_type
            suggestions.append(f"Ожидается тип: {expected_type}")

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
            field=field,
            suggestions=suggestions,
        )


class NotFoundError(APIError):
    """Ресурс не найден с DDD интеграцией"""

    def __init__(
        self,
        resource: str,
        resource_id: Optional[Any] = None,
        search_criteria: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource} not found"
        details = {"resource": resource}
        suggestions = []

        if resource_id is not None:
            message += f" with id {resource_id}"
            details["resource_id"] = resource_id
            suggestions.append(f"Проверьте корректность ID: {resource_id}")

        if search_criteria:
            details["search_criteria"] = search_criteria
            suggestions.append("Проверьте критерии поиска")

        suggestions.append(f"Убедитесь, что {resource} существует")

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=message,
            details=details,
            suggestions=suggestions,
        )


# Специфические исключения для модулей
class CommentNotFoundError(NotFoundError):
    """Комментарий не найден"""

    def __init__(self, comment_id: Optional[Any] = None):
        super().__init__(
            resource="Comment",
            resource_id=comment_id,
        )


class GroupNotFoundError(NotFoundError):
    """Группа не найдена"""

    def __init__(self, group_id: Optional[Any] = None):
        super().__init__(
            resource="Group",
            resource_id=group_id,
        )


class VKAPIError(APIError):
    """Ошибка VK API с enterprise-grade информацией"""

    def __init__(
        self,
        vk_error_code: Optional[int] = None,
        vk_error_msg: Optional[str] = None,
        request_params: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ):
        message = "VK API Error"
        details = {}
        suggestions = []

        if vk_error_msg:
            message = f"VK API: {vk_error_msg}"
            details["vk_error_message"] = vk_error_msg

        if vk_error_code is not None:
            details["vk_error_code"] = vk_error_code
            suggestions.append(f"Проверьте код ошибки VK API: {vk_error_code}")

        if request_params:
            details["request_params"] = request_params
            suggestions.append("Проверьте параметры запроса к VK API")

        if retry_after:
            details["retry_after"] = retry_after
            suggestions.append(f"Повторите запрос через {retry_after} секунд")

        suggestions.append("Проверьте токен доступа VK API")
        suggestions.append("Проверьте лимиты запросов VK API")

        super().__init__(
            status_code=502,  # Bad Gateway for external API errors
            error_code="VK_API_ERROR",
            message=message,
            details=details,
            suggestions=suggestions,
        )


class RateLimitError(APIError):
    """Превышен лимит запросов с enterprise-grade информацией"""

    def __init__(
        self,
        retry_after: int = 60,
        client_ip: Optional[str] = None,
        request_count: Optional[int] = None,
    ):
        details = {"retry_after": retry_after}
        suggestions = [
            f"Повторите запрос через {retry_after} секунд",
            "Уменьшите частоту запросов",
            "Реализуйте механизм повторных попыток с экспоненциальной задержкой",
        ]

        if client_ip:
            details["client_ip"] = client_ip
        if request_count:
            details["request_count"] = request_count

        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Превышен лимит запросов. Повторите через {retry_after} секунд.",
            details=details,
            suggestions=suggestions,
        )


class ServiceUnavailableError(APIError):
    """Сервис недоступен с DDD интеграцией"""

    def __init__(
        self,
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        reason: Optional[str] = None,
    ):
        details = {}
        suggestions = ["Повторите запрос позже", "Проверьте статус сервиса"]

        if service_name:
            details["service_name"] = service_name
        if retry_after:
            details["retry_after"] = retry_after
            suggestions.append(
                f"Рекомендуемое время ожидания: {retry_after} секунд"
            )
        if reason:
            details["reason"] = reason

        message = "Сервис временно недоступен"
        if service_name:
            message = f"Сервис '{service_name}' временно недоступен"
        if reason:
            # Включаем причину в сообщение, чтобы тесты могли искать коды ошибок
            message = f"{message}: {reason}"

        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            message=message,
            details=details,
            suggestions=suggestions,
        )


class AuthenticationError(APIError):
    """Ошибка аутентификации с enterprise-grade информацией"""

    def __init__(self, auth_method: Optional[str] = None):
        details = {}
        suggestions = [
            "Проверьте правильность учетных данных",
            "Убедитесь, что токен не истек",
            "Используйте правильный метод аутентификации",
        ]

        if auth_method:
            details["auth_method"] = auth_method

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR",
            message="Требуется аутентификация",
            details=details,
            suggestions=suggestions,
        )


class AuthorizationError(APIError):
    """Ошибка авторизации с enterprise-grade информацией"""

    def __init__(
        self,
        required_permission: Optional[str] = None,
        user_role: Optional[str] = None,
    ):
        details = {}
        suggestions = [
            "Проверьте свои права доступа",
            "Обратитесь к администратору для получения необходимых прав",
        ]

        if required_permission:
            details["required_permission"] = required_permission
            suggestions.append(f"Требуется разрешение: {required_permission}")
        if user_role:
            details["user_role"] = user_role

        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            message="Недостаточно прав для выполнения операции",
            details=details,
            suggestions=suggestions,
        )


class ConflictError(APIError):
    """Конфликт данных с DDD интеграцией"""

    def __init__(
        self,
        message: str,
        resource: Optional[str] = None,
        conflicting_value: Optional[Any] = None,
    ):
        details = {}
        suggestions = ["Измените данные для устранения конфликта"]

        if resource:
            details["resource"] = resource
        if conflicting_value:
            details["conflicting_value"] = conflicting_value

        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            details=details,
            suggestions=suggestions,
        )


class DomainError(APIError):
    """Ошибка доменной логики (DDD)"""

    def __init__(
        self,
        message: str,
        domain_entity: Optional[str] = None,
        business_rule: Optional[str] = None,
    ):
        details = {}
        suggestions = ["Проверьте бизнес-правила домена"]

        if domain_entity:
            details["domain_entity"] = domain_entity
        if business_rule:
            details["business_rule"] = business_rule
            suggestions.append(f"Нарушено бизнес-правило: {business_rule}")

        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="DOMAIN_ERROR",
            message=message,
            details=details,
            suggestions=suggestions,
        )


# Функции-хелперы для создания типовых ошибок
def create_validation_error(
    field: str,
    value: Any,
    expected_type: Optional[str] = None,
) -> ValidationError:
    """Создать ошибку валидации поля"""
    message = f"Некорректное значение поля '{field}'"
    return ValidationError(
        message=message,
        field=field,
        value=value,
        expected_type=expected_type,
    )


def create_not_found_error(
    resource: str,
    resource_id: Optional[Any] = None,
) -> NotFoundError:
    """Создать ошибку 'ресурс не найден'"""
    return NotFoundError(
        resource=resource,
        resource_id=resource_id,
    )


def create_rate_limit_error(
    retry_after: int = 60,
    client_ip: Optional[str] = None,
) -> RateLimitError:
    """Создать ошибку превышения лимита запросов"""
    return RateLimitError(
        retry_after=retry_after,
        client_ip=client_ip,
    )
