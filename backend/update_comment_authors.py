#!/usr/bin/env python3
"""
Скрипт для обновления информации об авторах комментариев из VK API
"""

import asyncio

import structlog
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.vk_comment import VKComment
from app.services.vk_api_service import VKAPIService

logger = structlog.get_logger()


async def update_comment_authors():
    """Обновляет информацию об авторах комментариев из VK API"""

    db = await anext(get_db())
    try:
        # Получаем все комментарии с fallback именами
        result = await db.execute(
            select(VKComment).where(
                VKComment.author_name.like("Пользователь %")
            )
        )
        comments = result.scalars().all()

        logger.info(f"Найдено {len(comments)} комментариев для обновления")

        if not comments:
            logger.info("Нет комментариев для обновления")
            return

        # Создаем VK API сервис
        vk_service = VKAPIService(
            token=settings.vk.access_token,
            api_version=settings.vk.api_version,
        )

        updated_count = 0
        error_count = 0

        for comment in comments:
            try:
                if comment.author_id > 0:
                    # Получаем информацию о пользователе
                    user_info = await vk_service.get_user_info(
                        comment.author_id
                    )

                    if user_info:
                        # Формируем полное имя
                        first_name = user_info.get("first_name", "")
                        last_name = user_info.get("last_name", "")
                        name = f"{first_name} {last_name}".strip()

                        # Получаем screen_name
                        screen_name = user_info.get("screen_name", "")

                        # Получаем URL фото
                        photo_url = user_info.get("photo_100", "")

                        # Обновляем комментарий
                        comment.author_name = name
                        comment.author_screen_name = screen_name
                        comment.author_photo_url = photo_url

                        updated_count += 1
                        logger.info(
                            f"Обновлен комментарий {comment.id}: {name} (@{screen_name})"
                        )
                    else:
                        logger.warning(
                            f"Не удалось получить данные пользователя {comment.author_id}"
                        )
                        error_count += 1
                else:
                    # Группа
                    group_id = abs(comment.author_id)
                    group_info = await vk_service.get_group_info(group_id)

                    if group_info:
                        name = group_info.get("name", "")
                        screen_name = group_info.get("screen_name", "")
                        photo_url = group_info.get("photo_100", "")

                        # Обновляем комментарий
                        comment.author_name = name
                        comment.author_screen_name = screen_name
                        comment.author_photo_url = photo_url

                        updated_count += 1
                        logger.info(
                            f"Обновлен комментарий {comment.id}: {name} (@{screen_name})"
                        )
                    else:
                        logger.warning(
                            f"Не удалось получить данные группы {group_id}"
                        )
                        error_count += 1

                # Сохраняем изменения каждые 10 комментариев
                if updated_count % 10 == 0:
                    await db.commit()
                    logger.info(f"Сохранено {updated_count} обновлений")

            except Exception as e:
                logger.error(
                    f"Ошибка обновления комментария {comment.id}: {e}"
                )
                error_count += 1

        # Финальное сохранение
        await db.commit()

        logger.info(
            f"Обновление завершено. Обновлено: {updated_count}, ошибок: {error_count}"
        )

        await vk_service.close()
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(update_comment_authors())
