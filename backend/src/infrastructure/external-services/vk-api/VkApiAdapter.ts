/**
 * @fileoverview VkApiAdapter - реализация IVkApiRepository
 *
 * Infrastructure adapter для работы с VK API через vk-io библиотеку.
 */

import { VK } from 'vk-io';
import {
  IVkApiRepository,
  VkGroupInfo,
  VkPostInfo,
  VkCommentInfo,
  VkApiBatchResult
} from '@domain/repositories/IVkApiRepository';
import { VkId } from '@domain/value-objects/VkId';
import logger from '@infrastructure/utils/logger';

/**
 * VK API Adapter через vk-io
 *
 * @description
 * Адаптер для работы с VKontakte API.
 * Скрывает детали vk-io библиотеки от Domain Layer.
 */
export class VkApiAdapter implements IVkApiRepository {
  private readonly vk: VK;
  private readonly batchSize = 500; // VK API лимит для groups.getById

  constructor(accessToken: string) {
    if (!accessToken) {
      throw new Error('VK access token is required');
    }

    this.vk = new VK({
      token: accessToken,
      apiLimit: 3 // 3 запроса в секунду
    });

    logger.info('VkApiAdapter initialized');
  }

  /**
   * Получает информацию о группе
   */
  async getGroupInfo(identifier: VkId | string): Promise<VkGroupInfo> {
    try {
      const groupId = typeof identifier === 'string'
        ? identifier
        : identifier.toNegative().toString();

      const response: any = await this.vk.api.groups.getById({
        group_id: groupId,
        fields: ['description', 'members_count', 'screen_name']
      });

      const groups = Array.isArray(response) ? response : [response];
      const group = groups[0];

      if (!group) {
        throw new Error(`Group ${identifier} not found`);
      }

      return this.mapVkGroupToInfo(group);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get group info', { identifier, error: errorMsg });
      throw new Error(`Failed to get group info: ${errorMsg}`);
    }
  }

  /**
   * Получает информацию о нескольких группах батчами
   */
  async getGroupsInfo(identifiers: ReadonlyArray<VkId | string>): Promise<VkApiBatchResult<VkGroupInfo>> {
    const successful: VkGroupInfo[] = [];
    const failed: Array<{ identifier: string | number; error: string }> = [];

    // Обрабатываем батчами по 500 групп
    for (let i = 0; i < identifiers.length; i += this.batchSize) {
      const batch = identifiers.slice(i, i + this.batchSize);

      try {
        // Преобразуем идентификаторы для VK API
        const groupIds = batch.map(id => {
          if (typeof id === 'string') {
            return id;
          }
          // Для VK API нужны отрицательные ID для групп
          return Math.abs(id.value).toString();
        }).join(',');

        // Запрос к VK API
        const response: any = await this.vk.api.groups.getById({
          group_ids: groupIds as any,
          fields: ['description', 'members_count', 'screen_name'] as any
        });

        const groups = Array.isArray(response) ? response : [response];

        // Маппим успешные результаты
        for (const group of groups) {
          successful.push(this.mapVkGroupToInfo(group));
        }

        // Находим не найденные группы
        const foundIds = new Set(groups.map(g => g.id));
        for (const id of batch) {
          const numericId = typeof id === 'string' ? null : Math.abs(id.value);
          if (numericId && !foundIds.has(numericId)) {
            failed.push({
              identifier: numericId,
              error: 'Group not found or not accessible'
            });
          }
        }

        // Задержка между батчами для соблюдения rate limits
        if (i + this.batchSize < identifiers.length) {
          await this.delay(350); // ~3 запроса в секунду
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        logger.error('Batch request to VK API failed', {
          batchNumber: Math.floor(i / this.batchSize) + 1,
          error: errorMsg
        });

        // Помечаем весь батч как failed
        for (const id of batch) {
          failed.push({
            identifier: typeof id === 'string' ? id : id.value,
            error: errorMsg
          });
        }
      }
    }

    logger.info('VK API batch requests completed', {
      total: identifiers.length,
      successful: successful.length,
      failed: failed.length
    });

    return { successful, failed };
  }

  /**
   * Проверяет доступность группы
   */
  async isGroupAccessible(identifier: VkId | string): Promise<boolean> {
    try {
      await this.getGroupInfo(identifier);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Получает информацию о посте
   */
  async getPost(ownerId: number, postId: number): Promise<VkPostInfo> {
    try {
      const posts = await this.vk.api.wall.getById({
        posts: `${ownerId}_${postId}`,
        extended: 1
      });

      if (!posts || posts.length === 0) {
        throw new Error(`Post ${ownerId}_${postId} not found`);
      }

      const post = posts[0];

      return {
        id: post.id,
        ownerId: post.owner_id || ownerId,
        fromId: post.from_id || ownerId,
        date: new Date(post.date * 1000),
        text: post.text || '',
        commentsCount: post.comments?.count || 0,
        likesCount: post.likes?.count || 0,
        repostsCount: post.reposts?.count || 0,
        viewsCount: post.views?.count || 0
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get post', { ownerId, postId, error: errorMsg });
      throw new Error(`Failed to get post: ${errorMsg}`);
    }
  }

  /**
   * Получает комментарии к посту
   */
  async getPostComments(
    ownerId: number,
    postId: number,
    options?: {
      readonly offset?: number;
      readonly count?: number;
      readonly sort?: 'asc' | 'desc';
      readonly needLikes?: boolean;
    }
  ): Promise<readonly VkCommentInfo[]> {
    try {
      const response = await this.vk.api.wall.getComments({
        owner_id: ownerId,
        post_id: postId,
        offset: options?.offset || 0,
        count: options?.count || 100,
        sort: options?.sort || 'asc',
        need_likes: options?.needLikes ? 1 : 0,
        extended: 1
      });

      return response.items.map(comment => ({
        id: comment.id,
        postId,
        fromId: comment.from_id,
        date: new Date(comment.date * 1000),
        text: comment.text,
        likesCount: comment.likes?.count || 0,
        replyToUser: comment.reply_to_user || null,
        replyToComment: comment.reply_to_comment || null
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get post comments', { ownerId, postId, error: errorMsg });
      throw new Error(`Failed to get comments: ${errorMsg}`);
    }
  }

  /**
   * Проверяет валидность токена
   */
  async isTokenValid(): Promise<boolean> {
    try {
      await this.vk.api.users.get({});
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Получает информацию о текущем пользователе
   */
  async getCurrentUser(): Promise<{
    readonly id: number;
    readonly firstName: string;
    readonly lastName: string;
  }> {
    try {
      const [user] = await this.vk.api.users.get({});

      return {
        id: user.id,
        firstName: user.first_name,
        lastName: user.last_name
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get current user', { error: errorMsg });
      throw new Error(`Failed to get current user: ${errorMsg}`);
    }
  }

  // ============ Private Helpers ============

  /**
   * Преобразует VK API группу в VkGroupInfo
   */
  private mapVkGroupToInfo(vkGroup: any): VkGroupInfo {
    return {
      id: vkGroup.id,
      name: vkGroup.name,
      screenName: vkGroup.screen_name || '',
      description: vkGroup.description || null,
      photo50: vkGroup.photo_50 || null,
      membersCount: vkGroup.members_count || 0,
      isClosed: (vkGroup.is_closed ?? 0) as 0 | 1 | 2
    };
  }

  /**
   * Задержка в миллисекундах
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
