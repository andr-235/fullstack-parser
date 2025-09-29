import logger from '../utils/logger';
import { prisma } from '../config/prisma';
import { tasks, posts, comments, Prisma } from '@prisma/client';
import {
  TASK_STATUSES,
  TASK_TYPES,
  PAGINATION_DEFAULTS,
  DEFAULT_VALUES,
  TaskStatus,
  TaskType
} from '../constants';
import { ERROR_MESSAGES } from '../constants/errors';

// Интерфейсы для запросов
interface ListTasksOptions {
  limit: number;
  offset: number;
  status?: TaskStatus;
  type?: TaskType;
}

interface ListTasksResult {
  tasks: tasks[];
  total: number;
}

interface GetResultsResult {
  posts: (posts & { comments: comments[] })[];
  totalComments: number;
}

interface TaskUpdateData {
  status?: TaskStatus;
  progress?: number;
  error?: string;
  result?: Prisma.JsonValue;
  finishedAt?: Date;
  metrics?: Prisma.JsonValue;
  parameters?: Prisma.JsonValue;
  executionTime?: number;
  startedAt?: Date;
}

interface CreateTaskData {
  type?: TaskType;
  priority?: number;
  groups?: Prisma.JsonValue;
  parameters?: Prisma.JsonValue;
  metadata?: Prisma.JsonValue;
  status?: TaskStatus;
  createdBy?: string;
}

class DBRepo {
  constructor() {
    // Prisma Client используется напрямую через импорт
  }

  /**
   * Создает новую задачу
   */
  async createTask(taskData: CreateTaskData): Promise<tasks> {
    const task = await prisma.tasks.create({
      data: {
        type: taskData.type || TASK_TYPES.FETCH_COMMENTS,
        status: taskData.status || TASK_STATUSES.PENDING,
        groups: taskData.groups || [],
        parameters: taskData.parameters || {},
        metrics: taskData.metadata || {},
        progress: DEFAULT_VALUES.PROGRESS_INITIAL,
        priority: taskData.priority || DEFAULT_VALUES.LIKES_COUNT,
        createdBy: taskData.createdBy || DEFAULT_VALUES.CREATED_BY,
        updatedAt: new Date()
      }
    });
    return task;
  }

  /**
   * Получает задачу по ID
   */
  async getTaskById(taskId: number): Promise<tasks> {
    const task = await prisma.tasks.findUnique({
      where: { id: taskId }
    });
    if (!task) {
      throw new Error(`${ERROR_MESSAGES.TASK_NOT_FOUND}: ${taskId}`);
    }
    return task;
  }

  /**
   * Обновляет задачу
   */
  async updateTask(taskId: number, updates: TaskUpdateData): Promise<tasks> {
    try {
      const updatedTask = await prisma.tasks.update({
        where: { id: taskId },
        data: {
          ...(updates.status && { status: updates.status }),
          ...(updates.progress !== undefined && { progress: updates.progress }),
          ...(updates.error !== undefined && { error: updates.error }),
          ...(updates.result !== undefined && { result: updates.result as any }),
          ...(updates.finishedAt && { finishedAt: updates.finishedAt }),
          ...(updates.metrics !== undefined && { metrics: updates.metrics as any }),
          ...(updates.parameters !== undefined && { parameters: updates.parameters as any }),
          ...(updates.executionTime !== undefined && { executionTime: updates.executionTime }),
          ...(updates.startedAt && { startedAt: updates.startedAt }),
          updatedAt: new Date()
        }
      });
      return updatedTask;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Record to update not found')) {
        logger.error(ERROR_MESSAGES.TASK_UPDATE_FAILED, { taskId, error: `${ERROR_MESSAGES.TASK_NOT_FOUND}: ${taskId}` });
        throw new Error(`${ERROR_MESSAGES.TASK_NOT_FOUND}: ${taskId}`);
      }
      throw error;
    }
  }

  /**
   * Создает посты для задачи
   */
  async createPosts(taskId: number, postsData: Partial<posts>[]): Promise<posts[]> {
    const createdPosts = await prisma.$transaction(
      postsData.map(postData =>
        prisma.posts.create({
          data: {
            vk_post_id: postData.vk_post_id!,
            owner_id: postData.owner_id!,
            group_id: postData.group_id!,
            text: postData.text || '',
            date: postData.date!,
            likes: postData.likes || DEFAULT_VALUES.LIKES_COUNT,
            task_id: taskId,
            createdAt: new Date(),
            updatedAt: new Date()
          }
        })
      )
    );
    return createdPosts;
  }

  /**
   * Создает комментарии для поста
   */
  async createComments(postId: number, commentsData: Partial<comments>[]): Promise<comments[]> {
    const createdComments = await prisma.$transaction(
      commentsData.map(commentData =>
        prisma.comments.create({
          data: {
            vk_comment_id: commentData.vk_comment_id!,
            post_vk_id: commentData.post_vk_id!,
            owner_id: commentData.owner_id!,
            author_id: commentData.author_id!,
            author_name: commentData.author_name!,
            text: commentData.text || '',
            date: commentData.date!,
            likes: commentData.likes || DEFAULT_VALUES.LIKES_COUNT,
            post_id: postId,
            createdAt: new Date(),
            updatedAt: new Date()
          }
        })
      )
    );
    return createdComments;
  }

  /**
   * Создает или обновляет посты (upsert)
   */
  async upsertPosts(taskId: number, postsData: Partial<posts>[]): Promise<posts[]> {
    try {
      const upsertedPosts = await prisma.$transaction(
        postsData.map(postData =>
          prisma.posts.upsert({
            where: { vk_post_id: postData.vk_post_id! },
            update: {
              text: postData.text || '',
              date: postData.date!,
              likes: postData.likes || DEFAULT_VALUES.LIKES_COUNT,
              owner_id: postData.owner_id!,
              group_id: postData.group_id!,
              updatedAt: new Date()
            },
            create: {
              vk_post_id: postData.vk_post_id!,
              owner_id: postData.owner_id!,
              group_id: postData.group_id!,
              text: postData.text || '',
              date: postData.date!,
              likes: postData.likes || DEFAULT_VALUES.LIKES_COUNT,
              task_id: taskId,
              createdAt: new Date(),
              updatedAt: new Date()
            }
          })
        )
      );
      return upsertedPosts;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to upsert posts', { taskId, error: errorMsg });
      throw new Error(`Failed to upsert posts: ${errorMsg}`);
    }
  }

  /**
   * Создает или обновляет комментарии (upsert)
   */
  async upsertComments(postVkId: number, commentsData: Partial<comments>[]): Promise<comments[]> {
    try {
      // Найти пост по vk_post_id для связи с комментариями
      const post = await prisma.posts.findUnique({
        where: { vk_post_id: postVkId }
      });
      if (!post) {
        throw new Error(`Post with vk_post_id ${postVkId} not found`);
      }

      const upsertedComments = await prisma.$transaction(
        commentsData.map(commentData =>
          prisma.comments.upsert({
            where: { vk_comment_id: commentData.vk_comment_id! },
            update: {
              text: commentData.text || '',
              date: commentData.date!,
              likes: commentData.likes || DEFAULT_VALUES.LIKES_COUNT,
              author_id: commentData.author_id!,
              author_name: commentData.author_name!,
              updatedAt: new Date()
            },
            create: {
              vk_comment_id: commentData.vk_comment_id!,
              post_vk_id: postVkId,
              owner_id: commentData.owner_id!,
              author_id: commentData.author_id!,
              author_name: commentData.author_name!,
              text: commentData.text || '',
              date: commentData.date!,
              likes: commentData.likes || DEFAULT_VALUES.LIKES_COUNT,
              post_id: post.id,
              createdAt: new Date(),
              updatedAt: new Date()
            }
          })
        )
      );
      return upsertedComments;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to upsert comments', { postVkId, error: errorMsg });
      throw new Error(`Failed to upsert comments: ${errorMsg}`);
    }
  }

  /**
   * Получает список задач с пагинацией и опциональными фильтрами
   */
  async listTasks({ limit, offset, status, type }: ListTasksOptions): Promise<ListTasksResult> {
    const where: any = {};
    if (status) {
      where.status = status;
    }
    if (type) {
      where.type = type;
    }

    const [tasks, total] = await prisma.$transaction([
      prisma.tasks.findMany({
        where,
        take: limit,
        skip: offset,
        orderBy: { createdAt: 'desc' }
      }),
      prisma.tasks.count({ where })
    ]);

    return { tasks, total };
  }

  /**
   * Получает результаты задачи с постами и комментариями
   */
  async getResults(taskId: number, groupId: number | null = null, postId: number | null = null): Promise<GetResultsResult> {
    const where: any = { task_id: taskId };

    if (postId) {
      where.id = postId;
    }
    if (groupId) {
      where.group_id = groupId;
    }

    const posts = await prisma.posts.findMany({
      where,
      include: {
        comments_comments_post_idToposts: true
      }
    });

    const totalComments = posts.reduce((sum, post) => {
      const commentsCount = post.comments_comments_post_idToposts?.length || 0;
      return sum + commentsCount;
    }, 0);

    return {
      posts: posts.map(post => ({
        ...post,
        comments: post.comments_comments_post_idToposts || []
      })),
      totalComments,
    };
  }

  /**
   * Получает статистику по задаче
   */
  async getTaskStatsByTaskId(taskId: number): Promise<{
    postsCount: number;
    commentsCount: number;
    avgLikesPerPost: number;
    avgCommentsPerPost: number;
  }> {
    const posts = await prisma.posts.findMany({
      where: { task_id: taskId },
      include: {
        comments_comments_post_idToposts: true
      }
    });

    const postsCount = posts.length;
    const totalLikes = posts.reduce((sum, post) => sum + post.likes, 0);
    const totalComments = posts.reduce((sum, post) => {
      const commentsCount = post.comments_comments_post_idToposts?.length || 0;
      return sum + commentsCount;
    }, 0);

    return {
      postsCount,
      commentsCount: totalComments,
      avgLikesPerPost: postsCount > 0 ? Math.round(totalLikes / postsCount * 100) / 100 : 0,
      avgCommentsPerPost: postsCount > 0 ? Math.round(totalComments / postsCount * 100) / 100 : 0
    };
  }

  /**
   * Удаляет данные задачи
   */
  async deleteTaskData(taskId: number): Promise<void> {
    try {
      await prisma.$transaction(async (tx) => {
        // Удаляем комментарии для всех постов задачи
        await tx.comments.deleteMany({
          where: {
            posts_comments_post_idToposts: {
              task_id: taskId
            }
          }
        });

        // Удаляем посты задачи
        await tx.posts.deleteMany({
          where: { task_id: taskId }
        });
      });

      logger.info('Task data deleted successfully', { taskId });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete task data', { taskId, error: errorMsg });
      throw new Error(`Failed to delete task data: ${errorMsg}`);
    }
  }

  /**
   * Получает последние задачи по типу
   */
  async getRecentTasks(limit: number, type: string): Promise<tasks[]> {
    try {
      return await prisma.tasks.findMany({
        where: { type: type as TaskType },
        take: limit,
        orderBy: { createdAt: 'desc' }
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get recent tasks', { limit, type, error: errorMsg });
      throw new Error(`Failed to get recent tasks: ${errorMsg}`);
    }
  }

  /**
   * Получает статистику задач по статусам
   */
  async getTaskStats(): Promise<Record<TaskStatus, number>> {
    try {
      const stats = await prisma.tasks.groupBy({
        by: ['status'],
        _count: {
          id: true
        }
      });

      const result: Record<TaskStatus, number> = {
        pending: 0,
        processing: 0,
        completed: 0,
        failed: 0
      };

      stats.forEach(stat => {
        result[stat.status] = stat._count.id;
      });

      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task stats', { error: errorMsg });
      throw new Error(`Failed to get task stats: ${errorMsg}`);
    }
  }

  /**
   * Получает группы с VK данными по ID задачи
   * @param taskId - ID задачи
   * @returns Массив групп с vk_id и name
   */
  async getGroupsWithVkDataByTaskId(taskId: number): Promise<Array<{
    id: number;
    vk_id: number;
    name: string;
    status?: string;
  }>> {
    try {
      return await prisma.groups.findMany({
        where: { task_id: taskId.toString() },
        select: {
          id: true,
          vk_id: true,
          name: true,
          status: true
        }
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get groups with VK data by task ID', { taskId, error: errorMsg });
      throw new Error(`Failed to get groups: ${errorMsg}`);
    }
  }

}

// Экспорт класса и экземпляра репозитория
export { DBRepo };
export default new DBRepo();

// Экспорт типов для совместимости
export type {
  ListTasksOptions,
  ListTasksResult,
  GetResultsResult,
  TaskUpdateData,
  CreateTaskData
};