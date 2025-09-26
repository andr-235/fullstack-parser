import logger from '../utils/logger';
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { RateLimiterMemory } from 'rate-limiter-flexible';
import axiosRetry from 'axios-retry';

// Интерфейсы для VK API ответов
interface VKError {
  error_code: number;
  error_msg: string;
  request_params?: Array<{ key: string; value: string }>;
}

interface VKResponse<T> {
  response?: T;
  error?: VKError;
}

interface VKPost {
  id: number;
  owner_id: number;
  from_id: number;
  date: number;
  text: string;
  likes: {
    count: number;
  };
  reposts?: {
    count: number;
  };
  views?: {
    count: number;
  };
  comments?: {
    count: number;
  };
}

interface VKComment {
  id: number;
  from_id: number;
  date: number;
  text: string;
  post_id: number;
  likes: {
    count: number;
  };
  reply_to_user?: number;
  reply_to_comment?: number;
  thread?: {
    count: number;
  };
}

interface VKProfile {
  id: number;
  first_name: string;
  last_name: string;
}

interface VKGroup {
  id: number;
  name: string;
  screen_name: string;
  description: string;
  type: string;
  is_closed: number;
  photo_50?: string;
  photo_100?: string;
  photo_200?: string;
  members_count?: number;
}

interface VKWallResponse {
  count: number;
  items: VKPost[];
}

interface VKCommentsResponse {
  count: number;
  items: VKComment[];
  profiles: VKProfile[];
  current_level_count?: number;
  can_post?: number;
}

// Интерфейсы для возвращаемых данных
export interface ProcessedPost {
  vk_post_id: number;
  owner_id: number;
  group_id: number;
  text: string;
  date: Date;
  likes: number;
}

export interface ProcessedComment {
  vk_comment_id: number;
  post_vk_id: number;
  owner_id: number;
  author_id: number;
  author_name: string;
  text: string;
  date: Date;
  likes: number;
}

export interface ProcessedGroup {
  id: number;
  name: string;
  screen_name: string;
  description: string;
}

export interface GetPostsResult {
  posts: ProcessedPost[];
}

export interface GetCommentsResult {
  comments: ProcessedComment[];
  hasMore: boolean;
}

class VKApi {
  private baseURL: string;
  private token: string;
  private version: string;
  private client: AxiosInstance;
  private rateLimiter: RateLimiterMemory;

  constructor() {
    this.baseURL = 'https://api.vk.com/method';
    this.token = process.env.VK_ACCESS_TOKEN || '';
    this.version = '5.199';

    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
    });

    this.rateLimiter = new RateLimiterMemory({
      points: 3,
      duration: 1,
    });

    // Interceptor для rate limiting
    this.client.interceptors.request.use(async (config: AxiosRequestConfig) => {
      await this.rateLimiter.consume('vk-api');
      return config;
    });

    // Retry config с exponential backoff
    axiosRetry(this.client, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      retryCondition: (error) => {
        return error.code === 'ECONNABORTED' || (error.response?.status || 0) >= 500;
      },
    });
  }

  /**
   * Выполняет запрос к VK API
   */
  private async _makeRequest<T>(method: string, params: Record<string, any>): Promise<T> {
    try {
      const response = await this.client.get<VKResponse<T>>(method, {
        params: {
          ...params,
          access_token: this.token,
          v: this.version,
        },
      });

      const data = response.data;
      if (data.error) {
        const error = new Error(`VK API error: ${data.error.error_msg} (code: ${data.error.error_code})`);
        logger.error('VK API error', { error: data.error, method });
        throw error;
      }

      if (!data.response) {
        throw new Error('Invalid VK API response: missing response field');
      }

      return data.response;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
          logger.error('HTTP Error', {
            status: error.response.status,
            message: error.message,
            method
          });
        } else if (error.request) {
          logger.error('Request Error', { message: error.message, method });
        } else {
          logger.error('Error', { message: error.message, method });
        }
      } else {
        logger.error('Unexpected error', { error, method });
      }
      throw error;
    }
  }

  /**
   * Получает посты группы
   */
  async getPosts(groupId: number): Promise<GetPostsResult> {
    const ownerId = -Math.abs(groupId); // Ensure negative for groups
    const params = {
      owner_id: ownerId,
      count: 10,
    };

    const response = await this._makeRequest<VKWallResponse>('wall.get', params);

    if (!response || !response.items) {
      logger.warn('No items in VK posts response', { groupId, ownerId });
      return { posts: [] };
    }

    logger.info('VK posts response received', { groupId, count: response.items.length });

    const posts = response.items.map(post => ({
      vk_post_id: post.id,
      owner_id: ownerId,
      group_id: Math.abs(groupId),
      text: post.text || '',
      date: new Date(post.date * 1000),
      likes: post.likes?.count || 0,
    }));

    return { posts };
  }

  /**
   * Получает комментарии к посту
   */
  async getComments(groupId: number, postVkId: number, offset: number = 0): Promise<GetCommentsResult> {
    const ownerId = -Math.abs(groupId); // Ensure negative for groups
    let allComments: ProcessedComment[] = [];
    let currentOffset = offset;
    let hasMore = true;
    let maxIterations = 100; // Максимум 10,000 комментариев (100 * 100)

    while (hasMore && maxIterations > 0) {
      maxIterations--;
      const params = {
        owner_id: ownerId,
        post_id: postVkId,
        offset: currentOffset,
        count: 100,
        extended: 1,
        fields: 'first_name,last_name',
      };

      const response = await this._makeRequest<VKCommentsResponse>('wall.getComments', params);
      const items = response.items || [];
      const profiles = response.profiles || [];

      // Create profile mapping for author names
      const profileMap = profiles.reduce((map, profile) => {
        map[profile.id] = `${profile.first_name} ${profile.last_name}`;
        return map;
      }, {} as Record<number, string>);

      const processedComments = items.map(comment => ({
        vk_comment_id: comment.id,
        post_vk_id: postVkId,
        owner_id: ownerId,
        author_id: comment.from_id,
        author_name: profileMap[comment.from_id] || `User ${comment.from_id}`,
        text: comment.text || '',
        date: new Date(comment.date * 1000),
        likes: comment.likes?.count || 0,
      }));

      allComments = allComments.concat(processedComments);

      if (items.length < 100) {
        hasMore = false;
      } else {
        currentOffset += 100;
      }
    }

    if (maxIterations <= 0) {
      logger.warn('Comments pagination reached maximum limit', {
        groupId,
        postVkId,
        currentOffset,
        commentsCount: allComments.length
      });
    }

    return { comments: allComments, hasMore: false };
  }

  /**
   * Получает информацию о группах
   */
  async getGroupsInfo(groupIds: number[]): Promise<ProcessedGroup[]> {
    if (!groupIds || groupIds.length === 0) {
      return [];
    }

    // Конвертируем в положительные ID для VK API
    const positiveIds = groupIds.map(id => Math.abs(id));

    const params = {
      group_ids: positiveIds.join(','),
      fields: 'name,screen_name,description'
    };

    try {
      const response = await this._makeRequest<VKGroup[]>('groups.getById', params);

      if (!response || !Array.isArray(response)) {
        logger.warn('Invalid response from groups.getById', { groupIds });
        return [];
      }

      return response.map(group => ({
        id: Math.abs(group.id), // Возвращаем положительный ID
        name: group.name,
        screen_name: group.screen_name,
        description: group.description
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Error fetching groups info', {
        groupIds,
        error: errorMsg
      });
      throw error;
    }
  }

  /**
   * Проверяет валидность токена
   */
  async validateToken(): Promise<boolean> {
    try {
      await this._makeRequest('account.getInfo', {});
      return true;
    } catch (error) {
      logger.error('Token validation failed', { error });
      return false;
    }
  }

  /**
   * Получает информацию о пользователе/группе по ID
   */
  async getUserInfo(userId: number): Promise<any> {
    try {
      const params = {
        user_ids: Math.abs(userId).toString(),
        fields: 'first_name,last_name,photo_50'
      };

      const response = await this._makeRequest('users.get', params);
      return response;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Error fetching user info', {
        userId,
        error: errorMsg
      });
      throw error;
    }
  }

  /**
   * Получает ограничения API
   */
  getRateLimiterStats(): {
    points: number;
    duration: number;
    remainingPoints: number;
  } {
    return {
      points: this.rateLimiter.points,
      duration: this.rateLimiter.duration,
      remainingPoints: this.rateLimiter.getTokensRemaining()
    };
  }
}

export default new VKApi();