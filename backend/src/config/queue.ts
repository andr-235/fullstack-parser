/**
 * @fileoverview Конфигурация BullMQ очередей и worker'ов
 * Централизованное управление асинхронными задачами
 *
 * Особенности:
 * - Настройки всех типов очередей (VK_COLLECT, PROCESS_GROUPS, etc.)
 * - Worker конфигурации с rate limiting
 * - Backoff стратегии и retry политики
 * - Redis connection factories
 * - Health checks и monitoring
 * - Graceful shutdown handling
 */

import { QueueConfig, WorkerConfig } from '@/types/queue';
import { createRedisConnection, redisConfig } from './redis';

/**
 * Имена очередей в системе
 */
export const QUEUE_NAMES = {
  VK_COLLECT: 'vk-collect',
  PROCESS_GROUPS: 'process-groups',
  ANALYZE_POSTS: 'analyze-posts',
} as const;

/**
 * Конфигурация по умолчанию для BullMQ очередей
 */
export const DEFAULT_QUEUE_CONFIG: QueueConfig = {
  redis: redisConfig,
  defaultJobOptions: {
    // Настройки повторных попыток
    attempts: 3,
    backoff: {
      type: 'exponential',
      delay: 5000, // 5 секунд базовая задержка
    },

    // Задержка перед выполнением
    delay: 1000, // 1 секунда

    // Время жизни job'а
    removeOnComplete: 100, // Хранить последние 100 успешных
    removeOnFail: 50, // Хранить последние 50 неудачных

    // Примечание: timeout убран, так как не поддерживается в новых версиях BullMQ
    // Используйте Worker timeout вместо этого

    // Приоритет (выше число = выше приоритет)
    priority: 0,
  },

  // Общие настройки очереди
  concurrency: 5, // Максимум 5 одновременных job'ов
  removeOnComplete: 100,
  removeOnFail: 50,

  settings: {
    stalledInterval: 30000, // 30 секунд
    maxStalledCount: 1, // Максимум 1 "зависший" job
  },
};

/**
 * Конфигурация по умолчанию для BullMQ worker'ов
 */
export const DEFAULT_WORKER_CONFIG: WorkerConfig = {
  redis: redisConfig,
  concurrency: 3, // 3 одновременных задачи на worker
  stalledInterval: 30000, // 30 секунд
  maxStalledCount: 1,
  retryProcessDelay: 5000, // 5 секунд между попытками

  // Rate limiting для защиты внешних API
  limiter: {
    max: 10, // Максимум 10 jobs
    duration: 60000, // За 60 секунд
  },

  settings: {
    // Exponential backoff стратегия
    backoffStrategy: (attemptsMade: number, type: string, err: Error): number => {
      // Базовая задержка увеличивается экспоненциально
      const baseDelay = 5000; // 5 секунд
      const maxDelay = 300000; // 5 минут максимум

      const delay = Math.min(baseDelay * Math.pow(2, attemptsMade - 1), maxDelay);

      // Добавляем случайную составляющую для избежания "thundering herd"
      const jitter = Math.random() * 1000; // 0-1 секунда

      return delay + jitter;
    },
  },
};

/**
 * Специфичные конфигурации для разных типов очередей
 */
export const QUEUE_CONFIGS = {
  [QUEUE_NAMES.VK_COLLECT]: {
    ...DEFAULT_QUEUE_CONFIG,
    defaultJobOptions: {
      ...DEFAULT_QUEUE_CONFIG.defaultJobOptions,
      // VK API требует более осторожного подхода
      attempts: 5, // Больше попыток из-за rate limits
      timeout: 600000, // 10 минут на сбор комментариев
      priority: 10, // Высокий приоритет
    },
    concurrency: 2, // Меньше concurrent jobs для VK API
  },

  [QUEUE_NAMES.PROCESS_GROUPS]: {
    ...DEFAULT_QUEUE_CONFIG,
    defaultJobOptions: {
      ...DEFAULT_QUEUE_CONFIG.defaultJobOptions,
      timeout: 120000, // 2 минуты на обработку файла
      priority: 5, // Средний приоритет
    },
    concurrency: 3,
  },

  [QUEUE_NAMES.ANALYZE_POSTS]: {
    ...DEFAULT_QUEUE_CONFIG,
    defaultJobOptions: {
      ...DEFAULT_QUEUE_CONFIG.defaultJobOptions,
      timeout: 180000, // 3 минуты на анализ
      priority: 1, // Низкий приоритет
    },
    concurrency: 4,
  },
} as const;

/**
 * Специфичные конфигурации worker'ов
 */
export const WORKER_CONFIGS = {
  [QUEUE_NAMES.VK_COLLECT]: {
    ...DEFAULT_WORKER_CONFIG,
    concurrency: 1, // Только один VK job одновременно
    limiter: {
      max: 3, // Очень консервативный rate limit для VK API
      duration: 60000,
    },
  },

  [QUEUE_NAMES.PROCESS_GROUPS]: {
    ...DEFAULT_WORKER_CONFIG,
    concurrency: 2,
    limiter: {
      max: 10,
      duration: 60000,
    },
  },

  [QUEUE_NAMES.ANALYZE_POSTS]: {
    ...DEFAULT_WORKER_CONFIG,
    concurrency: 3,
    limiter: {
      max: 15,
      duration: 60000,
    },
  },
} as const;

/**
 * Создает Redis соединение для очередей
 */
export function createQueueRedisConnection() {
  return createRedisConnection();
}

/**
 * Создает Redis соединение для worker'ов
 */
export function createWorkerRedisConnection() {
  return createRedisConnection();
}

/**
 * Создает Redis соединение для QueueEvents
 */
export function createQueueEventsRedisConnection() {
  return createRedisConnection();
}