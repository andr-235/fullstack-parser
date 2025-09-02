"""
Глобальные настройки приложения VK Comments Parser

Мигрировано из app/api/v1/infrastructure/services/config_service.py
в соответствии с fastapi-best-practices
"""

from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Глобальные настройки приложения"""

    # База данных
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/vk_parser",
        alias="DATABASE_URL",
        description="URL подключения к базе данных",
    )

    # Redis
    redis_url: str = Field(
        default="redis://redis:6379/0",
        alias="REDIS_URL",
        description="URL подключения к Redis",
    )

    # VK API
    vk_access_token: str = Field(
        default="stub_token",
        alias="VK_ACCESS_TOKEN",
        description="Токен доступа к VK API",
    )
    vk_api_version: str = Field(
        default="5.199",
        alias="VK_API_VERSION",
        description="Версия VK API",
    )

    # CORS (читаем как строку, чтобы избежать JSON-декодинга pydantic-settings)
    cors_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
        description="Разрешенные origins для CORS (через запятую или JSON-массив)",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Нормализует CORS_ORIGINS из env: поддерживает CSV и JSON-массив.

        - Если значение похоже на JSON-массив, пытаемся распарсить его
        - Иначе разбиваем по запятой
        """
        raw = (self.cors_origins_raw or "").strip()
        if not raw:
            return []
        # JSON-массив
        if raw.startswith("[") and raw.endswith("]"):
            try:
                import json

                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                # Падает на невалидном JSON – fallback на CSV
                pass
        # CSV
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    # Основные настройки
    debug: bool = Field(
        default=False,
        description="Режим отладки",
    )
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Уровень логирования",
    )
    environment: str = Field(
        default="development",
        alias="ENVIRONMENT",
        description="Окружение приложения",
    )

    # Настройки производительности
    max_workers: int = Field(
        default=4,
        description="Максимальное количество воркеров",
    )
    request_timeout: int = Field(
        default=30,
        description="Таймаут запросов в секундах",
    )

    # Настройки мониторинга
    monitoring_enabled: bool = Field(
        default=False,
        description="Включен ли мониторинг",
    )
    monitoring_interval: int = Field(
        default=300,
        description="Интервал мониторинга в секундах",
    )
    health_check_enabled: bool = Field(
        default=True,
        description="Включена ли проверка здоровья",
    )

    # Настройки безопасности
    secret_key: str = Field(
        default="your-secret-key-here",
        alias="SECRET_KEY",
        description="Секретный ключ для JWT",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Алгоритм JWT",
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="Время жизни JWT токена в часах",
    )

    # Настройки кеширования
    cache_enabled: bool = Field(
        default=True,
        description="Включено ли кеширование",
    )
    cache_ttl: int = Field(
        default=3600,
        description="Время жизни кеша в секундах",
    )

    # Настройки ARQ (асинхронные задачи)
    arq_enabled: bool = Field(
        default=True,
        description="Включены ли асинхронные задачи ARQ",
    )
    arq_max_jobs: int = Field(
        default=10,
        description="Максимальное количество одновременно выполняемых задач",
    )
    arq_job_timeout: int = Field(
        default=300,
        description="Таймаут выполнения задачи в секундах (5 минут)",
    )
    arq_keep_result: int = Field(
        default=3600,
        description="Время хранения результатов задач в секундах (1 час)",
    )
    arq_max_tries: int = Field(
        default=3,
        description="Максимальное количество попыток выполнения задачи",
    )
    arq_poll_delay: float = Field(
        default=0.5,
        description="Задержка между опросами очереди в секундах",
    )
    arq_health_check_interval: int = Field(
        default=60,
        description="Интервал проверки здоровья в секундах",
    )
    arq_queue_name: str = Field(
        default="arq:queue",
        description="Имя очереди ARQ",
    )
    arq_burst_mode: bool = Field(
        default=False,
        description="Режим burst - остановка после обработки всех задач",
    )

    class Config:
        """Конфигурация Pydantic"""

        env_file = ".env"
        case_sensitive = False


# Глобальный объект настроек
settings = Settings()


class ConfigService:
    """
    Сервис для работы с конфигурацией

    Предоставляет унифицированный интерфейс для доступа к настройкам
    """

    def __init__(self):
        self._settings = settings

    @property
    def database_url(self) -> str:
        """URL базы данных"""
        return self._settings.database_url

    @property
    def redis_url(self) -> str:
        """URL Redis"""
        return self._settings.redis_url

    @property
    def vk_access_token(self) -> str:
        """VK API токен"""
        return self._settings.vk_access_token

    @property
    def vk_api_version(self) -> str:
        """Версия VK API"""
        return self._settings.vk_api_version

    @property
    def cors_origins(self) -> List[str]:
        """CORS origins"""
        return self._settings.cors_origins

    @property
    def debug(self) -> bool:
        """Режим отладки"""
        return self._settings.debug

    @property
    def log_level(self) -> str:
        """Уровень логирования"""
        return self._settings.log_level

    @property
    def environment(self) -> str:
        """Окружение"""
        return self._settings.environment

    @property
    def max_workers(self) -> int:
        """Максимальное количество воркеров"""
        return self._settings.max_workers

    @property
    def request_timeout(self) -> int:
        """Таймаут запросов"""
        return self._settings.request_timeout

    @property
    def monitoring_enabled(self) -> bool:
        """Мониторинг включен"""
        return self._settings.monitoring_enabled

    @property
    def monitoring_interval(self) -> int:
        """Интервал мониторинга"""
        return self._settings.monitoring_interval

    @property
    def health_check_enabled(self) -> bool:
        """Проверка здоровья включена"""
        return self._settings.health_check_enabled

    @property
    def secret_key(self) -> str:
        """Секретный ключ"""
        return self._settings.secret_key

    @property
    def jwt_algorithm(self) -> str:
        """Алгоритм JWT"""
        return self._settings.jwt_algorithm

    @property
    def jwt_expiration_hours(self) -> int:
        """Время жизни JWT"""
        return self._settings.jwt_expiration_hours

    @property
    def cache_enabled(self) -> bool:
        """Кеширование включено"""
        return self._settings.cache_enabled

    @property
    def cache_ttl(self) -> int:
        """Время жизни кеша"""
        return self._settings.cache_ttl

    def get_all_settings(self) -> Dict[str, Any]:
        """Получить все настройки"""
        return self._settings.model_dump()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Получить настройку по ключу"""
        return getattr(self._settings, key, default)

    def is_production(self) -> bool:
        """Проверить, является ли окружение production"""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Проверить, является ли окружение development"""
        return self.environment.lower() == "development"

    def get_database_config(self) -> Dict[str, Any]:
        """Получить конфигурацию базы данных"""
        return {
            "url": self.database_url,
            "echo": self.debug,
            "pool_size": 10,
            "max_overflow": 20,
            "pool_pre_ping": True,
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """Получить конфигурацию Redis"""
        return {
            "url": self.redis_url,
            "decode_responses": True,
        }

    def get_vk_api_config(self) -> Dict[str, Any]:
        """Получить конфигурацию VK API"""
        return {
            "access_token": self.vk_access_token,
            "api_version": self.vk_api_version,
        }

    def get_cors_config(self) -> Dict[str, Any]:
        """Получить конфигурацию CORS"""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Получить конфигурацию мониторинга"""
        return {
            "enabled": self.monitoring_enabled,
            "interval_seconds": self.monitoring_interval,
            "health_check_enabled": self.health_check_enabled,
        }

    def get_security_config(self) -> Dict[str, Any]:
        """Получить конфигурацию безопасности"""
        return {
            "secret_key": self.secret_key,
            "algorithm": self.jwt_algorithm,
            "expiration_hours": self.jwt_expiration_hours,
        }

    def get_cache_config(self) -> Dict[str, Any]:
        """Получить конфигурацию кеширования"""
        return {
            "enabled": self.cache_enabled,
            "ttl_seconds": self.cache_ttl,
        }

    # ARQ свойства
    @property
    def arq_enabled(self) -> bool:
        """ARQ включен"""
        return self._settings.arq_enabled

    @property
    def arq_max_jobs(self) -> int:
        """Максимальное количество одновременно выполняемых задач"""
        return self._settings.arq_max_jobs

    @property
    def arq_job_timeout(self) -> int:
        """Таймаут выполнения задачи"""
        return self._settings.arq_job_timeout

    @property
    def arq_keep_result(self) -> int:
        """Время хранения результатов задач"""
        return self._settings.arq_keep_result

    @property
    def arq_max_tries(self) -> int:
        """Максимальное количество попыток выполнения задачи"""
        return self._settings.arq_max_tries

    @property
    def arq_poll_delay(self) -> float:
        """Задержка между опросами очереди"""
        return self._settings.arq_poll_delay

    @property
    def arq_health_check_interval(self) -> int:
        """Интервал проверки здоровья"""
        return self._settings.arq_health_check_interval

    @property
    def arq_queue_name(self) -> str:
        """Имя очереди ARQ"""
        return self._settings.arq_queue_name

    @property
    def arq_burst_mode(self) -> bool:
        """Режим burst"""
        return self._settings.arq_burst_mode

    def get_arq_config(self) -> Dict[str, Any]:
        """Получить конфигурацию ARQ"""
        return {
            "enabled": self.arq_enabled,
            "max_jobs": self.arq_max_jobs,
            "job_timeout": self.arq_job_timeout,
            "keep_result": self.arq_keep_result,
            "max_tries": self.arq_max_tries,
            "poll_delay": self.arq_poll_delay,
            "health_check_interval": self.arq_health_check_interval,
            "queue_name": self.arq_queue_name,
            "burst_mode": self.arq_burst_mode,
        }


# Глобальный экземпляр сервиса конфигурации
config_service = ConfigService()
