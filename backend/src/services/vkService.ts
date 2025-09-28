import logger from '@/utils/logger';
import vkApi from '@/repositories/vkApi';
import dbRepo from '@/repositories/dbRepo';
import { VkPost, VkComment } from '@/types/vk';
// Временные типы для корректной работы
type Task = any;
type TaskStatus = "pending" | "processing" | "completed" | "failed";

interface CollectResult {
  totalPosts: number;
  totalComments: number;
  errors: string[];
  status: TaskStatus;
}

interface TaskMetrics {
  posts: number;
  comments: number;
  errors: string[];
}

interface CollectProgress {
  progress: number;
  processedGroups: number;
  totalGroups: number;
  currentGroupId?: number;
}

interface TaskCompletionResult {
  totalGroups: number;
  processedPosts: number;
  processedComments: number;
  completedAt: string;
}

// Используем правильные типы для репозиториев
interface VkApiRepository {
  getPosts(groupId: number): Promise<{ posts: VkPost[] }>;
  getComments(groupId: number, postId: number): Promise<{ comments: VkComment[] }>;
}

interface DatabaseRepository {
  getTaskById(taskId: number): Promise<Task | null>;
  updateTask(taskId: number, updates: any): Promise<Task>;
  upsertPosts(taskId: number, posts: any[]): Promise<any[]>;
  upsertComments(postId: number, comments: any[]): Promise<any[]>;
  getResults(taskId: number, groupId?: number, postId?: number): Promise<any>;
  getRecentTasks(limit: number, type: string): Promise<Task[]>;
}

class VKService {
  private vkApi: VkApiRepository;
  private dbRepo: DatabaseRepository;

  constructor(vkApiInstance?: VkApiRepository, dbRepoInstance?: DatabaseRepository) {
    // Временное решение - используем приведение типов для совместимости
    this.vkApi = (vkApiInstance || vkApi) as VkApiRepository;
    this.dbRepo = (dbRepoInstance || dbRepo) as DatabaseRepository;
  }

  async getResults(taskId: number, groupId?: number, postId?: number): Promise<any> {
    try {
      return await this.dbRepo.getResults(taskId, groupId, postId);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get results', { taskId, groupId, postId, error: errorMsg });
      throw new Error(`Failed to get results: ${errorMsg}`);
    }
  }

  async collectForTask(taskId: number, groups: (string | number)[]): Promise<CollectResult> {
    let totalPosts = 0;
    let totalComments = 0;
    const errors: string[] = [];
    let task: Task | null = null;

    try {
      // Получаем задачу и переводим в статус processing
      task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error(`Task with id ${taskId} not found`);
      }

      // Обновляем статус на processing через dbRepo
      await this.dbRepo.updateTask(taskId, {
        status: 'processing' as TaskStatus,
        startedAt: new Date()
      });

      // Convert groups to positive numbers if needed
      const normalizedGroups = groups.map(group => Math.abs(Number(group))).filter(Boolean);

      if (normalizedGroups.length === 0) {
        throw new Error('No valid groups provided');
      }

      logger.info('Starting VK collection', { taskId, groupsCount: normalizedGroups.length });

      for (let i = 0; i < normalizedGroups.length; i++) {
        const groupId = normalizedGroups[i];

        try {
          logger.info('Processing group', { groupId, taskId, progress: `${i + 1}/${normalizedGroups.length}` });

          // Get posts from VK API (already normalized)
          const result = await this.vkApi.getPosts(groupId);
          const posts: VkPost[] = result?.posts || [];
          logger.info('Posts received for processing', { groupId, taskId, count: posts.length });

          // Take only first 10 posts as required
          const postsToProcess = posts.slice(0, 10);
          let groupPosts = 0;
          let groupComments = 0;

          if (postsToProcess.length > 0) {
            // Upsert posts
            await this.dbRepo.upsertPosts(taskId, postsToProcess);
            groupPosts = postsToProcess.length;

            // Process comments for each post
            for (const post of postsToProcess) {
              try {
                const { comments }: { comments: VkComment[] } = await this.vkApi.getComments(groupId, post.id || 0);

                if (comments.length > 0) {
                  await this.dbRepo.upsertComments(post.id || 0, comments);
                  groupComments += comments.length;
                }
              } catch (commentError) {
                const errorMsg = commentError instanceof Error ? commentError.message : String(commentError);
                logger.error('Error getting comments for post', {
                  groupId,
                  postId: post.id,
                  error: errorMsg
                });
                errors.push(`Error getting comments for group ${groupId}, post ${post.id || 0}: ${errorMsg}`);
              }
            }
          }

          totalPosts += groupPosts;
          totalComments += groupComments;

          logger.info('Group processing completed', {
            groupId,
            taskId,
            groupPosts,
            groupComments
          });

          // Update progress and metrics periodically for UI tracking
          const progressPercent = Math.min(90, Math.round(((i + 1) / normalizedGroups.length) * 90));

          // Update metrics using metadata field
          const currentMetrics: TaskMetrics = {
            posts: totalPosts,
            comments: totalComments,
            errors: [...errors]
          };

          const updatedMetrics = {
            ...currentMetrics,
            processedGroups: i + 1,
            totalGroups: normalizedGroups.length,
            currentGroupId: groupId
          };

          // Обновляем задачу через dbRepo
          await this.dbRepo.updateTask(taskId, {
            progress: progressPercent,
            metrics: updatedMetrics
          });

        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          logger.error('Error processing group', { groupId, error: errorMsg });
          errors.push(`Error processing group ${groupId}: ${errorMsg}`);
        }
      }

      const finalMetrics: TaskMetrics = {
        posts: totalPosts,
        comments: totalComments,
        errors
      };

      // Determine final status and mark task as completed/failed
      if (errors.length > 0 && totalPosts === 0) {
        // Complete failure - no posts processed
        const errorMessage = errors.join('; ');
        await this.dbRepo.updateTask(taskId, {
          status: 'failed' as TaskStatus,
          error: errorMessage,
          finishedAt: new Date(),
          metrics: finalMetrics
        });

        return {
          totalPosts,
          totalComments,
          errors,
          status: 'failed' as TaskStatus
        };
      } else {
        // Success or partial success
        const result: TaskCompletionResult = {
          totalGroups: normalizedGroups.length,
          processedPosts: totalPosts,
          processedComments: totalComments,
          completedAt: new Date().toISOString()
        };

        // Final metadata update
        const finalMetadata = {
          ...finalMetrics,
          result
        };

        await this.dbRepo.updateTask(taskId, {
          status: 'completed' as TaskStatus,
          result: result,
          finishedAt: new Date(),
          progress: 100,
          metrics: finalMetadata
        });

        logger.info('Task completed successfully', {
          taskId,
          status: task.status,
          totalPosts,
          totalComments,
          errorsCount: errors.length
        });

        return {
          totalPosts,
          totalComments,
          errors,
          status: 'completed' as TaskStatus
        };
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('General error in collectForTask', { taskId, error: errorMsg });
      errors.push(`General error in collectForTask: ${errorMsg}`);

      if (task) {
        // Update error metadata
        const errorMetrics = {
          posts: totalPosts,
          comments: totalComments,
          errors
        };

        await this.dbRepo.updateTask(taskId, {
          status: 'failed' as TaskStatus,
          error: errorMsg,
          finishedAt: new Date(),
          metrics: errorMetrics
        });
      }

      throw new Error(errorMsg);
    }
  }

  /**
   * Получает прогресс выполнения задачи сбора данных VK
   */
  async getCollectProgress(taskId: number): Promise<CollectProgress | null> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        return null;
      }

      const metadata = (task.metrics as any) || {};

      return {
        progress: task.progress,
        processedGroups: metadata.processedGroups || 0,
        totalGroups: metadata.totalGroups || 0,
        currentGroupId: metadata.currentGroupId
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get collect progress', { taskId, error: errorMsg });
      return null;
    }
  }

  /**
   * Отменяет выполняющуюся задачу сбора данных
   */
  async cancelCollectTask(taskId: number): Promise<boolean> {
    try {
      const task = await this.dbRepo.getTaskById(taskId);
      if (!task) {
        throw new Error('Task not found');
      }

      if (task.status !== 'processing') {
        throw new Error('Task is not currently processing');
      }

      await this.dbRepo.updateTask(taskId, {
        status: 'failed' as TaskStatus,
        error: 'Task cancelled by user',
        finishedAt: new Date()
      });

      logger.info('Task cancelled', { taskId });
      return true;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to cancel task', { taskId, error: errorMsg });
      return false;
    }
  }

  /**
   * Получает статистику по последним задачам сбора VK данных
   */
  async getCollectStats(limit = 10): Promise<any[]> {
    try {
      const tasks = await this.dbRepo.getRecentTasks(limit, 'fetch_comments');

      return tasks.map(task => ({
        taskId: task.id,
        status: task.status,
        progress: task.progress,
        posts: (task.metrics as any)?.posts || 0,
        comments: (task.metrics as any)?.comments || 0,
        errors: (task.metrics as any)?.errors?.length || 0,
        startedAt: task.startedAt,
        finishedAt: task.finishedAt,
        executionTime: task.executionTime,
        createdAt: task.createdAt
      }));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get collect stats', { error: errorMsg });
      return [];
    }
  }
}

const vkService = new VKService();
export default vkService;
export { VKService };
export type {
  CollectResult,
  TaskMetrics,
  CollectProgress,
  TaskCompletionResult
};