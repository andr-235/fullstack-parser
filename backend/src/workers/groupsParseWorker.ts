/**
 * @fileoverview GroupsParseWorker - Worker для парсинга групп VK через VK-IO API
 *
 * Основные возможности:
 * - Обработка VK ID и screen_name через единый API VK-IO
 * - Батч-обработка для оптимизации запросов к VK API
 * - Детальный progress tracking с метриками
 * - Graceful error handling без прерывания обработки
 * - Интеграция с существующей инфраструктурой (vkIoService, groupsRepo, taskService)
 * - Проверка дубликатов перед сохранением
 * - Structured logging для мониторинга
 */

import { Worker, Job } from 'bullmq';
import {
  ProcessGroupsJobData,
  GroupsParseJobResult,
  GroupsParseJobProgress,
  WorkerError,
  TypedWorker,
  WorkerConfig
} from '@/types/queue';
import { QUEUE_NAMES, WORKER_CONFIGS, createWorkerRedisConnection } from '@/config/queue';
import taskService from '@/services/taskService';
import vkIoService, { ProcessedGroup } from '@/services/vkIoService';
import groupsRepo, { CreateGroupInput } from '@/repositories/groupsRepo';
import logger from '@/utils/logger';

/**
 * Конфигурация батч-обработки
 */
const BATCH_CONFIG = {
  VK_API_BATCH_SIZE: 100,    // Размер батча для VK API (groups.getById поддерживает до 500)
  DB_SAVE_BATCH_SIZE: 50,     // Размер батча для сохранения в БД
  BATCH_DELAY_MS: 400,        // Задержка между батчами VK API (безопасность)
  PROGRESS_UPDATE_INTERVAL: 10 // Обновлять прогресс каждые N групп
};

/**
 * GroupsParseWorker - класс для обработки задач парсинга групп VK
 *
 * Workflow:
 * 1. Получает массив идентификаторов (VK ID или screen_name) из job metadata
 * 2. Батч-обработка через vkIoService.getGroupsInfo() (VK-IO сам определяет тип)
 * 3. Проверка дубликатов через groupsRepo
 * 4. Сохранение валидных групп в БД батчами
 * 5. Финализация с детальной статистикой
 */
export class GroupsParseWorker {
  private worker: TypedWorker<ProcessGroupsJobData, GroupsParseJobResult>;
  private isRunning = false;

  constructor(config?: Partial<WorkerConfig>) {
    const workerConfig = {
      ...WORKER_CONFIGS[QUEUE_NAMES.PROCESS_GROUPS],
      ...config
    };

    // Создаем типизированный worker для обработки групп
    this.worker = new Worker<ProcessGroupsJobData, GroupsParseJobResult>(
      QUEUE_NAMES.PROCESS_GROUPS,
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
   * Главный метод обработки задачи парсинга групп
   *
   * @param job - BullMQ Job с данными о группах для парсинга
   * @returns Результат выполнения с детальной статистикой
   */
  private async processJob(job: Job<ProcessGroupsJobData>): Promise<GroupsParseJobResult> {
    const startTime = performance.now();
    const { taskId, metadata } = job.data;
    const { groupIdentifiers, source, originalFileName } = metadata;

    logger.info('Groups parse job started', {
      jobId: job.id,
      taskId,
      totalIdentifiers: groupIdentifiers.length,
      source,
      originalFileName
    });

    // Инициализация статистики
    const stats: GroupsParseJobResult['stats'] & { processed: number } = {
      total: groupIdentifiers.length,
      processed: 0,
      valid: 0,
      invalid: 0,
      duplicate: 0,
      saved: 0
    };

    const errors: Array<{ identifier: string; error: string; timestamp: Date }> = [];

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

      // Валидация входных данных
      if (!groupIdentifiers || groupIdentifiers.length === 0) {
        throw new WorkerError(
          `No group identifiers provided for task ${taskId}`,
          'NO_IDENTIFIERS',
          job.id?.toString()
        );
      }

      // Обновляем статус задачи на processing
      await taskService.updateTaskStatus(taskId, 'processing', new Date());

      // Stage 1: Инициализация
      await this.updateProgress(job, {
        percentage: 0,
        stage: 'init',
        stats
      });

      logger.info('Starting groups fetching', {
        jobId: job.id,
        taskId,
        totalIdentifiers: groupIdentifiers.length
      });

      // Stage 2: Получение информации о группах через VK-IO (батч-обработка)
      const validGroups = await this.fetchGroupsInfo(
        groupIdentifiers,
        job,
        stats,
        errors
      );

      logger.info('Groups fetching completed', {
        jobId: job.id,
        taskId,
        validGroups: validGroups.length,
        invalid: stats.invalid
      });

      // Stage 3: Сохранение групп в БД
      if (validGroups.length > 0) {
        await this.saveGroupsBatch(validGroups, taskId, job, stats);
      }

      // Stage 4: Финализация
      await this.updateProgress(job, {
        percentage: 100,
        stage: 'done',
        stats
      });

      // Определяем успешность выполнения
      const success = stats.saved > 0;
      const finalStatus = success ? 'completed' : 'failed';

      // Обновляем задачу в БД
      if (success) {
        await taskService.completeTask(taskId, {
          totalIdentifiers: stats.total,
          validGroups: stats.valid,
          invalidGroups: stats.invalid,
          duplicateGroups: stats.duplicate,
          savedGroups: stats.saved,
          errors: errors.map(e => e.error),
          completedAt: new Date().toISOString()
        });
      } else {
        await taskService.failTask(
          taskId,
          `No groups saved. Total errors: ${errors.length}`
        );
      }

      const processingTimeMs = performance.now() - startTime;

      logger.info('Groups parse job completed', {
        jobId: job.id,
        taskId,
        success,
        stats,
        errorsCount: errors.length,
        processingTimeMs: Math.round(processingTimeMs)
      });

      // Убираем processed из результата (не требуется в финальной статистике)
      const { processed, ...finalStats } = stats;

      return {
        success,
        taskId,
        stats: finalStats,
        errors,
        processingTimeMs
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      const processingTimeMs = performance.now() - startTime;

      logger.error('Groups parse job failed', {
        jobId: job.id,
        taskId,
        error: errorMsg,
        processingTimeMs: Math.round(processingTimeMs)
      });

      // Помечаем задачу как неудачную
      await taskService.failTask(taskId, errorMsg);

      throw new WorkerError(
        `Groups parse job failed: ${errorMsg}`,
        'JOB_PROCESSING_FAILED',
        job.id?.toString(),
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Получает информацию о группах через VK-IO API с батч-обработкой
   * VK-IO автоматически обрабатывает как VK ID, так и screen_name
   *
   * @param identifiers - Массив идентификаторов (VK ID или screen_name)
   * @param job - Job для обновления прогресса
   * @param stats - Статистика для обновления
   * @param errors - Массив для сбора ошибок
   * @returns Массив валидных групп с полной информацией
   */
  private async fetchGroupsInfo(
    identifiers: string[],
    job: Job<ProcessGroupsJobData>,
    stats: GroupsParseJobResult['stats'] & { processed: number },
    errors: GroupsParseJobResult['errors']
  ): Promise<ProcessedGroup[]> {
    const validGroups: ProcessedGroup[] = [];
    const totalBatches = Math.ceil(identifiers.length / BATCH_CONFIG.VK_API_BATCH_SIZE);

    logger.info('Starting batch processing', {
      totalIdentifiers: identifiers.length,
      batchSize: BATCH_CONFIG.VK_API_BATCH_SIZE,
      totalBatches
    });

    // Обрабатываем идентификаторы батчами
    for (let i = 0; i < identifiers.length; i += BATCH_CONFIG.VK_API_BATCH_SIZE) {
      const currentBatch = Math.floor(i / BATCH_CONFIG.VK_API_BATCH_SIZE) + 1;
      const batchIdentifiers = identifiers.slice(i, i + BATCH_CONFIG.VK_API_BATCH_SIZE);

      logger.info('Processing batch', {
        batch: currentBatch,
        totalBatches,
        batchSize: batchIdentifiers.length
      });

      try {
        // VK-IO автоматически обрабатывает VK ID и screen_name
        const groupsInfo = await vkIoService.getGroupsInfo(batchIdentifiers);

        // Обрабатываем результаты батча
        for (const group of groupsInfo) {
          // Проверяем дубликат в БД
          const isDuplicate = await groupsRepo.groupExistsByVkId(group.id);

          if (isDuplicate) {
            stats.duplicate++;
            logger.debug('Group is duplicate', {
              vkId: group.id,
              name: group.name
            });
          } else {
            validGroups.push(group);
            stats.valid++;
          }
        }

        // Подсчитываем невалидные (не вернулись из VK API)
        const returnedIds = new Set(groupsInfo.map(g => String(g.id)));
        for (const identifier of batchIdentifiers) {
          const idStr = String(identifier);
          if (!returnedIds.has(idStr)) {
            stats.invalid++;
            errors.push({
              identifier: idStr,
              error: 'Group not found or inaccessible',
              timestamp: new Date()
            });
          }
        }

        stats.processed += batchIdentifiers.length;

        // Обновляем прогресс (0-70% на fetching)
        const fetchProgress = (currentBatch / totalBatches) * 70;
        await this.updateProgress(job, {
          percentage: Math.round(fetchProgress),
          stage: 'fetching',
          currentBatch,
          totalBatches,
          stats
        });

        logger.info('Batch processed', {
          batch: currentBatch,
          totalBatches,
          validInBatch: groupsInfo.length,
          totalValid: stats.valid,
          totalDuplicate: stats.duplicate,
          totalInvalid: stats.invalid
        });

        // Задержка между батчами для rate limiting
        if (currentBatch < totalBatches) {
          await new Promise(resolve => setTimeout(resolve, BATCH_CONFIG.BATCH_DELAY_MS));
        }

      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        logger.error('Error processing batch', {
          batch: currentBatch,
          totalBatches,
          error: errorMsg
        });

        // Добавляем все идентификаторы батча в ошибки
        for (const identifier of batchIdentifiers) {
          stats.invalid++;
          errors.push({
            identifier: String(identifier),
            error: `Batch error: ${errorMsg}`,
            timestamp: new Date()
          });
        }

        stats.processed += batchIdentifiers.length;

        // Продолжаем обработку следующих батчей
        continue;
      }
    }

    logger.info('All batches processed', {
      totalValid: validGroups.length,
      totalInvalid: stats.invalid,
      totalDuplicate: stats.duplicate
    });

    return validGroups;
  }

  /**
   * Сохраняет группы в БД батчами
   *
   * @param groups - Массив валидных групп для сохранения
   * @param taskId - ID задачи
   * @param job - Job для обновления прогресса
   * @param stats - Статистика для обновления
   */
  private async saveGroupsBatch(
    groups: ProcessedGroup[],
    taskId: number,
    job: Job<ProcessGroupsJobData>,
    stats: GroupsParseJobResult['stats'] & { processed: number }
  ): Promise<void> {
    const totalSaveBatches = Math.ceil(groups.length / BATCH_CONFIG.DB_SAVE_BATCH_SIZE);

    logger.info('Starting groups saving', {
      totalGroups: groups.length,
      batchSize: BATCH_CONFIG.DB_SAVE_BATCH_SIZE,
      totalBatches: totalSaveBatches
    });

    for (let i = 0; i < groups.length; i += BATCH_CONFIG.DB_SAVE_BATCH_SIZE) {
      const currentBatch = Math.floor(i / BATCH_CONFIG.DB_SAVE_BATCH_SIZE) + 1;
      const batchGroups = groups.slice(i, i + BATCH_CONFIG.DB_SAVE_BATCH_SIZE);

      try {
        // Преобразуем в формат для БД
        const groupsData: CreateGroupInput[] = batchGroups.map(group => ({
          vk_id: group.id,
          name: group.name,
          screen_name: group.screen_name,
          photo_50: group.photo_50,
          members_count: group.members_count,
          is_closed: group.is_closed,
          description: group.description,
          status: 'valid' as const
        }));

        // Сохраняем батч в БД
        const savedGroups = await groupsRepo.createGroups(groupsData, String(taskId));
        stats.saved += savedGroups.length;

        // Обновляем прогресс (70-95% на saving)
        const saveProgress = 70 + (currentBatch / totalSaveBatches) * 25;
        await this.updateProgress(job, {
          percentage: Math.round(saveProgress),
          stage: 'saving',
          currentBatch,
          totalBatches: totalSaveBatches,
          stats
        });

        logger.info('Save batch completed', {
          batch: currentBatch,
          totalBatches: totalSaveBatches,
          savedInBatch: savedGroups.length,
          totalSaved: stats.saved
        });

      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : String(error);
        logger.error('Error saving batch to DB', {
          batch: currentBatch,
          totalBatches: totalSaveBatches,
          batchSize: batchGroups.length,
          error: errorMsg
        });
        // Не прерываем процесс, но логируем ошибку
        // stats.saved не увеличивается для этого батча
      }
    }

    logger.info('All groups saved', {
      totalSaved: stats.saved,
      totalGroups: groups.length
    });
  }

  /**
   * Обновляет прогресс выполнения job'а
   * Синхронизирует прогресс между BullMQ и Task Service
   *
   * @param job - Job для обновления
   * @param progress - Данные прогресса
   */
  private async updateProgress(
    job: Job<ProcessGroupsJobData>,
    progress: Partial<GroupsParseJobProgress>
  ): Promise<void> {
    try {
      // Обновляем прогресс в BullMQ
      await job.updateProgress(progress);

      // Обновляем прогресс в Task Service
      if (typeof progress.percentage === 'number') {
        await taskService.updateTaskProgress(
          job.data.taskId,
          progress.percentage,
          {
            stage: progress.stage,
            currentBatch: progress.currentBatch,
            totalBatches: progress.totalBatches,
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
      // Не прерываем выполнение из-за ошибки обновления прогресса
    }
  }

  /**
   * Настраивает обработчики событий worker'а для мониторинга
   */
  private setupEventHandlers(): void {
    this.worker.on('ready', () => {
      this.isRunning = true;
      logger.info('GroupsParseWorker ready', {
        queueName: QUEUE_NAMES.PROCESS_GROUPS,
        concurrency: this.worker.opts.concurrency
      });
    });

    this.worker.on('completed', (job: Job<ProcessGroupsJobData>, result: GroupsParseJobResult) => {
      logger.info('Groups parse job completed', {
        jobId: job.id,
        taskId: job.data.taskId,
        success: result.success,
        stats: result.stats,
        errorsCount: result.errors.length
      });
    });

    this.worker.on('failed', (job: Job<ProcessGroupsJobData> | undefined, error: Error) => {
      logger.error('Groups parse job failed', {
        jobId: job?.id,
        taskId: job?.data.taskId,
        error: error.message,
        stack: error.stack
      });
    });

    this.worker.on('progress', (job: Job<ProcessGroupsJobData>, progress: GroupsParseJobProgress) => {
      logger.debug('Groups parse job progress', {
        jobId: job.id,
        taskId: job.data.taskId,
        percentage: progress.percentage,
        stage: progress.stage,
        stats: progress.stats
      });
    });

    this.worker.on('error', (error: Error) => {
      logger.error('GroupsParseWorker error', {
        error: error.message,
        stack: error.stack
      });
    });

    this.worker.on('stalled', (jobId: string) => {
      logger.warn('Groups parse job stalled', { jobId });
    });

    this.worker.on('drained', () => {
      logger.debug('GroupsParseWorker queue drained');
    });
  }

  /**
   * Запускает worker
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      logger.warn('GroupsParseWorker already running');
      return;
    }

    try {
      logger.info('Starting GroupsParseWorker', {
        queueName: QUEUE_NAMES.PROCESS_GROUPS
      });
      // Worker автоматически стартует при создании
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to start GroupsParseWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to start GroupsParseWorker: ${errorMsg}`,
        'WORKER_START_FAILED',
        undefined,
        error instanceof Error ? error : undefined
      );
    }
  }

  /**
   * Останавливает worker gracefully
   */
  async stop(): Promise<void> {
    if (!this.isRunning) {
      logger.warn('GroupsParseWorker already stopped');
      return;
    }

    try {
      await this.worker.close();
      this.isRunning = false;
      logger.info('GroupsParseWorker stopped');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to stop GroupsParseWorker', { error: errorMsg });
      throw new WorkerError(
        `Failed to stop GroupsParseWorker: ${errorMsg}`,
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
      queueName: QUEUE_NAMES.PROCESS_GROUPS
    };
  }

  /**
   * Возвращает экземпляр worker'а для прямого доступа
   */
  getWorkerInstance(): TypedWorker<ProcessGroupsJobData, GroupsParseJobResult> {
    return this.worker;
  }
}

// Экспортируем singleton экземпляр
const groupsParseWorker = new GroupsParseWorker();
export default groupsParseWorker;
