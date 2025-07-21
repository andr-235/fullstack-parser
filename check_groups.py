#!/usr/bin/env python3
import asyncio
import sys
import os

# Добавляем путь к приложению
sys.path.append('/app')

from app.core.database import AsyncSessionLocal
from app.models.vk_group import VKGroup
from sqlalchemy import select, func

async def count_groups():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count(VKGroup.id)))
        total = result.scalar() or 0
        print(f"Всего групп в базе данных: {total}")
        
        # Проверяем активные группы
        active_result = await db.execute(select(func.count(VKGroup.id)).where(VKGroup.is_active == True))
        active = active_result.scalar() or 0
        print(f"Активных групп: {active}")
        
        # Проверяем группы с мониторингом
        monitored_result = await db.execute(select(func.count(VKGroup.id)).where(VKGroup.auto_monitoring_enabled == True))
        monitored = monitored_result.scalar() or 0
        print(f"Групп с мониторингом: {monitored}")

if __name__ == "__main__":
    asyncio.run(count_groups()) 