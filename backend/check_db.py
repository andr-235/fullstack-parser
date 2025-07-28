#!/usr/bin/env python3

import asyncio
from app.core.database import engine


async def check_data():
    async with engine.begin() as conn:
        # Проверяем количество комментариев
        result = await conn.execute("SELECT COUNT(*) FROM vk_comments")
        comments_count = result.scalar()
        print(f"Comments: {comments_count}")

        # Проверяем количество постов
        result = await conn.execute("SELECT COUNT(*) FROM vk_posts")
        posts_count = result.scalar()
        print(f"Posts: {posts_count}")

        # Проверяем количество групп
        result = await conn.execute("SELECT COUNT(*) FROM vk_groups")
        groups_count = result.scalar()
        print(f"Groups: {groups_count}")

        # Проверяем связи комментариев с постами
        result = await conn.execute(
            """
            SELECT c.id, c.author_name, p.id as post_id, g.name as group_name 
            FROM vk_comments c 
            LEFT JOIN vk_posts p ON c.post_id = p.id 
            LEFT JOIN vk_groups g ON p.group_id = g.id 
            LIMIT 5
        """
        )
        rows = result.fetchall()
        print(f"\nSample comments with groups:")
        for row in rows:
            print(
                f"Comment {row[0]}: author={row[1]}, post={row[2]}, group={row[3]}"
            )


if __name__ == "__main__":
    asyncio.run(check_data())
