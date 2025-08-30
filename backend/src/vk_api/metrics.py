"""
Production-ready metrics and monitoring for VK API module

Этот модуль предоставляет комплексную систему метрик для мониторинга
производительности и здоровья VK API сервиса.
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque
import psutil


@dataclass
class MetricPoint:
    """Точка метрики с временной меткой"""

    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Counter:
    """Счетчик метрики"""

    name: str
    description: str
    value: int = 0
    tags: Dict[str, str] = field(default_factory=dict)

    def increment(self, amount: int = 1) -> None:
        """Увеличить счетчик"""
        self.value += amount

    def reset(self) -> None:
        """Сбросить счетчик"""
        self.value = 0


@dataclass
class Gauge:
    """Измеритель метрики"""

    name: str
    description: str
    value: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)

    def set(self, value: float) -> None:
        """Установить значение"""
        self.value = value

    def increment(self, amount: float = 1.0) -> None:
        """Увеличить значение"""
        self.value += amount

    def decrement(self, amount: float = 1.0) -> None:
        """Уменьшить значение"""
        self.value -= amount


@dataclass
class Histogram:
    """Гистограмма для измерения распределения"""

    name: str
    description: str
    buckets: List[float] = field(
        default_factory=lambda: [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
    )
    counts: Dict[float, int] = field(default_factory=dict)
    sum: float = 0.0
    count: int = 0
    tags: Dict[str, str] = field(default_factory=dict)

    def observe(self, value: float) -> None:
        """Добавить наблюдение"""
        self.sum += value
        self.count += 1

        for bucket in self.buckets:
            if value <= bucket:
                self.counts[bucket] = self.counts.get(bucket, 0) + 1

    def reset(self) -> None:
        """Сбросить гистограмму"""
        self.counts.clear()
        self.sum = 0.0
        self.count = 0


class VKAPIMetrics:
    """
    Метрики для мониторинга VK API сервиса

    Собирает и предоставляет метрики для:
    - Количества запросов и ответов
    - Времени отклика
    - Ошибок и сбоев
    - Использования ресурсов
    - Состояния circuit breakers
    """

    def __init__(self):
        # Счетчики запросов
        self.requests_total = Counter(
            "vk_api_requests_total", "Total number of VK API requests"
        )
        self.requests_success = Counter(
            "vk_api_requests_success", "Number of successful VK API requests"
        )
        self.requests_error = Counter(
            "vk_api_requests_error", "Number of failed VK API requests"
        )

        # Метрики по методам
        self.requests_by_method = defaultdict(
            lambda: Counter(
                f"vk_api_requests_method_{{method}}",
                "Requests by VK API method",
            )
        )

        # Гистограммы времени отклика
        self.request_duration = Histogram(
            "vk_api_request_duration_seconds",
            "VK API request duration in seconds",
        )

        # Метрики circuit breaker
        self.circuit_breaker_state = Gauge(
            "vk_api_circuit_breaker_state",
            "Circuit breaker state (0=closed, 1=open, 2=half_open)",
        )
        self.circuit_breaker_failures = Counter(
            "vk_api_circuit_breaker_failures", "Circuit breaker failure count"
        )

        # Метрики rate limiter
        self.rate_limiter_rejected = Counter(
            "vk_api_rate_limiter_rejected",
            "Number of requests rejected by rate limiter",
        )

        # Метрики кеша
        self.cache_hits = Counter("vk_api_cache_hits", "Number of cache hits")
        self.cache_misses = Counter(
            "vk_api_cache_misses", "Number of cache misses"
        )

        # Метрики массовых операций
        self.bulk_operations_total = Counter(
            "vk_api_bulk_operations_total", "Total bulk operations"
        )
        self.bulk_operations_success = Counter(
            "vk_api_bulk_operations_success", "Successful bulk operations"
        )
        self.bulk_operations_error = Counter(
            "vk_api_bulk_operations_error", "Failed bulk operations"
        )

        # Системные метрики
        self.memory_usage = Gauge(
            "vk_api_memory_usage_mb", "Memory usage in MB"
        )
        self.cpu_usage = Gauge(
            "vk_api_cpu_usage_percent", "CPU usage percentage"
        )

        # Временные ряды для трендов
        self.response_time_history = deque(maxlen=1000)
        self.error_rate_history = deque(maxlen=100)

        # Мьютекс для потокобезопасности
        self._lock = threading.Lock()

        # Запуск сбора системных метрик
        self._start_system_metrics_collection()

    def _start_system_metrics_collection(self) -> None:
        """Запуск периодического сбора системных метрик"""

        def collect_system_metrics():
            while True:
                try:
                    with self._lock:
                        # Сбор метрик памяти
                        memory_mb = (
                            psutil.Process().memory_info().rss / 1024 / 1024
                        )
                        self.memory_usage.set(memory_mb)

                        # Сбор метрик CPU
                        cpu_percent = psutil.Process().cpu_percent()
                        self.cpu_usage.set(cpu_percent)

                    time.sleep(30)  # Сбор каждые 30 секунд
                except Exception:
                    time.sleep(60)  # При ошибке ждем минуту

        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()

    def record_request(
        self,
        method: str,
        duration: float,
        success: bool,
        error_type: Optional[str] = None,
    ) -> None:
        """Записать метрики запроса"""
        with self._lock:
            self.requests_total.increment()
            self.requests_by_method[method].increment()

            if success:
                self.requests_success.increment()
            else:
                self.requests_error.increment()

            self.request_duration.observe(duration)
            self.response_time_history.append(
                (datetime.now(timezone.utc), duration)
            )

            # Обновление error rate
            recent_errors = sum(
                1 for _, d in self.response_time_history if d > 5.0
            )  # Считаем ошибки как запросы > 5 сек
            if self.response_time_history:
                error_rate = recent_errors / len(self.response_time_history)
                self.error_rate_history.append(
                    (datetime.now(timezone.utc), error_rate)
                )

    def record_circuit_breaker_event(
        self, state: str, failure_count: int = 0
    ) -> None:
        """Записать событие circuit breaker"""
        with self._lock:
            state_value = {"closed": 0, "open": 1, "half_open": 2}.get(
                state, 0
            )
            self.circuit_breaker_state.set(state_value)

            if failure_count > 0:
                self.circuit_breaker_failures.increment(failure_count)

    def record_rate_limit_event(self) -> None:
        """Записать событие rate limiting"""
        with self._lock:
            self.rate_limiter_rejected.increment()

    def record_cache_event(self, hit: bool) -> None:
        """Записать событие кеша"""
        with self._lock:
            if hit:
                self.cache_hits.increment()
            else:
                self.cache_misses.increment()

    def record_bulk_operation(
        self, total_items: int, success_count: int, duration: float
    ) -> None:
        """Записать метрики массовой операции"""
        with self._lock:
            self.bulk_operations_total.increment()

            if success_count == total_items:
                self.bulk_operations_success.increment()
            else:
                self.bulk_operations_error.increment()

            # Записываем как обычный запрос для консистентности
            success = success_count > 0
            self.record_request("bulk_operation", duration, success)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Получить сводную статистику"""
        with self._lock:
            total_requests = self.requests_total.value
            success_requests = self.requests_success.value

            return {
                "total_requests": total_requests,
                "success_rate": (
                    (success_requests / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
                "error_rate": (
                    (self.requests_error.value / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
                "avg_response_time": (
                    (self.request_duration.sum / self.request_duration.count)
                    if self.request_duration.count > 0
                    else 0
                ),
                "cache_hit_rate": (
                    (
                        self.cache_hits.value
                        / (self.cache_hits.value + self.cache_misses.value)
                        * 100
                    )
                    if (self.cache_hits.value + self.cache_misses.value) > 0
                    else 0
                ),
                "circuit_breaker_failures": self.circuit_breaker_failures.value,
                "rate_limiter_rejections": self.rate_limiter_rejected.value,
                "memory_usage_mb": self.memory_usage.value,
                "cpu_usage_percent": self.cpu_usage.value,
                "bulk_operations_success_rate": (
                    (
                        self.bulk_operations_success.value
                        / self.bulk_operations_total.value
                        * 100
                    )
                    if self.bulk_operations_total.value > 0
                    else 0
                ),
            }

    def get_health_status(self) -> Dict[str, Any]:
        """Получить статус здоровья сервиса"""
        with self._lock:
            stats = self.get_summary_stats()

            # Определяем статус здоровья
            if stats["error_rate"] > 50:
                health_status = "critical"
            elif stats["error_rate"] > 20:
                health_status = "warning"
            elif stats["avg_response_time"] > 10:
                health_status = "degraded"
            else:
                health_status = "healthy"

            return {
                "status": health_status,
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "metrics": stats,
                "checks": {
                    "error_rate_check": stats["error_rate"] < 20,
                    "response_time_check": stats["avg_response_time"] < 5,
                    "memory_check": stats["memory_usage_mb"]
                    < 1000,  # 1GB limit
                    "circuit_breaker_check": self.circuit_breaker_state.value
                    == 0,
                },
            }

    def reset_all_metrics(self) -> None:
        """Сбросить все метрики"""
        with self._lock:
            # Сброс счетчиков
            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if hasattr(attr, "reset"):
                    attr.reset()

            # Очистка истории
            self.response_time_history.clear()
            self.error_rate_history.clear()

    def export_metrics(self, format: str = "dict") -> Any:
        """Экспорт метрик в различных форматах"""
        if format == "dict":
            return self._export_as_dict()
        elif format == "prometheus":
            return self._export_as_prometheus()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_as_dict(self) -> Dict[str, Any]:
        """Экспорт в формате словаря"""
        with self._lock:
            return {
                "counters": {
                    "requests_total": self.requests_total.value,
                    "requests_success": self.requests_success.value,
                    "requests_error": self.requests_error.value,
                    "cache_hits": self.cache_hits.value,
                    "cache_misses": self.cache_misses.value,
                    "circuit_breaker_failures": self.circuit_breaker_failures.value,
                    "rate_limiter_rejections": self.rate_limiter_rejected.value,
                },
                "gauges": {
                    "circuit_breaker_state": self.circuit_breaker_state.value,
                    "memory_usage_mb": self.memory_usage.value,
                    "cpu_usage_percent": self.cpu_usage.value,
                },
                "histograms": {
                    "request_duration": {
                        "sum": self.request_duration.sum,
                        "count": self.request_duration.count,
                        "buckets": dict(self.request_duration.counts),
                    }
                },
                "summary": self.get_summary_stats(),
                "health": self.get_health_status(),
            }

    def _export_as_prometheus(self) -> str:
        """Экспорт в формате Prometheus"""
        lines = []

        # Counters
        lines.append(
            f"# HELP {self.requests_total.name} {self.requests_total.description}"
        )
        lines.append(f"# TYPE {self.requests_total.name} counter")
        lines.append(f"{self.requests_total.name} {self.requests_total.value}")

        lines.append(
            f"# HELP {self.requests_success.name} {self.requests_success.description}"
        )
        lines.append(f"# TYPE {self.requests_success.name} counter")
        lines.append(
            f"{self.requests_success.name} {self.requests_success.value}"
        )

        # Gauges
        lines.append(
            f"# HELP {self.memory_usage.name} {self.memory_usage.description}"
        )
        lines.append(f"# TYPE {self.memory_usage.name} gauge")
        lines.append(f"{self.memory_usage.name} {self.memory_usage.value}")

        lines.append(
            f"# HELP {self.cpu_usage.name} {self.cpu_usage.description}"
        )
        lines.append(f"# TYPE {self.cpu_usage.name} gauge")
        lines.append(f"{self.cpu_usage.name} {self.cpu_usage.value}")

        return "\n".join(lines)


# Глобальный экземпляр метрик
vk_api_metrics = VKAPIMetrics()


# Экспорт
__all__ = [
    "VKAPIMetrics",
    "vk_api_metrics",
    "Counter",
    "Gauge",
    "Histogram",
    "MetricPoint",
]
