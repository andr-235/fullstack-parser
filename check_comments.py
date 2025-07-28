#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from app.core.database import get_db


async def check_comments():
    async for db in get_db():
        result = await db.execute(
            text(
                "SELECT author_name, author_screen_name, author_photo_url, author_id FROM vk_comment LIMIT 10"
            )
        )
        rows = result.fetchall()
        print("Sample comments:")
        for row in rows:
            print(
                f"ID: {row[3]}, Name: '{row[0]}', Screen: '{row[1]}', Photo: '{row[2]}'"
            )
        break


if __name__ == "__main__":
    asyncio.run(check_comments())
