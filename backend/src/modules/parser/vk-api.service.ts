import { Injectable, Logger } from "@nestjs/common";
import { VK } from "vk-io";
import { ConfigService } from "@nestjs/config";

export interface VKUser {
  id: number;
  first_name: string;
  last_name: string;
  screen_name?: string;
  photo_100?: string;
  deactivated?: string;
}

export interface VKGroup {
  id: number;
  name: string;
  screen_name: string;
  photo_100?: string;
  type: string;
  is_closed: number;
  is_admin: number;
  is_member: number;
  is_advertiser: number;
}

export interface VKPost {
  id: number;
  owner_id: number;
  from_id: number;
  date: number;
  text: string;
  attachments?: any[];
  likes?: {
    count: number;
    user_likes: number;
    can_like: number;
    can_publish: number;
  };
  reposts?: {
    count: number;
    user_reposted: number;
  };
  comments?: {
    count: number;
    can_post?: number;
  };
  views?: {
    count: number;
  };
}

export interface VKComment {
  id: number;
  from_id: number;
  date: number;
  text: string;
  attachments?: any[];
  likes?: {
    count: number;
    user_likes: number;
    can_like: number;
  };
}

export interface VKWallResponse {
  count: number;
  items: VKPost[];
}

export interface VKCommentsResponse {
  count: number;
  items: VKComment[];
}

@Injectable()
export class VkApiService {
  private readonly logger = new Logger(VkApiService.name);
  private vk: VK;

  constructor(private configService: ConfigService) {
    const token = this.configService.get<string>("VK_ACCESS_TOKEN");

    if (!token) {
      this.logger.error("VK_TOKEN not found in environment variables");
      throw new Error("VK_TOKEN is required");
    }

    this.vk = new VK({
      token,
      apiVersion: "5.199",
    });

    this.logger.log("VK API service initialized");
  }

  /**
   * Получить информацию о пользователе
   */
  async getUser(userId: number | string): Promise<VKUser | null> {
    try {
      const response = await this.vk.api.users.get({
        user_ids: [userId],
        fields: ["screen_name", "photo_100"],
      });

      if (response && response.length > 0) {
        return response[0] as VKUser;
      }

      return null;
    } catch (error) {
      this.logger.error(`Failed to get user ${userId}:`, error);
      throw error;
    }
  }

  /**
   * Получить информацию о группе
   */
  async getGroup(groupId: number | string): Promise<VKGroup | null> {
    try {
      const response = await this.vk.api.groups.getById({
        group_id: groupId,
        fields: ["screen_name", "photo_100"],
      });

      return (response as unknown as VKGroup) || null;
    } catch (error) {
      this.logger.error(`Failed to get group ${groupId}:`, error);
      throw error;
    }
  }

  /**
   * Получить посты со стены
   */
  async getWallPosts(
    ownerId: number,
    count: number = 100,
    offset: number = 0
  ): Promise<VKWallResponse> {
    try {
      const response = await this.vk.api.wall.get({
        owner_id: ownerId,
        count,
        offset,
        extended: 1,
      });

      return {
        count: response.count,
        items: response.items,
      };
    } catch (error) {
      this.logger.error(`Failed to get wall posts for ${ownerId}:`, error);
      throw error;
    }
  }

  /**
   * Получить комментарии к посту
   */
  async getPostComments(
    ownerId: number,
    postId: number,
    count: number = 100,
    offset: number = 0
  ): Promise<VKCommentsResponse> {
    try {
      const response = await this.vk.api.wall.getComments({
        owner_id: ownerId,
        post_id: postId,
        count,
        offset,
        extended: 1,
        sort: "desc",
      });

      return {
        count: response.count,
        items: response.items,
      };
    } catch (error) {
      this.logger.error(
        `Failed to get comments for post ${postId} in ${ownerId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Поиск постов по запросу
   */
  async searchPosts(
    query: string,
    ownerId?: number,
    count: number = 100,
    offset: number = 0
  ): Promise<VKWallResponse> {
    try {
      const params: any = {
        query,
        count,
        offset,
        extended: 1,
      };

      if (ownerId) {
        params.owner_id = ownerId;
      }

      const response = await this.vk.api.wall.search(params);

      return {
        count: response.count,
        items: response.items,
      };
    } catch (error) {
      this.logger.error(`Failed to search posts with query "${query}":`, error);
      throw error;
    }
  }

  /**
   * Получить информацию о нескольких пользователях
   */
  async getUsers(userIds: (number | string)[]): Promise<VKUser[]> {
    try {
      const response = await this.vk.api.users.get({
        user_ids: userIds,
        fields: ["screen_name", "photo_100"],
      });

      return (response || []) as VKUser[];
    } catch (error) {
      this.logger.error(`Failed to get users ${userIds}:`, error);
      throw error;
    }
  }

  /**
   * Получить информацию о нескольких группах
   */
  async getGroups(groupIds: (number | string)[]): Promise<VKGroup[]> {
    try {
      const response = await this.vk.api.groups.getById({
        group_ids: groupIds,
        fields: ["screen_name", "photo_100"],
      });

      return (Array.isArray(response) ? response : [response]) as VKGroup[];
    } catch (error) {
      this.logger.error(`Failed to get groups ${groupIds}:`, error);
      throw error;
    }
  }

  /**
   * Проверить доступность токена
   */
  async checkToken(): Promise<boolean> {
    try {
      await this.vk.api.users.get({ user_ids: [1] });
      return true;
    } catch (error) {
      this.logger.error("VK token validation failed:", error);
      return false;
    }
  }

  /**
   * Получить статистику поста
   */
  async getPostStats(ownerId: number, postId: number): Promise<any> {
    try {
      const response = await this.vk.api.wall.getById({
        posts: `${ownerId}_${postId}`,
        extended: 1,
      });

      if (response && response.length > 0) {
        const post = response[0];
        return {
          likes: post.likes?.count || 0,
          reposts: post.reposts?.count || 0,
          comments: post.comments?.count || 0,
          views: post.views?.count || 0,
        };
      }

      return null;
    } catch (error) {
      this.logger.error(
        `Failed to get stats for post ${postId} in ${ownerId}:`,
        error
      );
      throw error;
    }
  }

  /**
   * Получить информацию о вложениях поста
   */
  async getPostAttachments(ownerId: number, postId: number): Promise<any[]> {
    try {
      const response = await this.vk.api.wall.getById({
        posts: `${ownerId}_${postId}`,
        extended: 1,
      });

      if (response && response.length > 0) {
        return response[0].attachments || [];
      }

      return [];
    } catch (error) {
      this.logger.error(
        `Failed to get attachments for post ${postId} in ${ownerId}:`,
        error
      );
      throw error;
    }
  }
}
