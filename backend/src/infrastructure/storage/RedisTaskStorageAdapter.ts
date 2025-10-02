/**
 * @fileoverview RedisTaskStorageAdapter - реализация ITaskStorageRepository
 *
 * Infrastructure adapter для работы с задачами через Redis.
 */

import Redis from 'ioredis';
import {
  ITaskStorageRepository,
  TaskInfo
} from '@domain/repositories/ITaskStorageRepository';
import logger from '@infrastructure/utils/logger';

/**
 * Redis adapter для хранения задач
 *
 * @description
 * Использует Redis для временного хранения информации о задачах.
 * Предоставляет быстрый доступ к статусу задач.
 */
export class RedisTaskStorageAdapter implements ITaskStorageRepository {
  private readonly redis: Redis;
  private readonly keyPrefix = 'task:';
  private readonly defaultTTL = 24 * 60 * 60; // 24 часа

  constructor(redisClient: Redis) {
    if (!redisClient) {
      throw new Error('Redis client is required');
    }

    this.redis = redisClient;
    logger.info('RedisTaskStorageAdapter initialized');
  }

  /**
   * Сохраняет задачу в Redis
   */
  async saveTask<T extends TaskInfo>(taskId: string, task: T, ttl?: number): Promise<void> {
    try {
      const key = this.buildKey(taskId);
      const data = JSON.stringify(task);
      const expiration = ttl || this.defaultTTL;

      await this.redis.setex(key, expiration, data);

      logger.debug('Task saved to Redis', { taskId, ttl: expiration });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to save task to Redis', { taskId, error: errorMsg });
      throw new Error(`Failed to save task: ${errorMsg}`);
    }
  }

  /**
   * Получает задачу из Redis
   */
  async getTask<T extends TaskInfo>(taskId: string): Promise<T | null> {
    try {
      const key = this.buildKey(taskId);
      const data = await this.redis.get(key);

      if (!data) {
        logger.debug('Task not found in Redis', { taskId });
        return null;
      }

      const parsedTask = JSON.parse(data);

      // Преобразуем строки дат обратно в Date объекты
      const task: T = {
        ...parsedTask,
        createdAt: parsedTask.createdAt ? new Date(parsedTask.createdAt) : parsedTask.createdAt,
        startedAt: parsedTask.startedAt ? new Date(parsedTask.startedAt) : parsedTask.startedAt,
        completedAt: parsedTask.completedAt ? new Date(parsedTask.completedAt) : parsedTask.completedAt
      } as T;

      return task;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get task from Redis', { taskId, error: errorMsg });
      throw new Error(`Failed to get task: ${errorMsg}`);
    }
  }

  /**
   * Обновляет статус задачи
   */
  async updateTaskStatus<T extends TaskInfo>(
    taskId: string,
    status: T['status'],
    updates?: Partial<Omit<T, 'taskId' | 'status'>>
  ): Promise<void> {
    try {
      const task = await this.getTask<T>(taskId);

      if (!task) {
        throw new Error(`Task ${taskId} not found`);
      }

      const updatedTask: T = {
        ...task,
        status,
        ...updates
      } as T;

      await this.saveTask(taskId, updatedTask);

      logger.debug('Task status updated', { taskId, status });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update task status', { taskId, status, error: errorMsg });
      throw new Error(`Failed to update task status: ${errorMsg}`);
    }
  }

  /**
   * Обновляет прогресс задачи
   */
  async updateTaskProgress<TProgress>(taskId: string, progress: Partial<TProgress>): Promise<void> {
    try {
      const task = await this.getTask<TaskInfo<TProgress>>(taskId);

      if (!task) {
        throw new Error(`Task ${taskId} not found`);
      }

      const updatedTask: TaskInfo<TProgress> = {
        ...task,
        progress: {
          ...task.progress,
          ...progress
        }
      };

      await this.saveTask(taskId, updatedTask);

      logger.debug('Task progress updated', { taskId });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update task progress', { taskId, error: errorMsg });
      throw new Error(`Failed to update task progress: ${errorMsg}`);
    }
  }

  /**
   * Удаляет задачу из Redis
   */
  async deleteTask(taskId: string): Promise<boolean> {
    try {
      const key = this.buildKey(taskId);
      const result = await this.redis.del(key);

      const deleted = result > 0;
      logger.debug('Task deleted from Redis', { taskId, deleted });

      return deleted;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete task from Redis', { taskId, error: errorMsg });
      throw new Error(`Failed to delete task: ${errorMsg}`);
    }
  }

  /**
   * Удаляет все задачи по паттерну
   */
  async deleteTasksByPattern(pattern: string): Promise<number> {
    try {
      const fullPattern = this.keyPrefix + pattern;
      const keys = await this.redis.keys(fullPattern);

      if (keys.length === 0) {
        return 0;
      }

      const result = await this.redis.del(...keys);

      logger.info('Tasks deleted by pattern', { pattern, count: result });
      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete tasks by pattern', { pattern, error: errorMsg });
      throw new Error(`Failed to delete tasks: ${errorMsg}`);
    }
  }

  /**
   * Получает все задачи по паттерну
   */
  async findTasksByPattern<T extends TaskInfo>(pattern: string): Promise<readonly T[]> {
    try {
      const fullPattern = this.keyPrefix + pattern;
      const keys = await this.redis.keys(fullPattern);

      if (keys.length === 0) {
        return [];
      }

      const pipeline = this.redis.pipeline();
      keys.forEach(key => pipeline.get(key));

      const results = await pipeline.exec();

      if (!results) {
        return [];
      }

      const tasks: T[] = [];

      for (const [error, data] of results) {
        if (error || !data) {
          continue;
        }

        try {
          const parsedTask = JSON.parse(data as string);

          // Преобразуем даты
          const task: T = {
            ...parsedTask,
            createdAt: parsedTask.createdAt ? new Date(parsedTask.createdAt) : parsedTask.createdAt,
            startedAt: parsedTask.startedAt ? new Date(parsedTask.startedAt) : parsedTask.startedAt,
            completedAt: parsedTask.completedAt ? new Date(parsedTask.completedAt) : parsedTask.completedAt
          } as T;

          tasks.push(task);
        } catch {
          // Игнорируем невалидные задачи
          continue;
        }
      }

      return tasks;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to find tasks by pattern', { pattern, error: errorMsg });
      throw new Error(`Failed to find tasks: ${errorMsg}`);
    }
  }

  /**
   * Проверяет существование задачи
   */
  async taskExists(taskId: string): Promise<boolean> {
    try {
      const key = this.buildKey(taskId);
      const exists = await this.redis.exists(key);

      return exists === 1;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to check task existence', { taskId, error: errorMsg });
      return false;
    }
  }

  /**
   * Продлевает время жизни задачи
   */
  async extendTaskTTL(taskId: string, ttl: number): Promise<void> {
    try {
      const key = this.buildKey(taskId);
      await this.redis.expire(key, ttl);

      logger.debug('Task TTL extended', { taskId, ttl });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to extend task TTL', { taskId, error: errorMsg });
      throw new Error(`Failed to extend TTL: ${errorMsg}`);
    }
  }

  /**
   * Очищает завершенные задачи старше указанного времени
   */
  async cleanupOldTasks(olderThanHours: number): Promise<number> {
    try {
      const allTasks = await this.findTasksByPattern<TaskInfo>('*');
      const cutoffTime = Date.now() - olderThanHours * 60 * 60 * 1000;

      let deletedCount = 0;

      for (const task of allTasks) {
        // Удаляем только завершенные или проваленные задачи
        if (task.status !== 'completed' && task.status !== 'failed') {
          continue;
        }

        const taskTime = task.completedAt
          ? task.completedAt.getTime()
          : task.createdAt.getTime();

        if (taskTime < cutoffTime) {
          const deleted = await this.deleteTask(task.taskId);
          if (deleted) {
            deletedCount++;
          }
        }
      }

      logger.info('Old tasks cleaned up', { olderThanHours, deletedCount });
      return deletedCount;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to cleanup old tasks', { olderThanHours, error: errorMsg });
      throw new Error(`Failed to cleanup tasks: ${errorMsg}`);
    }
  }

  // ============ Private Helpers ============

  /**
   * Строит ключ для Redis
   */
  private buildKey(taskId: string): string {
    return `${this.keyPrefix}${taskId}`;
  }
}
