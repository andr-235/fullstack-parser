#!/usr/bin/env python3
"""
Тестовый скрипт для проверки MonitoringService
"""

import asyncio

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.vk_api_service import VKAPIService


async def test_monitoring_service():
    """Тестирует MonitoringService"""
    async with AsyncSessionLocal() as db:
        vk_service = VKAPIService(
            token=settings.vk.access_token, api_version=settings.vk.api_version
        )
        monitoring_service = MonitoringService(db=db, vk_service=vk_service)

        print("🔍 Запускаем get_monitoring_stats...")
        stats = await monitoring_service.get_monitoring_stats()
        print("📊 Stats from MonitoringService:", stats)

        # Проверяем, есть ли поле next_monitoring_at_local
        if "next_monitoring_at_local" in stats:
            print(
                "✅ Поле next_monitoring_at_local найдено:",
                stats["next_monitoring_at_local"],
            )
        else:
            print("❌ Поле next_monitoring_at_local НЕ найдено")

        # Проверяем, есть ли поле next_monitoring_at
        if "next_monitoring_at" in stats:
            print("📅 next_monitoring_at:", stats["next_monitoring_at"])

            # Попробуем конвертировать вручную
            from datetime import datetime

            from app.core.time_utils import format_datetime_for_display

            try:
                utc_time = datetime.fromisoformat(stats["next_monitoring_at"])
                local_time = format_datetime_for_display(utc_time)
                print("🕐 Конвертированное время:", local_time)
            except Exception as e:
                print("❌ Ошибка конвертации:", e)
        else:
            print("❌ Поле next_monitoring_at НЕ найдено")


if __name__ == "__main__":
    asyncio.run(test_monitoring_service())
