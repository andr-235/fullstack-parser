#!/usr/bin/env python3
"""
Скрипт для исправления данных комментариев
Связывает комментарии с группами через посты и обновляет post_vk_id
"""

import asyncio
import os
import sys

# Добавляем путь к backend для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker

from app.core.config import settings
from app.models.vk_comment import VKComment
from app.models.vk_post import VKPost


async def fix_comments_data():
    """Исправляет данные комментариев"""

    # Создаем подключение к базе данных
    database_url = (
        str(settings.database.url) if settings.database.url else None
    )
    if not database_url:
        print("❌ Не удалось получить URL базы данных")
        return

    engine = create_async_engine(database_url)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("🔍 Анализируем данные комментариев...")

        # Получаем все комментарии
        result = await session.execute(select(VKComment))
        comments = result.scalars().all()

        print(f"📊 Найдено комментариев: {len(comments)}")

        # Получаем все посты с группами
        posts_result = await session.execute(
            select(VKPost).options(selectinload(VKPost.group))
        )
        posts = posts_result.scalars().all()

        print(f"📝 Найдено постов: {len(posts)}")

        # Создаем словарь постов для быстрого поиска
        posts_dict = {post.id: post for post in posts}

        # Анализируем комментарии
        comments_without_post = 0
        comments_without_group = 0
        comments_fixed = 0

        for comment in comments:
            post = posts_dict.get(comment.post_id)

            if not post:
                comments_without_post += 1
                print(
                    f"⚠️  Комментарий {comment.id} ссылается на несуществующий пост {comment.post_id}"
                )
                continue

            if not post.group:
                comments_without_group += 1
                print(f"⚠️  Пост {post.id} не связан с группой")
                continue

            # Проверяем, нужно ли обновить post_vk_id
            if (
                not hasattr(comment, "post_vk_id")
                or comment.post_vk_id is None
            ):
                comment.post_vk_id = post.vk_id
                comments_fixed += 1
                print(
                    f"✅ Обновлен post_vk_id для комментария {comment.id}: {post.vk_id}"
                )

        # Сохраняем изменения
        if comments_fixed > 0:
            await session.commit()
            print(f"💾 Сохранено изменений: {comments_fixed}")

        print("\n📈 Статистика:")
        print(f"   - Комментариев без поста: {comments_without_post}")
        print(f"   - Постов без группы: {comments_without_group}")
        print(f"   - Исправлено комментариев: {comments_fixed}")

        # Проверяем результат
        print("\n🔍 Проверяем результат...")

        # Получаем несколько комментариев для проверки
        test_result = await session.execute(
            select(VKComment)
            .options(selectinload(VKComment.post).selectinload(VKPost.group))
            .limit(5)
        )
        test_comments = test_result.scalars().all()

        for comment in test_comments:
            group_name = (
                comment.post.group.name
                if comment.post and comment.post.group
                else "N/A"
            )
            post_vk_id = getattr(comment, "post_vk_id", None)
            print(
                f"   Комментарий {comment.id}: группа='{group_name}', post_vk_id={post_vk_id}"
            )

    await engine.dispose()
    print("\n✅ Скрипт завершен!")


if __name__ == "__main__":
    asyncio.run(fix_comments_data())
