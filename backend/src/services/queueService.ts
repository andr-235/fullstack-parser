import { Queue, Job, QueueEvents, JobsOptions, Worker } from 'bullmq';
import logger from '@/utils/logger';
import {
  IQueueService,
  VkCollectJobData,
  ProcessGroupsJobData,
  QueueError,
  AnyJobData,
} from '@/types/queue';
import {
  QUEUE_NAMES,
  QUEUE_CONFIGS,
  createQueueRedisConnection,
  createQueueEventsRedisConnection,
} from '@/config/queue';
import { vkCollectWorker } from '@/workers';

/**
 * Базовый интерфейс для worker'ов
 */
interface BaseWorker {
  start(): Promise<void>;
  stop(): Promise<void>;
  getStatus(): { isRunning: boolean; isPaused: boolean; concurrency: number; queueName: string };
  healthCheck?(): Promise<{
    status: 'healthy' | 'unhealthy';
    details: {
      isRunning: boolean;
      isPaused: boolean;
      concurrency: number;
      queueName: string;
      uptime?: number;
    };
    error?: string;
  }>;
}

/**
 * Сервис для управления BullMQ очередями
 */
export class QueueService implements IQueueService {
  private queues: Map<string, Queue> = new Map();
  private queueEvents: Map<string, QueueEvents> = new Map();
  private workers: Map<string, BaseWorker> = new Map();
  private isInitialized = false;

  /**
   * Инициализация всех очередей
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      logger.info('Initializing BullMQ queues...');

      // Создаем соединения
      const queueConnection = createQueueRedisConnection();
      const eventsConnection = createQueueEventsRedisConnection();

      // Инициализируем все очереди
      for (const [queueName, config] of Object.entries(QUEUE_CONFIGS)) {
        // Создаем очередь
        const queue = new Queue(queueName, {
          connection: queueConnection,
          defaultJobOptions: config.defaultJobOptions,
          // settings: config.settings, // Removed due to type mismatch
        });

        // Создаем события очереди
        const events = new QueueEvents(queueName, {
          connection: eventsConnection,
        });

        // Настраиваем обработчики событий
        this.setupQueueEventHandlers(queueName, events);

        this.queues.set(queueName, queue);
        this.queueEvents.set(queueName, events);

        logger.info(`Queue initialized: ${queueName}`, {
          concurrency: config.concurrency,
          defaultJobOptions: {
            attempts: config.defaultJobOptions.attempts,
            timeout: config.defaultJobOptions.timeout,
          },
        });
      }

      // Инициализируем workers
      await this.initializeWorkers();

      this.isInitialized = true;
      logger.info('All BullMQ queues and workers initialized successfully');

    } catch (error) {
      logger.error('Failed to initialize BullMQ queues', {
        error: (error as Error).message,
        stack: (error as Error).stack,
      });
      throw new QueueError(
        'Queue initialization failed',
        'INIT_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Инициализация workers для обработки задач
   */
  private async initializeWorkers(): Promise<void> {
    try {
      logger.info('Initializing BullMQ workers...');

      // Инициализируем VK Collect Worker
      await vkCollectWorker.start();
      this.workers.set(QUEUE_NAMES.VK_COLLECT, vkCollectWorker);

      logger.info('VkCollectWorker started', {
        queueName: QUEUE_NAMES.VK_COLLECT,
        status: vkCollectWorker.getStatus()
      });

      logger.info('All BullMQ workers initialized successfully', {
        workersCount: this.workers.size
      });

    } catch (error) {
      logger.error('Failed to initialize BullMQ workers', {
        error: (error as Error).message,
        stack: (error as Error).stack,
      });
      throw new QueueError(
        'Workers initialization failed',
        'WORKERS_INIT_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Настройка обработчиков событий для очереди
   */
  private setupQueueEventHandlers(queueName: string, events: QueueEvents): void {
    // Job добавлен в очередь
    events.on('waiting', ({ jobId }) => {
      logger.debug(`Job waiting: ${jobId}`, { queue: queueName });
    });

    // Job начал выполняться
    events.on('active', ({ jobId }) => {
      logger.info(`Job started: ${jobId}`, { queue: queueName });
    });

    // Job завершен успешно
    events.on('completed', ({ jobId, returnvalue }) => {
      logger.info(`Job completed: ${jobId}`, {
        queue: queueName,
        returnValue: returnvalue,
      });
    });

    // Job завершен с ошибкой
    events.on('failed', ({ jobId, failedReason }) => {
      logger.error(`Job failed: ${jobId}`, {
        queue: queueName,
        reason: failedReason,
      });
    });

    // Прогресс выполнения job'а
    events.on('progress', ({ jobId, data }) => {
      logger.debug(`Job progress: ${jobId}`, {
        queue: queueName,
        progress: data,
      });
    });

    // Job был удален
    events.on('removed', ({ jobId }) => {
      logger.debug(`Job removed: ${jobId}`, { queue: queueName });
    });

    // Job застрял (stalled)
    events.on('stalled', ({ jobId }) => {
      logger.warn(`Job stalled: ${jobId}`, { queue: queueName });
    });
  }

  /**
   * Получает очередь по имени
   */
  private getQueue(queueName: string): Queue {
    const queue = this.queues.get(queueName);
    if (!queue) {
      throw new QueueError(
        `Queue not found: ${queueName}`,
        'QUEUE_NOT_FOUND'
      );
    }
    return queue;
  }

  /**
   * Добавляет VK collect job в очередь
   */
  async addVkCollectJob(
    data: Omit<VkCollectJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<VkCollectJobData>> {
    try {
      const queue = this.getQueue(QUEUE_NAMES.VK_COLLECT);
      const jobData: VkCollectJobData = { ...data, taskId };

      const defaultOpts = QUEUE_CONFIGS[QUEUE_NAMES.VK_COLLECT].defaultJobOptions || {};
      const jobOptions: JobsOptions = {
        ...defaultOpts,
        ...options,
        jobId: `vk-collect-${taskId}`,
        // ensure a small delay to avoid immediate rate-limit bursts if not overridden
        delay: options?.delay ?? 2000,
      };

      const job = await queue.add('vk-collect', jobData, jobOptions);

      logger.info(`VK collect job added`, {
        jobId: job.id,
        taskId,
        groupsCount: jobData.metadata.groups.length,
      });

      return job;

    } catch (error) {
      logger.error('Failed to add VK collect job', {
        taskId,
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to add VK collect job',
        'ADD_JOB_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Добавляет job для обработки групп
   */
  async addProcessGroupsJob(
    data: Omit<ProcessGroupsJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<ProcessGroupsJobData>> {
    try {
      const queue = this.getQueue(QUEUE_NAMES.PROCESS_GROUPS);
      const jobData: ProcessGroupsJobData = { ...data, taskId };

      const defaultOpts = QUEUE_CONFIGS[QUEUE_NAMES.PROCESS_GROUPS].defaultJobOptions || {};
      const jobOptions: JobsOptions = {
        ...defaultOpts,
        ...options,
        jobId: `process-groups-${taskId}`,
      };

      const job = await queue.add('process-groups', jobData, jobOptions);

      logger.info(`Process groups job added`, {
        jobId: job.id,
        taskId,
        groupIdentifiers: jobData.metadata.groupIdentifiers.length,
        source: jobData.metadata.source,
      });

      return job;

    } catch (error) {
      logger.error('Failed to add process groups job', {
        taskId,
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to add process groups job',
        'ADD_JOB_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Получает статистику по всем очередям
   */
  async getJobCounts(): Promise<{ waiting: number; active: number; completed: number; failed: number }> {
    try {
      let totalWaiting = 0;
      let totalActive = 0;
      let totalCompleted = 0;
      let totalFailed = 0;

      for (const [queueName, queue] of this.queues) {
        const waiting = await queue.getWaiting();
        const active = await queue.getActive();
        const completed = await queue.getCompleted();
        const failed = await queue.getFailed();

        totalWaiting += waiting.length;
        totalActive += active.length;
        totalCompleted += completed.length;
        totalFailed += failed.length;

        logger.debug(`Queue stats: ${queueName}`, {
          waiting: waiting.length,
          active: active.length,
          completed: completed.length,
          failed: failed.length,
        });
      }

      return {
        waiting: totalWaiting,
        active: totalActive,
        completed: totalCompleted,
        failed: totalFailed,
      };

    } catch (error) {
      logger.error('Failed to get job counts', {
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to get job counts',
        'GET_COUNTS_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Получает job по ID из любой очереди
   */
  async getJob(jobId: string): Promise<Job | null> {
    try {
      for (const [queueName, queue] of this.queues) {
        const job = await queue.getJob(jobId);
        if (job) {
          logger.debug(`Job found in queue: ${queueName}`, { jobId });
          return job;
        }
      }

      logger.debug(`Job not found: ${jobId}`);
      return null;

    } catch (error) {
      logger.error('Failed to get job', {
        jobId,
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to get job',
        'GET_JOB_FAILED',
        jobId,
        error as Error
      );
    }
  }

  /**
   * Удаляет job по ID
   */
  async removeJob(jobId: string): Promise<void> {
    try {
      const job = await this.getJob(jobId);
      if (job) {
        await job.remove();
        logger.info(`Job removed: ${jobId}`);
      } else {
        logger.warn(`Job not found for removal: ${jobId}`);
      }

    } catch (error) {
      logger.error('Failed to remove job', {
        jobId,
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to remove job',
        'REMOVE_JOB_FAILED',
        jobId,
        error as Error
      );
    }
  }

  /**
   * Останавливает все очереди
   */
  async pauseQueue(): Promise<void> {
    try {
      for (const [queueName, queue] of this.queues) {
        await queue.pause();
        logger.info(`Queue paused: ${queueName}`);
      }

    } catch (error) {
      logger.error('Failed to pause queues', {
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to pause queues',
        'PAUSE_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Возобновляет работу всех очередей
   */
  async resumeQueue(): Promise<void> {
    try {
      for (const [queueName, queue] of this.queues) {
        await queue.resume();
        logger.info(`Queue resumed: ${queueName}`);
      }

    } catch (error) {
      logger.error('Failed to resume queues', {
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to resume queues',
        'RESUME_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Получает QueueEvents для мониторинга
   */
  getQueueEvents(): QueueEvents {
    const events = this.queueEvents.get(QUEUE_NAMES.VK_COLLECT);
    if (!events) {
      throw new QueueError(
        'Queue events not available',
        'EVENTS_NOT_FOUND'
      );
    }
    return events;
  }

  /**
   * Очистка ресурсов
   */
  async cleanup(): Promise<void> {
    try {
      logger.info('Cleaning up BullMQ queues and workers...');

      // Останавливаем все workers
      for (const [workerName, worker] of this.workers) {
        try {
          await worker.stop();
          logger.debug(`Worker stopped: ${workerName}`);
        } catch (error) {
          logger.warn(`Failed to stop worker ${workerName}`, {
            error: (error as Error).message
          });
        }
      }

      // Закрываем все QueueEvents
      for (const [queueName, events] of this.queueEvents) {
        await events.close();
        logger.debug(`Queue events closed: ${queueName}`);
      }

      // Закрываем все очереди
      for (const [queueName, queue] of this.queues) {
        await queue.close();
        logger.debug(`Queue closed: ${queueName}`);
      }

      this.workers.clear();
      this.queues.clear();
      this.queueEvents.clear();
      this.isInitialized = false;

      logger.info('BullMQ queues and workers cleanup completed');

    } catch (error) {
      logger.error('Failed to cleanup BullMQ queues', {
        error: (error as Error).message,
      });
      throw new QueueError(
        'Cleanup failed',
        'CLEANUP_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Проверка состояния сервиса
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    details: {
      initialized: boolean;
      queuesCount: number;
      workersCount: number;
      workers: Array<{
        name: string;
        status: 'healthy' | 'unhealthy';
        isRunning: boolean;
        isPaused: boolean;
        processing: number;
      }>;
      totalJobs: {
        waiting: number;
        active: number;
        completed: number;
        failed: number;
      };
    };
  }> {
    try {
      const jobCounts = this.isInitialized ? await this.getJobCounts() : {
        waiting: 0,
        active: 0,
        completed: 0,
        failed: 0,
      };

      // Проверяем состояние workers
      const workersHealth = [];
      for (const [workerName, worker] of this.workers) {
        try {
          // Проверяем наличие метода healthCheck перед вызовом
          const workerHealthCheck = worker.healthCheck ? await worker.healthCheck() : null;
          if (workerHealthCheck) {
            workersHealth.push({
              name: workerName,
              status: workerHealthCheck.status,
              isRunning: workerHealthCheck.details.isRunning,
              isPaused: workerHealthCheck.details.isPaused,
              concurrency: workerHealthCheck.details.concurrency
            });
          }
        } catch (error) {
          workersHealth.push({
            name: workerName,
            status: 'unhealthy' as const,
            isRunning: false,
            isPaused: false,
            concurrency: 0
          });
        }
      }

      const allWorkersHealthy = workersHealth.every(w => w.status === 'healthy');
      const overallStatus = this.isInitialized && allWorkersHealthy ? 'healthy' : 'unhealthy';

      return {
        status: overallStatus,
        details: {
          initialized: this.isInitialized,
          queuesCount: this.queues.size,
          workersCount: this.workers.size,
          workers: workersHealth,
          totalJobs: jobCounts,
        },
      };

    } catch (error) {
      logger.error('Queue service health check failed', {
        error: (error as Error).message,
      });

      return {
        status: 'unhealthy',
        details: {
          initialized: false,
          queuesCount: 0,
          workersCount: 0,
          workers: [],
          totalJobs: { waiting: 0, active: 0, completed: 0, failed: 0 },
        },
      };
    }
  }
}

// Singleton instance
export const queueService = new QueueService();