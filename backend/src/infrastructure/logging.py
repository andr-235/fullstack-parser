"""
Инфраструктурный сервис логирования

Предоставляет структурированное логирование во всех слоях архитектуры
"""

import logging
import sys
from typing import Any, Dict, Optional
from functools import lru_cache


class LoggingService:
    """
    Инфраструктурный сервис для логирования

    Предоставляет структурированное логирование
    во всех слоях архитектуры
    """

    def __init__(self):
        self._configured = False
        self._configure_logging()

    def _configure_logging(self) -> None:
        """Настроить логирование"""
        if self._configured:
            return

        # Создаем форматтер
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Настраиваем корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Очищаем существующие обработчики
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Обработчик для ошибок
        error_handler = logging.StreamHandler(sys.stderr)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

        self._configured = True

    def get_logger(self, name: str) -> logging.Logger:
        """
        Получить логгер по имени

        Args:
            name: Имя логгера

        Returns:
            Logger instance
        """
        return logging.getLogger(name)

    def log_info(
        self, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логировать информационное сообщение

        Args:
            message: Сообщение
            extra: Дополнительные данные
        """
        logger = self.get_logger("infrastructure")
        if extra:
            logger.info(message, extra=extra)
        else:
            logger.info(message)

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Логировать сообщение об ошибке

        Args:
            message: Сообщение
            error: Исключение
            extra: Дополнительные данные
        """
        logger = self.get_logger("infrastructure")
        if error:
            message = f"{message}: {str(error)}"

        if extra:
            logger.error(message, extra=extra)
        else:
            logger.error(message)

    def log_warning(
        self, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логировать предупреждение

        Args:
            message: Сообщение
            extra: Дополнительные данные
        """
        logger = self.get_logger("infrastructure")
        if extra:
            logger.warning(message, extra=extra)
        else:
            logger.warning(message)

    def log_debug(
        self, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логировать отладочное сообщение

        Args:
            message: Сообщение
            extra: Дополнительные данные
        """
        logger = self.get_logger("infrastructure")
        if extra:
            logger.debug(message, extra=extra)
        else:
            logger.debug(message)

    def log_critical(
        self, message: str, extra: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Логировать критическое сообщение

        Args:
            message: Сообщение
            extra: Дополнительные данные
        """
        logger = self.get_logger("infrastructure")
        if extra:
            logger.critical(message, extra=extra)
        else:
            logger.critical(message)

    def log_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Логировать HTTP запрос

        Args:
            method: HTTP метод
            path: Путь запроса
            status_code: Код ответа
            duration: Длительность в секундах
            user_id: ID пользователя
        """
        logger = self.get_logger("requests")
        message = f"{method} {path} - {status_code} - {duration:.3f}s"

        extra = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration": duration,
        }

        if user_id:
            extra["user_id"] = user_id

        logger.info(message, extra=extra)

    def log_business_event(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        action: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Логировать бизнес-событие

        Args:
            event_type: Тип события
            entity_type: Тип сущности
            entity_id: ID сущности
            action: Действие
            user_id: ID пользователя
            details: Детали события
        """
        logger = self.get_logger("business")
        message = f"{event_type}: {entity_type} {entity_id} {action}"

        extra = {
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
        }

        if user_id:
            extra["user_id"] = user_id

        if details:
            extra.update(details)

        logger.info(message, extra=extra)

    def log_performance(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Логировать показатели производительности

        Args:
            operation: Название операции
            duration: Длительность в секундах
            success: Успешность операции
            details: Дополнительные детали
        """
        logger = self.get_logger("performance")
        status = "SUCCESS" if success else "FAILED"
        message = f"{operation} - {status} - {duration:.3f}s"

        extra = {
            "operation": operation,
            "duration": duration,
            "success": success,
        }

        if details:
            extra.update(details)

        if success:
            logger.info(message, extra=extra)
        else:
            logger.warning(message, extra=extra)

    def log_security_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Логировать событие безопасности

        Args:
            event_type: Тип события безопасности
            user_id: ID пользователя
            ip_address: IP адрес
            details: Детали события
        """
        logger = self.get_logger("security")
        message = f"Security event: {event_type}"

        extra = {"event_type": event_type}

        if user_id:
            extra["user_id"] = user_id
        if ip_address:
            extra["ip_address"] = ip_address
        if details:
            extra.update(details)

        logger.warning(message, extra=extra)

    def set_log_level(self, level: str) -> None:
        """
        Установить уровень логирования

        Args:
            level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)

        # Обновляем уровень для всех обработчиков
        for handler in logging.getLogger().handlers:
            handler.setLevel(numeric_level)

    def get_log_config(self) -> Dict[str, Any]:
        """
        Получить конфигурацию логирования

        Returns:
            Настройки логирования
        """
        return {
            "level": logging.getLevelName(logging.getLogger().level),
            "handlers": len(logging.getLogger().handlers),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }


# Глобальный экземпляр сервиса логирования
@lru_cache(maxsize=1)
def get_logging_service() -> LoggingService:
    """Получить экземпляр сервиса логирования (кешируется)"""
    return LoggingService()


# Глобальный объект для обратной совместимости
logging_service = get_logging_service()


# Экспорт
__all__ = [
    "LoggingService",
    "get_logging_service",
    "logging_service",
]
