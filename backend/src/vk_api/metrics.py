"""
Простая система метрик для VK API
"""

import time
from typing import Any, Dict


class VKAPIMetrics:
    """Простая система метрик"""

    def __init__(self):
        self._requests = 0
        self._errors = 0
        self._start_time = time.time()

    def record_request(self, success: bool = True) -> None:
        """Записать запрос"""
        self._requests += 1
        if not success:
            self._errors += 1

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику"""
        uptime = time.time() - self._start_time
        return {
            "uptime_seconds": uptime,
            "total_requests": self._requests,
            "error_requests": self._errors,
            "success_rate": ((self._requests - self._errors) / self._requests * 100) if self._requests > 0 else 0,
            "requests_per_second": self._requests / uptime if uptime > 0 else 0
        }


# Глобальный экземпляр метрик
metrics = VKAPIMetrics()

__all__ = ["VKAPIMetrics", "metrics"]
