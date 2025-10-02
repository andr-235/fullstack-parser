/**
 * @fileoverview ProcessGroupsWorker - worker для обработки групп
 *
 * BullMQ Worker для асинхронной обработки задач загрузки групп.
 */

import { Worker, Job } from 'bullmq';
import Redis from 'ioredis';
import { ProcessGroupsProcessor, ProcessGroupsJobData, ProcessGroupsJobResult } from '../processors/ProcessGroupsProcessor';
import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { IVkApiRepository } from '@domain/repositories/IVkApiRepository';
import { ITaskStorageRepository } from '@domain/repositories/ITaskStorageRepository';
import { QUEUE_NAMES, WORKER_CONFIGS } from '@infrastructure/config/queue';
import logger from '@infrastructure/utils/logger';

/**
 * Worker для обработки задач загрузки групп
 *
 * @description
 * Запускает ProcessGroupsProcessor для асинхронной обработки.
 * Обрабатывает события: completed, failed, progress.
 */
export class ProcessGroupsWorker {
  private worker: Worker<ProcessGroupsJobData, ProcessGroupsJobResult> | null = null;
  private processor: ProcessGroupsProcessor;

  constructor(
    private readonly redis: Redis,
    groupsRepository: IGroupsRepository,
    vkApiRepository: IVkApiRepository,
    taskStorageRepository: ITaskStorageRepository
  ) {
    this.processor = new ProcessGroupsProcessor(
      groupsRepository,
      vkApiRepository,
      taskStorageRepository
    );
  }

  /**
   * Запускает worker
   */
  async start(): Promise<void> {
    if (this.worker) {
      logger.warn('ProcessGroupsWorker already started');
      return;
    }

    const config = WORKER_CONFIGS[QUEUE_NAMES.PROCESS_GROUPS];

    this.worker = new Worker<ProcessGroupsJobData, ProcessGroupsJobResult>(
      QUEUE_NAMES.PROCESS_GROUPS,
      async (job: Job<ProcessGroupsJobData>) => {
        return this.processor.process(job);
      },
      {
        connection: this.redis,
        concurrency: config.concurrency,
        limiter: config.limiter
      }
    );

    // События worker'а
    this.worker.on('completed', (job: Job<ProcessGroupsJobData, ProcessGroupsJobResult>) => {
      logger.info('Job completed', {
        jobId: job.id,
        queueName: QUEUE_NAMES.PROCESS_GROUPS,
        result: job.returnvalue
      });
    });

    this.worker.on('failed', (job: Job<ProcessGroupsJobData> | undefined, error: Error) => {
      logger.error('Job failed', {
        jobId: job?.id,
        queueName: QUEUE_NAMES.PROCESS_GROUPS,
        error: error.message,
        stack: error.stack
      });
    });

    this.worker.on('progress', (job: Job<ProcessGroupsJobData>, progress: number | object) => {
      logger.debug('Job progress', {
        jobId: job.id,
        queueName: QUEUE_NAMES.PROCESS_GROUPS,
        progress
      });
    });

    this.worker.on('error', (error: Error) => {
      logger.error('Worker error', {
        queueName: QUEUE_NAMES.PROCESS_GROUPS,
        error: error.message
      });
    });

    logger.info('ProcessGroupsWorker started', {
      queueName: QUEUE_NAMES.PROCESS_GROUPS,
      concurrency: config.concurrency
    });
  }

  /**
   * Останавливает worker
   */
  async stop(): Promise<void> {
    if (!this.worker) {
      logger.warn('ProcessGroupsWorker not running');
      return;
    }

    try {
      await this.worker.close();
      this.worker = null;
      logger.info('ProcessGroupsWorker stopped', {
        queueName: QUEUE_NAMES.PROCESS_GROUPS
      });
    } catch (error) {
      logger.error('Failed to stop ProcessGroupsWorker', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Проверяет, запущен ли worker
   */
  isRunning(): boolean {
    return this.worker !== null;
  }

  /**
   * Получает статус worker'а
   */
  getStatus(): {
    running: boolean;
    queueName: string;
    concurrency: number;
  } {
    const config = WORKER_CONFIGS[QUEUE_NAMES.PROCESS_GROUPS];

    return {
      running: this.isRunning(),
      queueName: QUEUE_NAMES.PROCESS_GROUPS,
      concurrency: config.concurrency
    };
  }
}
