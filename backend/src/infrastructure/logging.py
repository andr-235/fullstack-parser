"""
Инфраструктурный сервис логирования на основе Loguru

Предоставляет структурированное логирование во всех слоях архитектуры
с простым и мощным интерфейсом Loguru
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger


class LogLevel(Enum):
    """Уровни логирования"""

    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"
    VERBOSE = "verbose"
    SILLY = "silly"


@dataclass
class LogEntry:
    """Структура записи лога"""

    level: LogLevel
    message: str
    timestamp: datetime
    meta: Dict[str, Any]
    service: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует запись в словарь"""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "meta": self.meta,
            "service": self.service,
            "request_id": self.request_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
        }


class LoguruLogger:
    """Логгер на основе Loguru с Winston-подобным интерфейсом"""

    def __init__(self, service_name: str = "app"):
        self.service_name = service_name
        self._configured = False
        self._configure_logger()

    def _configure_logger(self):
        """Настраивает Loguru логгер"""
        if self._configured:
            return

        # Удаляем стандартный handler только если он еще не настроен
        if not hasattr(LoguruLogger, "_handlers_configured"):
            logger.remove()
            LoguruLogger._handlers_configured = True

        # Проверяем, не добавлены ли уже handlers
        if not hasattr(LoguruLogger, "_handlers_added"):
            # Консольный вывод с цветами
            logger.add(
                sys.stderr,
                level="DEBUG",
                format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>",
                colorize=True,
                enqueue=True,  # Thread-safe
            )

            # JSON файл для production
            logger.add(
                "logs/app.log",
                level="INFO",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
                rotation="100 MB",
                retention="30 days",
                compression="zip",
                enqueue=True,
            )

            # JSON файл для структурированного логирования
            logger.add(
                "logs/structured.json",
                level="DEBUG",
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
                serialize=True,  # JSON формат
                rotation="50 MB",
                retention="7 days",
                compression="zip",
                enqueue=True,
            )

            LoguruLogger._handlers_added = True

        self._configured = True

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
        # Создаем контекст для логирования
        context = {
            "service": self.service_name,
            "meta": meta or {},
        }

        if request_id:
            context["request_id"] = request_id
        if user_id:
            context["user_id"] = user_id
        if correlation_id:
            context["correlation_id"] = correlation_id

        # Логируем с контекстом
        bound_logger = logger.bind(**context)

        if level == LogLevel.ERROR:
            bound_logger.error(message)
        elif level == LogLevel.WARN:
            bound_logger.warning(message)
        elif level == LogLevel.INFO:
            bound_logger.info(message)
        elif level == LogLevel.DEBUG:
            bound_logger.debug(message)
        elif level == LogLevel.VERBOSE:
            bound_logger.info(
                message
            )  # Loguru не имеет verbose, используем info
        elif level == LogLevel.SILLY:
            bound_logger.debug(
                message
            )  # Loguru не имеет silly, используем debug

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
        """Алиас для warn() - логировать предупреждение"""
        self.warn(message, meta, request_id, user_id, correlation_id)

    def info(
        self,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Логировать информацию"""
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
        """Логировать отладочную информацию"""
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
        """Логировать подробную информацию"""
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
        """Логировать мельчайшие детали"""
        self._log(
            LogLevel.SILLY,
            message,
            meta,
            request_id,
            user_id,
            correlation_id,
        )

    def bind(self, **kwargs) -> "LoguruLogger":
        """Создает новый логгер с привязанным контекстом"""
        new_logger = LoguruLogger(self.service_name)
        new_logger._configured = True
        return new_logger

    def catch(self, *args, **kwargs):
        """Перехватывает исключения и логирует их"""
        return logger.catch(*args, **kwargs)

    def add(self, sink, **kwargs):
        """Добавляет новый sink для логирования"""
        return logger.add(sink, **kwargs)

    def remove(self, handler_id=None):
        """Удаляет sink"""
        return logger.remove(handler_id)

    def configure(self, **kwargs):
        """Настраивает логгер"""
        return logger.configure(**kwargs)


# Глобальные экземпляры логгеров
_loggers: Dict[str, LoguruLogger] = {}


@lru_cache(maxsize=128)
def get_loguru_logger(service_name: str = "app") -> LoguruLogger:
    """
    Получить логгер для сервиса

    Args:
        service_name: Имя сервиса

    Returns:
        Настроенный логгер
    """
    if service_name not in _loggers:
        _loggers[service_name] = LoguruLogger(service_name)
    return _loggers[service_name]


# Обратная совместимость - создаем алиасы
def get_winston_logger(service_name: str = "app") -> LoguruLogger:
    """Обратная совместимость - возвращает Loguru логгер"""
    return get_loguru_logger(service_name)


# Утилитарные функции для быстрого логирования
def log_info(message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Быстрое логирование информации"""
    logger = get_loguru_logger("infrastructure")
    logger.info(message, meta=meta)


def log_error(
    message: str,
    error: Optional[Exception] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Быстрое логирование ошибки"""
    logger = get_loguru_logger("infrastructure")
    if error:
        message = f"{message}: {str(error)}"
    logger.error(message, meta=meta)


def log_warning(message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Быстрое логирование предупреждения"""
    logger = get_loguru_logger("infrastructure")
    logger.warn(message, meta=meta)


def log_debug(message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Быстрое логирование отладки"""
    logger = get_loguru_logger("infrastructure")
    logger.debug(message, meta=meta)


def log_critical(message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    """Быстрое логирование критической ошибки"""
    logger = get_loguru_logger("infrastructure")
    logger.error(message, meta=meta)


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Логирование HTTP запроса"""
    logger = get_loguru_logger("infrastructure")

    meta = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration": duration,
    }

    if user_id:
        meta["user_id"] = user_id
    if ip_address:
        meta["ip_address"] = ip_address
    if details:
        meta.update(details)

    if status_code >= 400:
        logger.warn(
            f"{method} {path} - {status_code} ({duration:.3f}s)", meta=meta
        )
    else:
        logger.info(
            f"{method} {path} - {status_code} ({duration:.3f}s)", meta=meta
        )


def log_security_event(
    event_type: str,
    message: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """Логирование событий безопасности"""
    logger = get_loguru_logger("security")

    meta = {
        "event_type": event_type,
    }

    if user_id:
        meta["user_id"] = user_id
    if ip_address:
        meta["ip_address"] = ip_address
    if details:
        meta.update(details)

    logger.warn(message, meta=meta)


def set_log_level(level: str) -> None:
    """
    Установить уровень логирования

    Args:
        level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level=level.upper(),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>",
        colorize=True,
        enqueue=True,
    )


# Создаем директорию для логов
Path("logs").mkdir(exist_ok=True)
