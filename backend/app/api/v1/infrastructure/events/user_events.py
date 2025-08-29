"""
Domain Events для пользователей (DDD Infrastructure Layer)

Конкретные реализации Domain Events для работы с пользователями
в рамках DDD архитектуры.
"""

from typing import List, Optional, Dict, Any
from .domain_event_publisher import DomainEvent


class UserCreatedEvent(DomainEvent):
    """
    Событие создания пользователя

    Генерируется при создании нового пользователя в системе.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        full_name: str,
        is_superuser: bool = False,
    ):
        """
        Args:
            user_id: ID созданного пользователя
            email: Email пользователя
            full_name: Полное имя пользователя
            is_superuser: Флаг суперпользователя
        """
        super().__init__(user_id)
        self.email = email
        self.full_name = full_name
        self.is_superuser = is_superuser

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "email": self.email,
            "full_name": self.full_name,
            "is_superuser": self.is_superuser,
        }


class UserUpdatedEvent(DomainEvent):
    """
    Событие обновления пользователя

    Генерируется при изменении данных пользователя.
    """

    def __init__(
        self,
        user_id: int,
        updated_fields: List[str],
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        updated_by: Optional[str] = None,
    ):
        """
        Args:
            user_id: ID обновленного пользователя
            updated_fields: Список измененных полей
            old_values: Старые значения полей
            new_values: Новые значения полей
            updated_by: Пользователь, выполнивший обновление
        """
        super().__init__(user_id)
        self.updated_fields = updated_fields
        self.old_values = old_values or {}
        self.new_values = new_values or {}
        self.updated_by = updated_by

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "updated_fields": self.updated_fields,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "updated_by": self.updated_by,
        }


class UserDeletedEvent(DomainEvent):
    """
    Событие удаления пользователя

    Генерируется при удалении пользователя из системы.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        deleted_by: Optional[str] = None,
        reason: str = "user_request",
    ):
        """
        Args:
            user_id: ID удаленного пользователя
            email: Email пользователя
            deleted_by: Пользователь, выполнивший удаление
            reason: Причина удаления
        """
        super().__init__(user_id)
        self.email = email
        self.deleted_by = deleted_by
        self.reason = reason

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "email": self.email,
            "deleted_by": self.deleted_by,
            "reason": self.reason,
        }


class UserAuthenticatedEvent(DomainEvent):
    """
    Событие аутентификации пользователя

    Генерируется при успешной аутентификации пользователя.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        login_method: str = "password",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Args:
            user_id: ID аутентифицированного пользователя
            email: Email пользователя
            login_method: Метод аутентификации
            ip_address: IP адрес пользователя
            user_agent: User-Agent браузера
        """
        super().__init__(user_id)
        self.email = email
        self.login_method = login_method
        self.ip_address = ip_address
        self.user_agent = user_agent

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "email": self.email,
            "login_method": self.login_method,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }


class UserPasswordChangedEvent(DomainEvent):
    """
    Событие изменения пароля пользователя

    Генерируется при изменении пароля пользователя.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        changed_by: Optional[str] = None,
        change_method: str = "user",
    ):
        """
        Args:
            user_id: ID пользователя
            email: Email пользователя
            changed_by: Пользователь, изменивший пароль
            change_method: Метод изменения (user, admin, reset)
        """
        super().__init__(user_id)
        self.email = email
        self.changed_by = changed_by
        self.change_method = change_method

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "email": self.email,
            "changed_by": self.changed_by,
            "change_method": self.change_method,
        }


class UserStatusChangedEvent(DomainEvent):
    """
    Событие изменения статуса пользователя

    Генерируется при изменении статуса активности пользователя.
    """

    def __init__(
        self,
        user_id: int,
        email: str,
        old_status: bool,
        new_status: bool,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """
        Args:
            user_id: ID пользователя
            email: Email пользователя
            old_status: Старый статус активности
            new_status: Новый статус активности
            changed_by: Пользователь, изменивший статус
            reason: Причина изменения статуса
        """
        super().__init__(user_id)
        self.email = email
        self.old_status = old_status
        self.new_status = new_status
        self.changed_by = changed_by
        self.reason = reason

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "email": self.email,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "changed_by": self.changed_by,
            "reason": self.reason,
        }


class UserBulkOperationEvent(DomainEvent):
    """
    Событие массовой операции с пользователями

    Генерируется при выполнении операций над несколькими пользователями.
    """

    def __init__(
        self,
        operation_type: str,
        user_ids: List[int],
        operation_params: Optional[Dict[str, Any]] = None,
        affected_count: int = 0,
        executed_by: Optional[str] = None,
    ):
        """
        Args:
            operation_type: Тип операции (activate, deactivate, delete, etc.)
            user_ids: Список ID пользователей
            operation_params: Параметры операции
            affected_count: Количество затронутых пользователей
            executed_by: Пользователь, выполнивший операцию
        """
        super().__init__(
            user_ids[0] if user_ids else 0
        )  # Используем первый ID как aggregate_id
        self.operation_type = operation_type
        self.user_ids = user_ids
        self.operation_params = operation_params or {}
        self.affected_count = affected_count
        self.executed_by = executed_by

    def _get_event_data(self) -> Dict[str, Any]:
        """Получить данные события"""
        return {
            "operation_type": self.operation_type,
            "user_ids": self.user_ids,
            "operation_params": self.operation_params,
            "affected_count": self.affected_count,
            "executed_by": self.executed_by,
        }


# Вспомогательные функции для создания событий


def create_user_created_event(
    user_id: int,
    email: str,
    full_name: str,
    is_superuser: bool = False,
) -> UserCreatedEvent:
    """
    Создать событие создания пользователя

    Args:
        user_id: ID пользователя
        email: Email пользователя
        full_name: Полное имя
        is_superuser: Флаг суперпользователя

    Returns:
        UserCreatedEvent
    """
    return UserCreatedEvent(
        user_id=user_id,
        email=email,
        full_name=full_name,
        is_superuser=is_superuser,
    )


def create_user_updated_event(
    user_id: int,
    updated_fields: List[str],
    updated_by: Optional[str] = None,
) -> UserUpdatedEvent:
    """
    Создать событие обновления пользователя

    Args:
        user_id: ID пользователя
        updated_fields: Измененные поля
        updated_by: Пользователь, выполнивший обновление

    Returns:
        UserUpdatedEvent
    """
    return UserUpdatedEvent(
        user_id=user_id,
        updated_fields=updated_fields,
        updated_by=updated_by,
    )


def create_user_deleted_event(
    user_id: int,
    email: str,
    deleted_by: Optional[str] = None,
    reason: str = "user_request",
) -> UserDeletedEvent:
    """
    Создать событие удаления пользователя

    Args:
        user_id: ID пользователя
        email: Email пользователя
        deleted_by: Пользователь, выполнивший удаление
        reason: Причина удаления

    Returns:
        UserDeletedEvent
    """
    return UserDeletedEvent(
        user_id=user_id,
        email=email,
        deleted_by=deleted_by,
        reason=reason,
    )


def create_user_authenticated_event(
    user_id: int,
    email: str,
    login_method: str = "password",
    ip_address: Optional[str] = None,
) -> UserAuthenticatedEvent:
    """
    Создать событие аутентификации пользователя

    Args:
        user_id: ID пользователя
        email: Email пользователя
        login_method: Метод аутентификации
        ip_address: IP адрес

    Returns:
        UserAuthenticatedEvent
    """
    return UserAuthenticatedEvent(
        user_id=user_id,
        email=email,
        login_method=login_method,
        ip_address=ip_address,
    )


def create_user_bulk_operation_event(
    operation_type: str,
    user_ids: List[int],
    executed_by: Optional[str] = None,
) -> UserBulkOperationEvent:
    """
    Создать событие массовой операции с пользователями

    Args:
        operation_type: Тип операции
        user_ids: ID пользователей
        executed_by: Пользователь, выполнивший операцию

    Returns:
        UserBulkOperationEvent
    """
    return UserBulkOperationEvent(
        operation_type=operation_type,
        user_ids=user_ids,
        affected_count=len(user_ids),
        executed_by=executed_by,
    )
