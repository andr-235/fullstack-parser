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
import vkIoService, { ProcessedPost } from '@/services/vkIoService';
import dbRepo from '@/repositories/dbRepo';
import logger from '@/utils/logger';
import { TaskMetrics } from '@/types/task';

/**
 * VkCollectWorker - класс для обработки задач сбора комментариев из VK
 *
 * Особенности:
 * - Строгая типизация с TypeScript
 * - Использует новый vkIoService с библиотекой vk-io (решает проблему IP-блокировки)
 * - Интеграция с существующими сервисами
 * - Proper error handling и retry логика
 * - Progress tracking с детализированными метриками
 * - Автоматический rate limiting через vk-io
 * - Structured logging для мониторинга
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
        // retryProcessDelay: workerConfig.retryProcessDelay, // Не поддерживается в текущей версии BullMQ
        limiter: workerConfig.limiter,
        settings: workerConfig.settings
      }
    );

    this.setupEventHandlers();
  }

  /**
   * Основной метод обработки VK collect job'а
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

      // Обновляем статус задачи на processing
      await taskService.updateTaskStatus(taskId, 'processing', new Date());

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

      let totalPosts = 0;
      let totalComments = 0;
      const errors: Array<{ groupId: string; error: string; timestamp: Date }> = [];

      // Получаем реальные группы из базы данных с VK ID
      const dbGroups = await dbRepo.getGroupsWithVkDataByTaskId(String(taskId));

      if (dbGroups.length === 0) {
        throw new WorkerError(
          `No valid groups found for task ${taskId}`,
          'NO_GROUPS_FOUND',
          job.id?.toString()
        );
      }

      // Обрабатываем каждую группу из базы данных
      for (let i = 0; i < dbGroups.length; i++) {
        const group = dbGroups[i];
        const groupId = group.vk_id; // Используем VK ID из базы данных

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
            percentage: Math.round((i / dbGroups.length) * 90), // 90% на обработку групп
            stage: 'fetching_posts',
            currentGroup: {
              vkId: String(groupId),
              name: group.name || `Группа ${groupId}`,
              progress: 0
            },
            stats: {
              groupsCompleted: i,
              totalGroups: dbGroups.length,
              postsProcessed: totalPosts,
              commentsCollected: totalComments
            }
          });

          // Обрабатываем группу через существующий VK service
          const groupResult = await this.processGroup(
            taskId,
            String(groupId),
            group.name || `Группа ${groupId}`,
            options,
            job
          );

          totalPosts += groupResult.posts;
          totalComments += groupResult.comments;

          // Обновляем progress после обработки группы
          await this.updateJobProgress(job, {
            percentage: Math.round(((i + 1) / dbGroups.length) * 90),
            stage: 'fetching_comments',
            currentGroup: {
              vkId: String(groupId),
              name: group.name || `Группа ${groupId}`,
              progress: 100
            },
            stats: {
              groupsCompleted: i + 1,
              totalGroups: dbGroups.length,
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
            error: errorMsg
          });

          errors.push({
            groupId: String(groupId),
            error: errorMsg,
            timestamp: new Date()
          });

          // Продолжаем обработку других групп при ошибке
        }
      }

      // Финальное сохранение данных
      await this.updateJobProgress(job, {
        percentage: 95,
        stage: 'saving_data',
        stats: {
          groupsCompleted: dbGroups.length,
          totalGroups: dbGroups.length,
          postsProcessed: totalPosts,
          commentsCollected: totalComments
        }
      });

      // Обновляем финальные метрики задачи
      const finalMetrics = {
        posts: totalPosts,
        comments: totalComments,
        errors: errors.map(e => e.error)
      };

      // Определяем финальный статус
      const finalStatus = errors.length > 0 && totalPosts === 0 ? 'failed' : 'completed';

      if (finalStatus === 'completed') {
        await taskService.completeTask(taskId, {
          totalGroups: dbGroups.length,
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
          groupsCompleted: dbGroups.length,
          totalGroups: dbGroups.length,
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
        groupsProcessed: dbGroups.length,
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
   */
  private async processGroup(
    taskId: number,
    groupId: string,
    groupName: string,
    options: any,
    job: Job<VkCollectJobData>
  ): Promise<{ posts: number; comments: number }> {
    try {
      // Конвертируем groupId в число для VK API
      const numericGroupId = Math.abs(Number(groupId));

      if (!numericGroupId) {
        throw new Error(`Invalid group ID: ${groupId}`);
      }

      // Получаем посты группы через vk-io с обработкой таймаутов
      const postsResult = await this.executeWithTimeout(
        () => vkIoService.getPosts(numericGroupId),
        60000, // 1 минута на получение постов
        `Получение постов для группы ${groupId}`
      );
      const posts = postsResult?.posts || [];

      if (posts.length === 0) {
        logger.warn('No posts found for group', { groupId, taskId });
        return { posts: 0, comments: 0 };
      }

      // Берем только первые 10 постов согласно требованиям
      const postsToProcess: ProcessedPost[] = posts.slice(0, options.limit || 10);

      // Сохраняем посты в базу
      await dbRepo.upsertPosts(taskId, postsToProcess);

      let totalComments = 0;

      // Обрабатываем комментарии для каждого поста
      for (const post of postsToProcess) {
        try {
          const commentsResult = await this.executeWithTimeout(
            () => vkIoService.getComments(numericGroupId, post.vk_post_id),
            90000, // 1.5 минуты на получение комментариев
            `Получение комментариев для поста ${post.vk_post_id}`
          );
          const comments = commentsResult?.comments || [];

          if (comments.length > 0) {
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
   * Обновляет progress job'а с детализированной информацией
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
      // Worker автоматически стартует при создании
      logger.info('Starting VkCollectWorker', {
        queueName: QUEUE_NAMES.VK_COLLECT
      });
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
   * Ставит worker на паузу
   */
  async pause(): Promise<void> {
    try {
      await this.worker.pause();
      logger.info('VkCollectWorker paused');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to pause VkCollectWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to pause VkCollectWorker: ${errorMsg}`,
        'WORKER_PAUSE_FAILED',
        undefined,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Возобновляет работу worker'а
   */
  async resume(): Promise<void> {
    try {
      await this.worker.resume();
      logger.info('VkCollectWorker resumed');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to resume VkCollectWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to resume VkCollectWorker: ${errorMsg}`,
        'WORKER_RESUME_FAILED',
        undefined,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Возвращает статус worker'а
   */
  getWorkerStatus() {
    return {
      isRunning: this.isRunning,
      isPaused: this.worker.isPaused(),
      concurrency: this.worker.opts.concurrency || 1,
      // processing: this.worker.processing, // Не доступно в публичном API
      queueName: QUEUE_NAMES.VK_COLLECT
    };
  }

  /**
   * Возвращает экземпляр worker'а для прямого доступа
   */
  getWorkerInstance(): TypedWorker<VkCollectJobData, VkCollectJobResult> {
    return this.worker;
  }

  /**
   * Выполняет операцию с таймаутом для предотвращения зависания
   */
  private async executeWithTimeout<T>(
    operation: () => Promise<T>,
    timeoutMs: number,
    operationName: string
  ): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const timeout = setTimeout(() => {
        reject(new Error(`${operationName} превысило таймаут ${timeoutMs}мс`));
      }, timeoutMs);

      operation()
        .then((result) => {
          clearTimeout(timeout);
          resolve(result);
        })
        .catch((error) => {
          clearTimeout(timeout);
          reject(error);
        });
    });
  }

  /**
   * Проверяет здоровье worker'а
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    details: {
      isRunning: boolean;
      isPaused: boolean;
      concurrency: number;
      queueName: string;
      uptime?: number;
    };
    error?: string;
  }> {
    try {
      const status = this.getWorkerStatus();

      // Базовая проверка состояния worker'а
      const isHealthy = this.isRunning && !status.isPaused;

      return {
        status: isHealthy ? 'healthy' : 'unhealthy',
        details: {
          ...status,
          uptime: process.uptime()
        },
        ...(isHealthy ? {} : {
          error: this.isRunning ? 'Worker is paused' : 'Worker is not running'
        })
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('VkCollectWorker health check failed', { error: errorMsg });

      return {
        status: 'unhealthy',
        details: {
          isRunning: false,
          isPaused: false,
          concurrency: 0,
          queueName: QUEUE_NAMES.VK_COLLECT
        },
        error: errorMsg
      };
    }
  }
}

// Экспортируем singleton экземпляр
const vkCollectWorker = new VkCollectWorker();
export default vkCollectWorker;