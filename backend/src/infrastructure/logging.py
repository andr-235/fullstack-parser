"""
Инфраструктурный сервис логирования

Предоставляет структурированное логирование во всех слоях архитектуры
с Winston-подобным интерфейсом для enterprise-grade приложений
"""

import logging
import sys
import json
import time
from typing import Any, Dict, Optional, List, Union
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(Enum):
    """Уровни логирования по аналогии с Winston"""

    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"
    VERBOSE = "verbose"
    SILLY = "silly"


class TransportType(Enum):
    """Типы транспортов для логирования"""

    CONSOLE = "console"
    FILE = "file"
    JSON = "json"
    SYSLOG = "syslog"


@dataclass
class LogEntry:
    """Структура записи лога по аналогии с Winston"""

    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = field(default_factory=dict)
    service: str = "vk-api"
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь для сериализации"""
        return {
            "timestamp": self.timestamp.isoformat() + "Z",
            "level": self.level.value,
            "log_message": self.message,
            "service": self.service,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "meta": self.meta,
        }

    def to_json(self) -> str:
        """Преобразовать в JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, default=str)


class WinstonLogger:
    """
    Winston-подобный логгер для Python

    Предоставляет интерфейс, аналогичный Winston из Node.js,
    но адаптированный для Python экосистемы.

    Пример использования:
        logger = WinstonLogger("my-service")
        logger.info("User logged in", {"user_id": 123})
        logger.error("Database error", {"error": str(e)})
    """

    def __init__(
        self,
        service_name: str,
        level: LogLevel = LogLevel.INFO,
        transports: Optional[List[Dict[str, Any]]] = None,
    ):
        self.service_name = service_name
        self.level = level
        self.transports = transports or self._default_transports()
        self._logger = logging.getLogger(service_name)
        self._setup_logger()

    def _default_transports(self) -> List[Dict[str, Any]]:
        """Настройка транспортов по умолчанию"""
        return [
            {
                "type": TransportType.CONSOLE,
                "level": LogLevel.DEBUG,
                "format": "simple",
            },
            {
                "type": TransportType.FILE,
                "level": LogLevel.INFO,
                "filename": f"logs/{self.service_name}.log",
                "format": "json",
            },
        ]

    def _setup_logger(self) -> None:
        """Настройка внутреннего логгера Python"""
        self._logger.setLevel(self._get_python_level(self.level))

        # Создаем директорию для логов если нужно
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Добавляем обработчики на основе транспортов
        for transport in self.transports:
            handler = self._create_handler(transport)
            if handler:
                self._logger.addHandler(handler)

    def _get_python_level(self, winston_level: LogLevel) -> int:
        """Преобразовать уровень Winston в уровень Python logging"""
        mapping = {
            LogLevel.ERROR: logging.ERROR,
            LogLevel.WARN: logging.WARNING,
            LogLevel.INFO: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.VERBOSE: logging.DEBUG,
            LogLevel.SILLY: logging.DEBUG,
        }
        return mapping.get(winston_level, logging.INFO)

    def _create_handler(
        self, transport: Dict[str, Any]
    ) -> Optional[logging.Handler]:
        """Создать обработчик на основе конфигурации транспорта"""
        transport_type = transport.get("type")

        if transport_type == TransportType.CONSOLE:
            handler = logging.StreamHandler(sys.stdout)
            formatter = self._create_formatter(
                transport.get("format", "simple")
            )
            handler.setFormatter(formatter)
            return handler

        elif transport_type == TransportType.FILE:
            filename = transport.get(
                "filename", f"logs/{self.service_name}.log"
            )
            handler = logging.FileHandler(filename, encoding="utf-8")
            formatter = self._create_formatter(transport.get("format", "json"))
            handler.setFormatter(formatter)
            return handler

        return None

    def _create_formatter(self, format_type: str) -> logging.Formatter:
        """Создать форматтер на основе типа"""
        if format_type == "json":
            return JSONFormatter()
        else:
            return logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

    def _should_log(self, level: LogLevel) -> bool:
        """Проверить, нужно ли логировать на данном уровне"""
        levels_order = [
            LogLevel.SILLY,
            LogLevel.VERBOSE,
            LogLevel.DEBUG,
            LogLevel.INFO,
            LogLevel.WARN,
            LogLevel.ERROR,
        ]
        current_index = levels_order.index(self.level)
        message_index = levels_order.index(level)
        return message_index >= current_index

    def _log(
        self,
        level: LogLevel,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Внутренний метод логирования"""
        if not self._should_log(level):
            return

        log_entry = LogEntry(
            level=level,
            message=message,
            meta=meta or {},
            service=self.service_name,
            request_id=request_id,
            user_id=user_id,
            correlation_id=correlation_id,
        )

        # Используем стандартный Python logger для совместимости
        python_level = self._get_python_level(level)
        self._logger.log(python_level, message, extra=log_entry.to_dict())

    def error(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать ошибку"""
        self._log(
            LogLevel.ERROR,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def warn(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать предупреждение"""
        self._log(
            LogLevel.WARN,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def warning(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать предупреждение (синоним warn для совместимости)"""
        self.warn(message, meta, request_id, user_id, correlation_id)

    def info(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать информационное сообщение"""
        self._log(
            LogLevel.INFO,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def debug(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать отладочное сообщение"""
        self._log(
            LogLevel.DEBUG,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def verbose(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать подробное сообщение"""
        self._log(
            LogLevel.VERBOSE,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def silly(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать очень подробное сообщение"""
        self._log(
            LogLevel.SILLY,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def add_transport(self, transport: Dict[str, Any]) -> None:
        """Добавить новый транспорт"""
        self.transports.append(transport)
        handler = self._create_handler(transport)
        if handler:
            self._logger.addHandler(handler)

    def remove_transport(self, transport_type: TransportType) -> None:
        """Удалить транспорт по типу"""
        self.transports = [
            t for t in self.transports if t.get("type") != transport_type
        ]
        # Пересоздаем обработчики
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)
        self._setup_logger()

    def set_level(self, level: LogLevel) -> None:
        """Установить уровень логирования"""
        self.level = level
        self._logger.setLevel(self._get_python_level(level))


class JSONFormatter(logging.Formatter):
    """JSON форматтер для структурированного логирования"""

    def format(self, record: logging.LogRecord) -> str:
        """Форматировать запись в JSON"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname.lower(),
            "message": record.getMessage(),
            "service": record.name,
        }

        # Добавляем дополнительные поля из extra
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "meta"):
            log_entry["meta"] = record.meta

        return json.dumps(log_entry, ensure_ascii=False, default=str)


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


# Глобальный экземпляр Winston логгера
@lru_cache(maxsize=1)
def get_winston_logger(service_name: str = "vk-api") -> WinstonLogger:
    """Получить экземпляр Winston логгера (кешируется)"""
    return WinstonLogger(service_name)


# Глобальный Winston логгер по умолчанию
winston_logger = get_winston_logger()


# Экспорт
__all__ = [
    "LoggingService",
    "get_logging_service",
    "logging_service",
    "WinstonLogger",
    "LogLevel",
    "TransportType",
    "LogEntry",
    "JSONFormatter",
    "get_winston_logger",
    "winston_logger",
]
