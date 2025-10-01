import { Queue, Job, JobsOptions } from 'bullmq';
// import pRetry from 'p-retry'; // ESM module incompatible with CommonJS
import {
  AnyJobData,
  VkCollectJobData,
  ProcessGroupsJobData,
  QueueError
} from '@/types/queue';
import { QUEUE_CONFIGS, QUEUE_NAMES } from '@/config/queue';
import logger from '@/utils/logger';

/**
 * Handler для операций с jobs
 * Использует generic методы для устранения дублирования кода
 *
 * Ответственность:
 * - Добавление jobs в очереди
 * - Получение job по ID
 * - Удаление jobs
 * - Retry failed jobs
 */
export class QueueJobHandler {
  constructor(private readonly queues: Map<string, Queue>) {}

  /**
   * Generic метод для добавления jobs любого типа
   * Устраняет дублирование между addVkCollectJob и addProcessGroupsJob
   *
   * @param queueName - Имя очереди
   * @param jobName - Имя job'а
   * @param data - Данные job'а (без taskId)
   * @param taskId - ID связанной задачи
   * @param options - Дополнительные опции job'а
   * @returns Promise с созданным job'ом
   */
  private async addGenericJob<T extends AnyJobData>(
    queueName: string,
    jobName: string,
    data: Omit<T, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<T>> {
    const queue = this.getQueue(queueName);
    const jobData = { ...data, taskId } as T;

    // Объединяем дефолтные опции из конфига с переданными
    const defaultOpts = QUEUE_CONFIGS[queueName]?.defaultJobOptions || {};
    const jobOptions: JobsOptions = {
      ...defaultOpts,
      ...options,
      jobId: options?.jobId || `${jobName}-${taskId}`,
    };

    const job = await queue.add(jobName, jobData, jobOptions);

    logger.info('Job added to queue', {
      jobId: job.id,
      queueName,
      jobName,
      taskId,
    });

    return job as Job<T>;
  }

  /**
   * Добавляет VK collect job в очередь
   * Используется для сбора комментариев из групп VK
   *
   * @param data - Данные для сбора (группы, опции)
   * @param taskId - ID связанной задачи
   * @param options - Дополнительные опции (delay, priority, и т.д.)
   * @returns Promise с созданным job'ом
   */
  async addVkCollectJob(
    data: Omit<VkCollectJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<VkCollectJobData>> {
    try {
      return await this.addGenericJob<VkCollectJobData>(
        QUEUE_NAMES.VK_COLLECT,
        'vk-collect',
        data,
        taskId,
        {
          ...options,
          // Небольшая задержка для избежания rate-limit burst'ов
          delay: options?.delay ?? 2000,
        }
      );
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
   * Добавляет process groups job в очередь
   * Используется для обработки и валидации групп из файла
   *
   * @param data - Данные для обработки (идентификаторы групп, источник)
   * @param taskId - ID связанной задачи
   * @param options - Дополнительные опции
   * @returns Promise с созданным job'ом
   */
  async addProcessGroupsJob(
    data: Omit<ProcessGroupsJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<ProcessGroupsJobData>> {
    try {
      return await this.addGenericJob<ProcessGroupsJobData>(
        QUEUE_NAMES.PROCESS_GROUPS,
        'process-groups',
        data,
        taskId,
        options
      );
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
   * Получает job по ID из любой очереди
   * Ищет job во всех доступных очередях
   *
   * @param jobId - ID job'а
   * @returns Promise с job'ом или null если не найден
   */
  async getJob(jobId: string): Promise<Job | null> {
    try {
      for (const [queueName, queue] of this.queues) {
        const job = await queue.getJob(jobId);
        if (job) {
          logger.debug('Job found', { jobId, queueName });
          return job;
        }
      }

      logger.debug('Job not found', { jobId });
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
   * Ищет job во всех очередях и удаляет его
   *
   * @param jobId - ID job'а для удаления
   */
  async removeJob(jobId: string): Promise<void> {
    try {
      const job = await this.getJob(jobId);
      if (job) {
        await job.remove();
        logger.info('Job removed', { jobId });
      } else {
        logger.warn('Job not found for removal', { jobId });
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
   * Повторяет выполнение failed job'а
   * Полезно для ручного retry после исправления ошибки
   *
   * @param jobId - ID job'а для retry
   */
  async retryJob(jobId: string): Promise<void> {
    try {
      const job = await this.getJob(jobId);
      if (!job) {
        throw new QueueError('Job not found', 'JOB_NOT_FOUND', jobId);
      }

      await job.retry();
      logger.info('Job retried', { jobId });
    } catch (error) {
      logger.error('Failed to retry job', {
        jobId,
        error: (error as Error).message,
      });
      throw new QueueError(
        'Failed to retry job',
        'RETRY_JOB_FAILED',
        jobId,
        error as Error
      );
    }
  }

  /**
   * Получает очередь по имени
   * Внутренний helper метод с валидацией
   *
   * @param queueName - Имя очереди
   * @returns Queue instance
   * @throws QueueError если очередь не найдена
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
}
