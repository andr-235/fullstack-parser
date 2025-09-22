#!/usr/bin/env python3
"""
Скрипт для исправления времени мониторинга в базе данных
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.vk_group import VKGroup


async def fix_monitoring_times():
    """Исправить время мониторинга в базе данных"""
    async with AsyncSessionLocal() as db:
        # Получаем все группы с мониторингом
        result = await db.execute(
            select(VKGroup).where(VKGroup.auto_monitoring_enabled == True)
        )
        groups = result.scalars().all()

        print(f"Найдено {len(groups)} групп с мониторингом")

        for group in groups:
            if group.next_monitoring_at:
                # Если время без часового пояса, добавляем UTC
                if group.next_monitoring_at.tzinfo is None:
                    print(f"Исправляем время для группы {group.name}")
                    # Добавляем 11 часов (разница между старым и новым расчетом)
                    fixed_time = group.next_monitoring_at.replace(
                        tzinfo=timezone.utc
                    ) - timezone.utc.utcoffset(datetime.now())
                    group.next_monitoring_at = fixed_time

            if (
                group.last_monitoring_success
                and group.last_monitoring_success.tzinfo is None
            ):
                print(
                    f"Исправляем время последнего запуска для группы {group.name}"
                )
                group.last_monitoring_success = (
                    group.last_monitoring_success.replace(tzinfo=timezone.utc)
                )

        # Сохраняем изменения
        await db.commit()
        print("Исправления сохранены в базе данных")


if __name__ == "__main__":
    asyncio.run(fix_monitoring_times())
