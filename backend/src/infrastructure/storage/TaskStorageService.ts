/**
 * @fileoverview Redis-backed persistent storage для upload tasks
 *
 * Заменяет in-memory Map<string, UploadTask> на persistent Redis storage
 *
 * Features:
 * - ✅ Persistent storage (переживает рестарты сервера)
 * - ✅ TTL для автоочистки старых задач
 * - ✅ Type-safe interface с GroupUploadTask
 * - ✅ Comprehensive error handling
 * - ✅ Structured logging
 * - ✅ Health checks и статистика
 *
 * @example
 * ```typescript
 * import { taskStorageService } from '@/infrastructure/storage/TaskStorageService';
 *
 * // Сохранить задачу
 * await taskStorageService.saveTask(taskId, task);
 *
 * // Получить задачу
 * const task = await taskStorageService.getTask(taskId);
 *
 * // Обновить прогресс
 * await taskStorageService.updateTask(taskId, {
 *   progress: { ...task.progress, processed: 50 }
 * });
 * ```
 */

import { Redis } from 'ioredis';
import { GroupUploadTask } from '@/domain/groups/types';
import { TaskStorageError, TaskNotFoundError } from '@/domain/groups/errors';
import logger from '@infrastructure/utils/logger';

/**
 * Конфигурация для TaskStorageService
 */
export interface TaskStorageConfig {
  /** Префикс для Redis ключей */
  keyPrefix: string;
  /** TTL для задач в секундах (по умолчанию 24 часа) */
  ttl: number;
  /** Включить автоочистку при инициализации */
  autoCleanup: boolean;
  /** Интервал автоочистки в часах */
  cleanupIntervalHours: number;
}

/**
 * Конфигурация по умолчанию
 */
const DEFAULT_CONFIG: TaskStorageConfig = {
  keyPrefix: 'groups:upload:task:',
  ttl: 86400, // 24 часа
  autoCleanup: true,
  cleanupIntervalHours: 12,
};

/**
 * Сервис для хранения задач загрузки групп в Redis
 *
 * Обеспечивает persistent хранилище для GroupUploadTask
 * вместо in-memory Map, что позволяет:
 * - Сохранять состояние между рестартами
 * - Масштабироваться горизонтально
 * - Автоматически очищать старые задачи
 */
export class TaskStorageService {
  private readonly config: TaskStorageConfig;
  private cleanupInterval?: NodeJS.Timeout;

  constructor(
    private readonly redis: Redis,
    config?: Partial<TaskStorageConfig>
  ) {
    this.config = { ...DEFAULT_CONFIG, ...config };

    logger.info('TaskStorageService initialized', {
      keyPrefix: this.config.keyPrefix,
      ttl: this.config.ttl,
      autoCleanup: this.config.autoCleanup,
    });

    // Запускаем автоочистку если включена
    if (this.config.autoCleanup) {
      this.startAutoCleanup();
    }
  }

  // ============ Core Operations ============

  /**
   * Сохраняет задачу в Redis с TTL
   *
   * @throws TaskStorageError если сохранение не удалось
   */
  async saveTask(taskId: string, task: GroupUploadTask): Promise<void> {
    try {
      const key = this.getKey(taskId);
      const serialized = JSON.stringify(task);

      await this.redis.setex(key, this.config.ttl, serialized);

      logger.debug('Task saved to Redis', {
        taskId,
        key,
        status: task.status,
        progress: task.progress,
        ttl: this.config.ttl,
      });
    } catch (error) {
      logger.error('Failed to save task to Redis', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
      });

      throw new TaskStorageError('Failed to save task', { taskId });
    }
  }

  /**
   * Получает задачу из Redis
   *
   * @returns Task или null если не найдена
   * @throws TaskStorageError если чтение не удалось
   */
  async getTask(taskId: string): Promise<GroupUploadTask | null> {
    try {
      const key = this.getKey(taskId);
      const data = await this.redis.get(key);

      if (!data) {
        logger.debug('Task not found in Redis', { taskId, key });
        return null;
      }

      const task = JSON.parse(data) as GroupUploadTask;

      // Восстанавливаем Date объекты (JSON.parse конвертирует в string)
      const restored: GroupUploadTask = {
        ...task,
        createdAt: new Date(task.createdAt),
        startedAt: task.startedAt ? new Date(task.startedAt) : null,
        completedAt: task.completedAt ? new Date(task.completedAt) : null,
      };

      logger.debug('Task retrieved from Redis', {
        taskId,
        status: restored.status,
        age: Date.now() - restored.createdAt.getTime(),
      });

      return restored;
    } catch (error) {
      logger.error('Failed to get task from Redis', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
      });

      throw new TaskStorageError('Failed to retrieve task', { taskId });
    }
  }

  /**
   * Обновляет существующую задачу
   *
   * @throws TaskNotFoundError если задача не существует
   * @throws TaskStorageError если обновление не удалось
   */
  async updateTask(
    taskId: string,
    updates: Partial<GroupUploadTask>
  ): Promise<void> {
    const existing = await this.getTask(taskId);

    if (!existing) {
      throw new TaskNotFoundError(taskId);
    }

    const updated: GroupUploadTask = {
      ...existing,
      ...updates,
    };

    await this.saveTask(taskId, updated);

    logger.debug('Task updated in Redis', {
      taskId,
      updatedFields: Object.keys(updates),
      newStatus: updated.status,
    });
  }

  /**
   * Удаляет задачу из Redis
   */
  async deleteTask(taskId: string): Promise<void> {
    try {
      const key = this.getKey(taskId);
      const deleted = await this.redis.del(key);

      if (deleted === 0) {
        logger.warn('Task not found for deletion', { taskId, key });
      } else {
        logger.debug('Task deleted from Redis', { taskId, key });
      }
    } catch (error) {
      logger.error('Failed to delete task', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
      });

      throw new TaskStorageError('Failed to delete task', { taskId });
    }
  }

  // ============ Batch Operations ============

  /**
   * Получает все задачи из Redis
   */
  async getAllTasks(): Promise<GroupUploadTask[]> {
    try {
      const pattern = `${this.config.keyPrefix}*`;
      const keys = await this.redis.keys(pattern);

      if (keys.length === 0) {
        logger.debug('No tasks found in Redis', { pattern });
        return [];
      }

      logger.debug('Found tasks in Redis', {
        count: keys.length,
        pattern,
      });

      // Параллельное получение всех задач
      const tasks = await Promise.all(
        keys.map(async (key) => {
          const taskId = key.replace(this.config.keyPrefix, '');
          return this.getTask(taskId);
        })
      );

      // Фильтруем null значения
      return tasks.filter((t): t is GroupUploadTask => t !== null);
    } catch (error) {
      logger.error('Failed to get all tasks', {
        error: error instanceof Error ? error.message : String(error),
      });

      throw new TaskStorageError('Failed to retrieve tasks');
    }
  }

  /**
   * Удаляет старые завершенные задачи
   *
   * @param olderThanHours - Удалить задачи старше N часов
   * @returns Количество удаленных задач
   */
  async cleanupOldTasks(olderThanHours: number = 24): Promise<number> {
    try {
      const tasks = await this.getAllTasks();
      const cutoff = new Date();
      cutoff.setHours(cutoff.getHours() - olderThanHours);

      let removed = 0;

      for (const task of tasks) {
        const shouldDelete =
          task.completedAt &&
          task.completedAt < cutoff &&
          (task.status === 'completed' || task.status === 'failed');

        if (shouldDelete) {
          await this.deleteTask(task.taskId);
          removed++;
        }
      }

      logger.info('Cleaned up old tasks', {
        removed,
        olderThanHours,
        totalTasks: tasks.length,
        cutoffDate: cutoff.toISOString(),
      });

      return removed;
    } catch (error) {
      logger.error('Failed to cleanup old tasks', {
        olderThanHours,
        error: error instanceof Error ? error.message : String(error),
      });

      throw new TaskStorageError('Failed to cleanup tasks');
    }
  }

  // ============ Utility Operations ============

  /**
   * Проверяет существование задачи
   */
  async taskExists(taskId: string): Promise<boolean> {
    try {
      const key = this.getKey(taskId);
      const exists = await this.redis.exists(key);
      return exists === 1;
    } catch (error) {
      logger.error('Failed to check task existence', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
      });
      return false;
    }
  }

  /**
   * Получает TTL задачи в секундах
   *
   * @returns TTL или -1 если ключа не существует, -2 если нет TTL
   */
  async getTaskTTL(taskId: string): Promise<number> {
    try {
      const key = this.getKey(taskId);
      return await this.redis.ttl(key);
    } catch (error) {
      logger.error('Failed to get task TTL', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
      });
      return -1;
    }
  }

  /**
   * Продлевает TTL задачи
   */
  async extendTaskTTL(taskId: string, additionalSeconds: number): Promise<void> {
    try {
      const key = this.getKey(taskId);
      const currentTTL = await this.redis.ttl(key);

      if (currentTTL < 0) {
        throw new TaskNotFoundError(taskId);
      }

      const newTTL = currentTTL + additionalSeconds;
      await this.redis.expire(key, newTTL);

      logger.debug('Task TTL extended', {
        taskId,
        oldTTL: currentTTL,
        newTTL,
        additionalSeconds,
      });
    } catch (error) {
      if (error instanceof TaskNotFoundError) {
        throw error;
      }

      logger.error('Failed to extend task TTL', {
        taskId,
        error: error instanceof Error ? error.message : String(error),
      });

      throw new TaskStorageError('Failed to extend TTL', { taskId });
    }
  }

  // ============ Statistics & Monitoring ============

  /**
   * Возвращает статистику хранилища
   */
  async getStats(): Promise<{
    totalTasks: number;
    tasksByStatus: Record<string, number>;
    averageTTL: number;
    oldestTask: Date | null;
    newestTask: Date | null;
  }> {
    const tasks = await this.getAllTasks();

    const tasksByStatus: Record<string, number> = {};
    let oldestTask: Date | null = null;
    let newestTask: Date | null = null;

    for (const task of tasks) {
      // Статистика по статусам
      tasksByStatus[task.status] = (tasksByStatus[task.status] || 0) + 1;

      // Поиск самой старой и новой задачи
      if (!oldestTask || task.createdAt < oldestTask) {
        oldestTask = task.createdAt;
      }
      if (!newestTask || task.createdAt > newestTask) {
        newestTask = task.createdAt;
      }
    }

    // Вычисляем средний TTL
    const ttls = await Promise.all(
      tasks.map((t) => this.getTaskTTL(t.taskId))
    );
    const validTTLs = ttls.filter((ttl) => ttl > 0);
    const averageTTL = validTTLs.length > 0
      ? validTTLs.reduce((sum, ttl) => sum + ttl, 0) / validTTLs.length
      : 0;

    return {
      totalTasks: tasks.length,
      tasksByStatus,
      averageTTL: Math.round(averageTTL),
      oldestTask,
      newestTask,
    };
  }

  /**
   * Health check для мониторинга
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    details: {
      redisConnected: boolean;
      totalTasks: number;
      canWrite: boolean;
      canRead: boolean;
    };
    error?: string;
  }> {
    try {
      // Проверка соединения
      await this.redis.ping();

      // Проверка записи
      const testKey = `${this.config.keyPrefix}healthcheck`;
      await this.redis.setex(testKey, 10, 'test');

      // Проверка чтения
      const testValue = await this.redis.get(testKey);

      // Очистка
      await this.redis.del(testKey);

      // Получение статистики
      const tasks = await this.getAllTasks();

      return {
        status: 'healthy',
        details: {
          redisConnected: true,
          totalTasks: tasks.length,
          canWrite: testValue === 'test',
          canRead: testValue === 'test',
        },
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        details: {
          redisConnected: false,
          totalTasks: 0,
          canWrite: false,
          canRead: false,
        },
        error: error instanceof Error ? error.message : String(error),
      };
    }
  }

  // ============ Auto-Cleanup ============

  /**
   * Запускает автоматическую очистку старых задач
   */
  private startAutoCleanup(): void {
    const intervalMs = this.config.cleanupIntervalHours * 60 * 60 * 1000;

    this.cleanupInterval = setInterval(async () => {
      try {
        logger.info('Running automatic task cleanup');
        const removed = await this.cleanupOldTasks(this.config.cleanupIntervalHours);
        logger.info('Automatic cleanup completed', { removed });
      } catch (error) {
        logger.error('Automatic cleanup failed', {
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }, intervalMs);

    logger.info('Auto-cleanup started', {
      intervalHours: this.config.cleanupIntervalHours,
      intervalMs,
    });
  }

  /**
   * Останавливает автоматическую очистку
   */
  stopAutoCleanup(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = undefined;
      logger.info('Auto-cleanup stopped');
    }
  }

  /**
   * Graceful shutdown
   */
  async shutdown(): Promise<void> {
    this.stopAutoCleanup();
    logger.info('TaskStorageService shutdown completed');
  }

  // ============ Private Helpers ============

  /**
   * Формирует полный Redis key для задачи
   */
  private getKey(taskId: string): string {
    return `${this.config.keyPrefix}${taskId}`;
  }
}

// ============ Factory & Singleton ============

import { getRedisClient } from '@infrastructure/config/redis';

/**
 * Singleton экземпляр TaskStorageService
 * Используйте этот экземпляр во всем приложении
 */
export const taskStorageService = new TaskStorageService(getRedisClient());

/**
 * Factory функция для создания кастомного экземпляра
 * Полезно для тестирования или специальных случаев
 */
export function createTaskStorageService(
  redis: Redis,
  config?: Partial<TaskStorageConfig>
): TaskStorageService {
  return new TaskStorageService(redis, config);
}
