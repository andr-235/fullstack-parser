#!/usr/bin/env python3
"""
Упрощенный скрипт для исправления данных комментариев
"""

import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Настройки базы данных из переменных окружения
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "vk_parser")

# URL для подключения к базе данных
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


async def fix_comments_data():
    """Исправляет данные комментариев"""

    print("🔍 Подключаемся к базе данных...")
    print(f"   URL: {DATABASE_URL}")

    # Создаем синхронное подключение
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        print("✅ Подключение установлено")

        # Проверяем количество комментариев
        result = session.execute(text("SELECT COUNT(*) FROM vk_comments"))
        comments_count = result.scalar()
        print(f"📊 Найдено комментариев: {comments_count}")

        # Проверяем количество постов
        result = session.execute(text("SELECT COUNT(*) FROM vk_posts"))
        posts_count = result.scalar()
        print(f"📝 Найдено постов: {posts_count}")

        # Проверяем количество групп
        result = session.execute(text("SELECT COUNT(*) FROM vk_groups"))
        groups_count = result.scalar()
        print(f"👥 Найдено групп: {groups_count}")

        # Анализируем связи комментариев с постами
        print("\n🔍 Анализируем связи...")

        # Комментарии без постов
        result = session.execute(
            text(
                """
            SELECT COUNT(*) FROM vk_comments c 
            LEFT JOIN vk_posts p ON c.post_id = p.id 
            WHERE p.id IS NULL
        """
            )
        )
        comments_without_post = result.scalar()
        print(f"   Комментариев без поста: {comments_without_post}")

        # Посты без групп
        result = session.execute(
            text(
                """
            SELECT COUNT(*) FROM vk_posts p 
            LEFT JOIN vk_groups g ON p.group_id = g.id 
            WHERE g.id IS NULL
        """
            )
        )
        posts_without_group = result.scalar()
        print(f"   Постов без группы: {posts_without_group}")

        # Комментарии с группами
        result = session.execute(
            text(
                """
            SELECT COUNT(*) FROM vk_comments c 
            JOIN vk_posts p ON c.post_id = p.id 
            JOIN vk_groups g ON p.group_id = g.id
        """
            )
        )
        comments_with_group = result.scalar()
        print(f"   Комментариев с группой: {comments_with_group}")

        # Добавляем колонку post_vk_id если её нет
        print("\n🔧 Проверяем структуру таблицы...")

        # Проверяем, есть ли колонка post_vk_id
        result = session.execute(
            text(
                """
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'vk_comments' AND column_name = 'post_vk_id'
        """
            )
        )

        if not result.fetchone():
            print("   Добавляем колонку post_vk_id...")
            session.execute(
                text("ALTER TABLE vk_comments ADD COLUMN post_vk_id INTEGER")
            )
            session.commit()
            print("   ✅ Колонка post_vk_id добавлена")
        else:
            print("   ✅ Колонка post_vk_id уже существует")

        # Обновляем post_vk_id для комментариев
        print("\n🔄 Обновляем post_vk_id...")

        result = session.execute(
            text(
                """
            UPDATE vk_comments 
            SET post_vk_id = p.vk_id 
            FROM vk_posts p 
            WHERE vk_comments.post_id = p.id 
            AND vk_comments.post_vk_id IS NULL
        """
            )
        )

        updated_count = result.rowcount
        session.commit()
        print(f"   ✅ Обновлено комментариев: {updated_count}")

        # Проверяем результат
        print("\n🔍 Проверяем результат...")

        result = session.execute(
            text(
                """
            SELECT c.id, c.post_vk_id, g.name as group_name
            FROM vk_comments c 
            JOIN vk_posts p ON c.post_id = p.id 
            JOIN vk_groups g ON p.group_id = g.id
            LIMIT 5
        """
            )
        )

        for row in result.fetchall():
            print(f"   Комментарий {row[0]}: post_vk_id={row[1]}, группа='{row[2]}'")

        # Статистика по группам
        print("\n📈 Статистика по группам:")
        result = session.execute(
            text(
                """
            SELECT g.name, COUNT(c.id) as comments_count
            FROM vk_groups g 
            JOIN vk_posts p ON g.id = p.group_id 
            JOIN vk_comments c ON p.id = c.post_id
            GROUP BY g.id, g.name
            ORDER BY comments_count DESC
            LIMIT 5
        """
            )
        )

        for row in result.fetchall():
            print(f"   {row[0]}: {row[1]} комментариев")

    print("\n✅ Скрипт завершен!")


if __name__ == "__main__":
    asyncio.run(fix_comments_data())
