#!/usr/bin/env python3

import asyncio

from sqlalchemy import select

from app.core.database import async_engine
from app.models import CommentKeywordMatch, Keyword, VKComment, VKGroup, VKPost


async def test_api():
    async with async_engine.begin() as conn:
        # Тестируем запрос как в API
        query = (
            select(VKComment)
            .outerjoin(VKPost, VKComment.post_id == VKPost.id)
            .outerjoin(VKGroup, VKPost.group_id == VKGroup.id)
        )

        result = await conn.execute(
            query.limit(1).order_by(VKComment.created_at.desc())
        )
        comments_with_relations = result.unique().all()

        print(f"Found {len(comments_with_relations)} comments")

        for comment, post, group in comments_with_relations:
            print(f"Comment ID: {comment.id}")
            print(f"Author name: {comment.author_name}")
            print(f"Author screen name: {comment.author_screen_name}")
            print(f"Author photo URL: {comment.author_photo_url}")
            print(f"Post ID: {post.id if post else 'None'}")
            print(f"Group: {group.name if group else 'None'}")

            # Получаем ключевые слова
            keyword_matches_query = (
                select(Keyword.word)
                .join(
                    CommentKeywordMatch,
                    Keyword.id == CommentKeywordMatch.keyword_id,
                )
                .where(CommentKeywordMatch.comment_id == comment.id)
            )

            keyword_result = await conn.execute(keyword_matches_query)
            matched_keywords = [kw for kw in keyword_result.scalars().all()]
            print(f"Matched keywords: {matched_keywords}")


if __name__ == "__main__":
    asyncio.run(test_api())
