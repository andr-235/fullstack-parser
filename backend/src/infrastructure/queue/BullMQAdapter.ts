/**
 * @fileoverview BullMQ Adapter - реализация IQueueRepository
 *
 * Адаптер для работы с BullMQ очередями, реализующий интерфейс из Domain Layer.
 * Предоставляет методы для управления задачами в очереди.
 */

import { Queue, Job, Worker } from 'bullmq';
import Redis from 'ioredis';
import {
  IQueueRepository,
  QueueJobOptions,
  JobStatus,
  QueueJob,
  QueueStats
} from '@domain/repositories/IQueueRepository';
import { QUEUE_CONFIGS } from '@infrastructure/config/queue';
import logger from '@infrastructure/utils/logger';

/**
 * BullMQ Adapter - реализация репозитория очередей
 *
 * @description
 * Управляет BullMQ очередями для асинхронной обработки задач.
 * Поддерживает множественные очереди и их конфигурации.
 */
export class BullMQAdapter implements IQueueRepository {
  private queues: Map<string, Queue> = new Map();
  private processors: Map<string, (job: QueueJob<any, any>) => Promise<any>> = new Map();

  constructor(
    private readonly redis: Redis
  ) {
    logger.info('BullMQAdapter initialized');
  }

  /**
   * Получает или создает очередь
   */
  private getOrCreateQueue(queueName: string): Queue {
    if (!this.queues.has(queueName)) {
      const config = QUEUE_CONFIGS[queueName] || QUEUE_CONFIGS['vk-collect'];

      const queue = new Queue(queueName, {
        connection: this.redis,
        defaultJobOptions: config.defaultJobOptions
      });

      this.queues.set(queueName, queue);
      logger.info(`Queue created: ${queueName}`);
    }

    return this.queues.get(queueName)!;
  }

  /**
   * Маппинг BullMQ статуса → Domain статус
   */
  private async mapJobStatus(job: Job): Promise<JobStatus> {
    const state = await job.getState();

    switch (state) {
      case 'waiting':
      case 'waiting-children':
        return 'waiting';
      case 'active':
        return 'active';
      case 'completed':
        return 'completed';
      case 'failed':
        return 'failed';
      case 'delayed':
      case 'prioritized':
        return 'delayed';
      case 'unknown':
        return 'waiting';
      default:
        return 'waiting';
    }
  }

  /**
   * Маппинг BullMQ Job → Domain QueueJob
   */
  private async mapToDomainJob<TData, TResult>(job: Job<TData, TResult>): Promise<QueueJob<TData, TResult>> {
    const status = await this.mapJobStatus(job);

    return {
      id: job.id!,
      name: job.name,
      data: job.data,
      status,
      progress: job.progress as number || 0,
      attemptsMade: job.attemptsMade,
      finishedOn: job.finishedOn ? new Date(job.finishedOn) : undefined,
      processedOn: job.processedOn ? new Date(job.processedOn) : undefined,
      failedReason: job.failedReason,
      returnvalue: job.returnvalue
    };
  }

  /**
   * Добавляет задачу в очередь
   */
  async addJob<TData>(
    queueName: string,
    jobName: string,
    data: TData,
    options?: QueueJobOptions
  ): Promise<string> {
    try {
      const queue = this.getOrCreateQueue(queueName);

      const job = await queue.add(jobName, data, {
        priority: options?.priority,
        delay: options?.delay,
        attempts: options?.attempts,
        backoff: options?.backoff,
        removeOnComplete: options?.removeOnComplete,
        removeOnFail: options?.removeOnFail
      });

      logger.info(`Job added to queue`, {
        queueName,
        jobName,
        jobId: job.id
      });

      return job.id!;
    } catch (error) {
      logger.error(`Failed to add job to queue`, {
        queueName,
        jobName,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Получает задачу по ID
   */
  async getJob<TData, TResult>(
    queueName: string,
    jobId: string
  ): Promise<QueueJob<TData, TResult> | null> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      const job = await queue.getJob(jobId);

      if (!job) {
        return null;
      }

      return this.mapToDomainJob<TData, TResult>(job);
    } catch (error) {
      logger.error(`Failed to get job`, {
        queueName,
        jobId,
        error: error instanceof Error ? error.message : String(error)
      });
      return null;
    }
  }

  /**
   * Получает статус задачи
   */
  async getJobStatus(queueName: string, jobId: string): Promise<JobStatus | null> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      const job = await queue.getJob(jobId);

      if (!job) {
        return null;
      }

      return this.mapJobStatus(job);
    } catch (error) {
      logger.error(`Failed to get job status`, {
        queueName,
        jobId,
        error: error instanceof Error ? error.message : String(error)
      });
      return null;
    }
  }

  /**
   * Удаляет задачу из очереди
   */
  async removeJob(queueName: string, jobId: string): Promise<boolean> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      const job = await queue.getJob(jobId);

      if (!job) {
        return false;
      }

      await job.remove();
      logger.info(`Job removed`, { queueName, jobId });
      return true;
    } catch (error) {
      logger.error(`Failed to remove job`, {
        queueName,
        jobId,
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Получает задачи по статусу
   */
  async getJobsByStatus<TData, TResult>(
    queueName: string,
    status: JobStatus,
    start: number = 0,
    end: number = 10
  ): Promise<readonly QueueJob<TData, TResult>[]> {
    try {
      const queue = this.getOrCreateQueue(queueName);

      // Маппинг Domain статуса → BullMQ статус
      const bullMQStatus = status === 'active' ? 'active' :
                          status === 'waiting' ? 'wait' :
                          status === 'completed' ? 'completed' :
                          status === 'failed' ? 'failed' :
                          status === 'delayed' ? 'delayed' :
                          'paused';

      const jobs = await queue.getJobs([bullMQStatus as any], start, end);

      return Promise.all(
        jobs.map(job => this.mapToDomainJob<TData, TResult>(job))
      );
    } catch (error) {
      logger.error(`Failed to get jobs by status`, {
        queueName,
        status,
        error: error instanceof Error ? error.message : String(error)
      });
      return [];
    }
  }

  /**
   * Получает статистику очереди
   */
  async getQueueStats(queueName: string): Promise<QueueStats> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      const counts = await queue.getJobCounts();

      return {
        waiting: counts.waiting || 0,
        active: counts.active || 0,
        completed: counts.completed || 0,
        failed: counts.failed || 0,
        delayed: counts.delayed || 0,
        paused: counts.paused || 0
      };
    } catch (error) {
      logger.error(`Failed to get queue stats`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });

      return {
        waiting: 0,
        active: 0,
        completed: 0,
        failed: 0,
        delayed: 0,
        paused: 0
      };
    }
  }

  /**
   * Очищает очередь от завершенных задач
   */
  async cleanQueue(queueName: string, grace: number = 0): Promise<number> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      const jobs = await queue.clean(grace, 100, 'completed');

      logger.info(`Queue cleaned`, { queueName, removed: jobs.length });
      return jobs.length;
    } catch (error) {
      logger.error(`Failed to clean queue`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });
      return 0;
    }
  }

  /**
   * Приостанавливает очередь
   */
  async pauseQueue(queueName: string): Promise<void> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      await queue.pause();
      logger.info(`Queue paused`, { queueName });
    } catch (error) {
      logger.error(`Failed to pause queue`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Возобновляет очередь
   */
  async resumeQueue(queueName: string): Promise<void> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      await queue.resume();
      logger.info(`Queue resumed`, { queueName });
    } catch (error) {
      logger.error(`Failed to resume queue`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Очищает все задачи в очереди
   */
  async obliterateQueue(queueName: string): Promise<number> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      await queue.obliterate();
      logger.warn(`Queue obliterated`, { queueName });
      return 0; // BullMQ не возвращает количество
    } catch (error) {
      logger.error(`Failed to obliterate queue`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });
      return 0;
    }
  }

  /**
   * Проверяет здоровье очереди
   */
  async isQueueHealthy(queueName: string): Promise<boolean> {
    try {
      const queue = this.getOrCreateQueue(queueName);
      await queue.getJobCounts(); // Простая проверка доступности
      return true;
    } catch (error) {
      logger.error(`Queue health check failed`, {
        queueName,
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Регистрирует обработчик задач
   *
   * Примечание: Этот метод сохраняет processor для использования в Worker
   */
  async registerProcessor<TData, TResult>(
    queueName: string,
    processor: (job: QueueJob<TData, any>) => Promise<TResult>
  ): Promise<void> {
    this.processors.set(queueName, processor);
    logger.info(`Processor registered for queue: ${queueName}`);
  }

  /**
   * Получает зарегистрированный processor
   */
  getProcessor<TData, TResult>(
    queueName: string
  ): ((job: QueueJob<TData, any>) => Promise<TResult>) | undefined {
    return this.processors.get(queueName);
  }

  /**
   * Закрывает все очереди
   */
  async closeAll(): Promise<void> {
    try {
      for (const [name, queue] of this.queues.entries()) {
        await queue.close();
        logger.info(`Queue closed: ${name}`);
      }
      this.queues.clear();
    } catch (error) {
      logger.error(`Failed to close queues`, {
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }
}
