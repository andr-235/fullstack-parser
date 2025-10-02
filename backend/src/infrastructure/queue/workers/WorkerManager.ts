/**
 * @fileoverview WorkerManager - управление всеми worker'ами
 *
 * Централизованное управление BullMQ worker'ами приложения.
 * Запуск, остановка и мониторинг worker'ов.
 */

import { ProcessGroupsWorker } from './ProcessGroupsWorker';
import { Container } from '@infrastructure/di/Container';
import logger from '@infrastructure/utils/logger';

/**
 * Статус worker'а
 */
export interface WorkerStatus {
  name: string;
  running: boolean;
  queueName: string;
  concurrency: number;
}

/**
 * WorkerManager - управление всеми worker'ами
 *
 * @description
 * Управляет жизненным циклом всех worker'ов:
 * - Запуск всех worker'ов при старте приложения
 * - Graceful shutdown при остановке
 * - Мониторинг статуса
 */
export class WorkerManager {
  private processGroupsWorker: ProcessGroupsWorker;
  // Добавятся другие worker'ы в будущем

  constructor(private readonly container: Container) {
    // Инициализируем worker'ы
    this.processGroupsWorker = new ProcessGroupsWorker(
      container.getRedis(),
      container.getGroupsRepository(),
      container.getVkApiRepository(),
      container.getTaskStorageRepository()
    );
  }

  /**
   * Запускает все worker'ы
   */
  async startAll(): Promise<void> {
    logger.info('Starting all workers...');

    try {
      await this.processGroupsWorker.start();
      // Добавятся другие worker'ы

      logger.info('All workers started successfully');
    } catch (error) {
      logger.error('Failed to start workers', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Останавливает все worker'ы (graceful shutdown)
   */
  async stopAll(): Promise<void> {
    logger.info('Stopping all workers...');

    const stopPromises: Promise<void>[] = [];

    try {
      if (this.processGroupsWorker.isRunning()) {
        stopPromises.push(this.processGroupsWorker.stop());
      }

      // Добавятся другие worker'ы

      await Promise.all(stopPromises);

      logger.info('All workers stopped successfully');
    } catch (error) {
      logger.error('Failed to stop workers', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }

  /**
   * Получает статус всех worker'ов
   */
  getStatus(): WorkerStatus[] {
    const statuses: WorkerStatus[] = [];

    // ProcessGroupsWorker
    const processGroupsStatus = this.processGroupsWorker.getStatus();
    statuses.push({
      name: 'ProcessGroupsWorker',
      running: processGroupsStatus.running,
      queueName: processGroupsStatus.queueName,
      concurrency: processGroupsStatus.concurrency
    });

    // Добавятся другие worker'ы

    return statuses;
  }

  /**
   * Проверяет, все ли worker'ы работают
   */
  areAllRunning(): boolean {
    return this.getStatus().every(status => status.running);
  }

  /**
   * Получает количество активных worker'ов
   */
  getActiveWorkersCount(): number {
    return this.getStatus().filter(status => status.running).length;
  }

  /**
   * Health check всех worker'ов
   */
  async healthCheck(): Promise<{
    healthy: boolean;
    workers: WorkerStatus[];
  }> {
    const workers = this.getStatus();
    const healthy = this.areAllRunning();

    return {
      healthy,
      workers
    };
  }
}
