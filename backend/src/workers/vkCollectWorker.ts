/**
 * @fileoverview VkCollectWorker - Worker для сбора комментариев из групп VK
 *
 * Основные возможности:
 * - Получение групп из БД по ID задачи
 * - Сбор последних 10 постов из каждой группы через VK-IO
 * - Сбор всех комментариев с постов
 * - Сохранение постов и комментариев в БД
 * - Детальный progress tracking
 * - Graceful error handling
 */

import { Worker, Job } from 'bullmq';
import {
  VkCollectJobData,
  VkCollectJobResult,
  VkCollectJobProgress,
  WorkerError,
  TypedWorker,
  WorkerConfig
} from '@/types/queue';
import { QUEUE_NAMES, WORKER_CONFIGS, createWorkerRedisConnection } from '@/config/queue';
import taskService from '@/services/taskService';
import vkIoService, { ProcessedPost, ProcessedComment } from '@/services/vkIoService';
import dbRepo from '@/repositories/dbRepo';
import groupsRepo from '@/repositories/groupsRepo';
import logger from '@/utils/logger';

/**
 * VkCollectWorker - класс для обработки задач сбора комментариев из VK групп
 *
 * Workflow:
 * 1. Получает группы из metadata job'а
 * 2. Для каждой группы получает последние 10 постов через vkIoService.getPosts()
 * 3. Сохраняет посты в БД
 * 4. Для каждого поста получает все комментарии через vkIoService.getComments()
 * 5. Сохраняет комментарии в БД
 * 6. Обновляет progress и статистику
 */
export class VkCollectWorker {
  private worker: TypedWorker<VkCollectJobData, VkCollectJobResult>;
  private isRunning = false;

  constructor(config?: Partial<WorkerConfig>) {
    const workerConfig = {
      ...WORKER_CONFIGS[QUEUE_NAMES.VK_COLLECT],
      ...config
    };

    // Создаем типизированный worker
    this.worker = new Worker<VkCollectJobData, VkCollectJobResult>(
      QUEUE_NAMES.VK_COLLECT,
      this.processJob.bind(this),
      {
        connection: createWorkerRedisConnection(),
        concurrency: workerConfig.concurrency,
        stalledInterval: workerConfig.stalledInterval,
        maxStalledCount: workerConfig.maxStalledCount,
        limiter: workerConfig.limiter,
        settings: workerConfig.settings
      }
    );

    this.setupEventHandlers();
  }

  /**
   * Главный метод обработки задачи сбора комментариев
   */
  private async processJob(job: Job<VkCollectJobData>): Promise<VkCollectJobResult> {
    const startTime = performance.now();
    const { taskId, metadata } = job.data;
    const { groups, options } = metadata;

    logger.info('VK collect job started', {
      jobId: job.id,
      taskId,
      groupsCount: groups.length,
      options
    });

    try {
      // Проверяем существование задачи
      const task = await taskService.getTaskById(taskId);
      if (!task) {
        throw new WorkerError(
          `Task ${taskId} not found`,
          'TASK_NOT_FOUND',
          job.id?.toString()
        );
      }

      // Валидация
      if (!groups || groups.length === 0) {
        throw new WorkerError(
          `No groups provided for task ${taskId}`,
          'NO_GROUPS_PROVIDED',
          job.id?.toString()
        );
      }

      // Обновляем статус задачи на processing
      await taskService.updateTaskStatus(taskId, 'processing', new Date());

      // Инициализация статистики
      let totalPosts = 0;
      let totalComments = 0;
      const errors: Array<{ groupId: string; error: string; timestamp: Date }> = [];

      // Инициализируем progress
      await this.updateJobProgress(job, {
        percentage: 0,
        stage: 'starting',
        stats: {
          groupsCompleted: 0,
          totalGroups: groups.length,
          postsProcessed: 0,
          commentsCollected: 0
        }
      });

      logger.info('Processing groups from job metadata', {
        jobId: job.id,
        taskId,
        groupsCount: groups.length
      });

      // Обрабатываем каждую группу
      for (let i = 0; i < groups.length; i++) {
        const group = groups[i];
        const groupId = parseInt(group.vkId);

        try {
          logger.info('Processing VK group', {
            jobId: job.id,
            taskId,
            groupId,
            groupName: group.name,
            progress: `${i + 1}/${groups.length}`
          });

          // Обновляем progress с текущей группой
          await this.updateJobProgress(job, {
            percentage: Math.round((i / groups.length) * 90),
            stage: 'fetching_posts',
            currentGroup: {
              vkId: group.vkId,
              name: group.name,
              progress: 0
            },
            stats: {
              groupsCompleted: i,
              totalGroups: groups.length,
              postsProcessed: totalPosts,
              commentsCollected: totalComments
            }
          });

          // Обрабатываем группу
          const groupResult = await this.processGroup(
            taskId,
            groupId,
            group.name,
            options,
            job
          );

          totalPosts += groupResult.posts;
          totalComments += groupResult.comments;

          // Обновляем progress после обработки группы
          await this.updateJobProgress(job, {
            percentage: Math.round(((i + 1) / groups.length) * 90),
            stage: 'fetching_comments',
            currentGroup: {
              vkId: group.vkId,
              name: group.name,
              progress: 100
            },
            stats: {
              groupsCompleted: i + 1,
              totalGroups: groups.length,
              postsProcessed: totalPosts,
              commentsCollected: totalComments
            }
          });

          logger.info('VK group processed successfully', {
            jobId: job.id,
            taskId,
            groupId,
            posts: groupResult.posts,
            comments: groupResult.comments
          });

        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          logger.error('Error processing VK group', {
            jobId: job.id,
            taskId,
            groupId,
            groupName: group.name,
            error: errorMsg
          });

          errors.push({
            groupId: group.vkId,
            error: errorMsg,
            timestamp: new Date()
          });

          // Продолжаем обработку других групп при ошибке
        }
      }

      // Финальное сохранение
      await this.updateJobProgress(job, {
        percentage: 95,
        stage: 'saving_data',
        stats: {
          groupsCompleted: groups.length,
          totalGroups: groups.length,
          postsProcessed: totalPosts,
          commentsCollected: totalComments
        }
      });

      // Определяем финальный статус
      const finalStatus = errors.length > 0 && totalPosts === 0 ? 'failed' : 'completed';

      // Обновляем задачу в БД
      if (finalStatus === 'completed') {
        await taskService.completeTask(taskId, {
          totalGroups: groups.length,
          processedPosts: totalPosts,
          processedComments: totalComments,
          errors: errors,
          completedAt: new Date().toISOString()
        });
      } else {
        await taskService.failTask(taskId, `Processing failed: ${errors.map(e => e.error).join('; ')}`);
      }

      // Финальный progress
      await this.updateJobProgress(job, {
        percentage: 100,
        stage: 'completing',
        stats: {
          groupsCompleted: groups.length,
          totalGroups: groups.length,
          postsProcessed: totalPosts,
          commentsCollected: totalComments
        }
      });

      const processingTime = performance.now() - startTime;

      logger.info('VK collect job completed', {
        jobId: job.id,
        taskId,
        finalStatus,
        totalPosts,
        totalComments,
        errorsCount: errors.length,
        processingTime: `${Math.round(processingTime)}ms`
      });

      return {
        success: finalStatus === 'completed',
        taskId,
        commentsCollected: totalComments,
        postsProcessed: totalPosts,
        groupsProcessed: groups.length,
        errors,
        processingTime,
        finalStatus
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      const processingTime = performance.now() - startTime;

      logger.error('VK collect job failed', {
        jobId: job.id,
        taskId,
        error: errorMsg,
        processingTime: `${Math.round(processingTime)}ms`
      });

      // Помечаем задачу как неудачную
      await taskService.failTask(taskId, errorMsg);

      throw new WorkerError(
        `VK collect job failed: ${errorMsg}`,
        'JOB_PROCESSING_FAILED',
        job.id?.toString(),
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Обрабатывает отдельную VK группу
   * Получает посты и комментарии, сохраняет в БД
   */
  private async processGroup(
    taskId: number,
    groupId: number,
    groupName: string,
    options: VkCollectJobData['metadata']['options'],
    job: Job<VkCollectJobData>
  ): Promise<{ posts: number; comments: number }> {
    try {
      const numericGroupId = Math.abs(groupId);

      if (!numericGroupId || isNaN(numericGroupId)) {
        throw new Error(`Invalid group ID: ${groupId}`);
      }

      // Получаем посты группы через vk-io
      logger.info('Fetching posts for group', { groupId: numericGroupId, taskId });
      const postsResult = await vkIoService.getPosts(numericGroupId);
      const posts = postsResult?.posts || [];

      if (posts.length === 0) {
        logger.warn('No posts found for group', { groupId, taskId });
        return { posts: 0, comments: 0 };
      }

      // Берем только первые 10 постов (или limit из options)
      const postsToProcess: ProcessedPost[] = posts.slice(0, options.limit || 10);

      logger.info('Saving posts to database', {
        groupId: numericGroupId,
        taskId,
        postsCount: postsToProcess.length
      });

      // Сохраняем посты в базу
      await dbRepo.upsertPosts(taskId, postsToProcess);

      let totalComments = 0;

      // Обрабатываем комментарии для каждого поста
      for (const post of postsToProcess) {
        try {
          logger.info('Fetching comments for post', {
            groupId: numericGroupId,
            postId: post.vk_post_id,
            taskId
          });

          const commentsResult = await vkIoService.getComments(numericGroupId, post.vk_post_id);
          const comments = commentsResult?.comments || [];

          if (comments.length > 0) {
            logger.info('Saving comments to database', {
              groupId: numericGroupId,
              postId: post.vk_post_id,
              taskId,
              commentsCount: comments.length
            });

            await dbRepo.upsertComments(post.vk_post_id, comments);
            totalComments += comments.length;
          }

        } catch (commentError) {
          const errorMsg = commentError instanceof Error ? commentError.message : String(commentError);
          logger.warn('Error getting comments for post', {
            taskId,
            groupId,
            postId: post.vk_post_id,
            error: errorMsg
          });
          // Продолжаем обработку других постов
        }
      }

      return {
        posts: postsToProcess.length,
        comments: totalComments
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Error in processGroup', {
        taskId,
        groupId,
        error: errorMsg
      });
      throw error;
    }
  }

  /**
   * Обновляет прогресс выполнения job'а
   */
  private async updateJobProgress(
    job: Job<VkCollectJobData>,
    progress: Partial<VkCollectJobProgress>
  ): Promise<void> {
    try {
      await job.updateProgress(progress);

      // Обновляем также progress задачи в базе
      if (typeof progress.percentage === 'number') {
        await taskService.updateTaskProgress(
          job.data.taskId,
          progress.percentage,
          {
            stage: progress.stage,
            currentGroup: progress.currentGroup,
            stats: progress.stats
          }
        );
      }
    } catch (error) {
      logger.warn('Failed to update job progress', {
        jobId: job.id,
        taskId: job.data.taskId,
        error: error instanceof Error ? error.message : String(error)
      });
      // Не прерываем выполнение из-за ошибки обновления progress
    }
  }

  /**
   * Настраивает обработчики событий worker'а
   */
  private setupEventHandlers(): void {
    this.worker.on('ready', () => {
      this.isRunning = true;
      logger.info('VkCollectWorker ready', {
        queueName: QUEUE_NAMES.VK_COLLECT,
        concurrency: this.worker.opts.concurrency
      });
    });

    this.worker.on('completed', (job: Job<VkCollectJobData>, result: VkCollectJobResult) => {
      logger.info('VK collect job completed', {
        jobId: job.id,
        taskId: job.data.taskId,
        commentsCollected: result.commentsCollected,
        postsProcessed: result.postsProcessed,
        success: result.success
      });
    });

    this.worker.on('failed', (job: Job<VkCollectJobData> | undefined, error: Error) => {
      logger.error('VK collect job failed', {
        jobId: job?.id,
        taskId: job?.data.taskId,
        error: error.message,
        stack: error.stack
      });
    });

    this.worker.on('progress', (job: Job<VkCollectJobData>, progress: VkCollectJobProgress) => {
      logger.debug('VK collect job progress', {
        jobId: job.id,
        taskId: job.data.taskId,
        percentage: progress.percentage,
        stage: progress.stage,
        currentGroup: progress.currentGroup?.vkId
      });
    });

    this.worker.on('error', (error: Error) => {
      logger.error('VkCollectWorker error', {
        error: error.message,
        stack: error.stack
      });
    });

    this.worker.on('stalled', (jobId: string) => {
      logger.warn('VK collect job stalled', { jobId });
    });

    this.worker.on('drained', () => {
      logger.debug('VkCollectWorker queue drained');
    });
  }

  /**
   * Запускает worker
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('VkCollectWorker already running');
      return;
    }

    try {
      logger.info('Starting VkCollectWorker', {
        queueName: QUEUE_NAMES.VK_COLLECT
      });
      // Worker автоматически стартует при создании
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to start VkCollectWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to start VkCollectWorker: ${errorMsg}`,
        'WORKER_START_FAILED',
        undefined,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Останавливает worker
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      logger.warn('VkCollectWorker already stopped');
      return;
    }

    try {
      await this.worker.close();
      this.isRunning = false;
      logger.info('VkCollectWorker stopped');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to stop VkCollectWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to stop VkCollectWorker: ${errorMsg}`,
        'WORKER_STOP_FAILED',
        undefined,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Возвращает статус worker'а
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      isPaused: this.worker.isPaused(),
      concurrency: this.worker.opts.concurrency || 1,
      queueName: QUEUE_NAMES.VK_COLLECT
    };
  }

  /**
   * Возвращает экземпляр worker'а
   */
  getWorkerInstance(): TypedWorker<VkCollectJobData, VkCollectJobResult> {
    return this.worker;
  }
}

// Экспортируем singleton экземпляр
const vkCollectWorker = new VkCollectWorker();
export default vkCollectWorker;
