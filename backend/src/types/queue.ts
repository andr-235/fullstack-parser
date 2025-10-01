import { Job, JobsOptions, Worker, QueueEvents } from 'bullmq';
import { TaskType, TaskStatus, BullJobData, JobProgress } from './task';

// =============================================================================
// BullMQ Job Types
// =============================================================================

/**
 * VK коллекция задач - основной тип job'ов для сбора комментариев
 */
export interface VkCollectJobData extends BullJobData {
  type: 'fetch_comments';
  metadata: {
    groups: Array<{
      vkId: string;
      name: string;
    }>;
    options: {
      limit?: number;
      includeReplies?: boolean;
      filterWords?: string[];
      token?: string;
    };
  };
}

/**
 * Обработка групп из файла - парсинг групп VK через VK-IO API
 * Принимает массив идентификаторов (VK ID или screen_name)
 */
export interface ProcessGroupsJobData extends BullJobData {
  type: 'process_groups';
  metadata: {
    groupIdentifiers: string[];  // VK ID (числа как строки) или screen_name
    source: 'file' | 'manual';   // Источник данных
    originalFileName?: string;   // Имя загруженного файла
  };
}

/**
 * Прогресс выполнения парсинга групп
 */
export interface GroupsParseJobProgress extends JobProgress {
  percentage: number;  // 0-100
  stage: 'init' | 'fetching' | 'saving' | 'done';
  currentBatch?: number;
  totalBatches?: number;
  stats: {
    total: number;      // Всего идентификаторов
    processed: number;  // Обработано
    valid: number;      // Валидных групп найдено
    invalid: number;    // Невалидных/недоступных
    duplicate: number;  // Дубликатов в БД
  };
}

/**
 * Результат выполнения парсинга групп
 */
export interface GroupsParseJobResult {
  success: boolean;
  taskId: number;
  stats: {
    total: number;
    valid: number;
    invalid: number;
    duplicate: number;
    saved: number;
  };
  errors: Array<{
    identifier: string;
    error: string;
    timestamp: Date;
  }>;
  processingTimeMs: number;
}

/**
 * Анализ постов (будущая фича)
 */
export interface AnalyzePostsJobData extends BullJobData {
  type: 'analyze_posts';
  metadata: {
    postUrls: string[];
    analysisType: 'sentiment' | 'keywords' | 'engagement';
  };
}

/**
 * Результат выполнения VK collect job'а
 */
export interface VkCollectJobResult {
  success: boolean;
  taskId: number;
  commentsCollected: number;
  postsProcessed: number;
  groupsProcessed: number;
  errors: Array<{
    groupId: string;
    error: string;
    timestamp: Date;
  }>;
  processingTime: number;
  finalStatus: TaskStatus;
}

/**
 * Прогресс выполнения VK collect job'а
 */
export interface VkCollectJobProgress extends JobProgress {
  stage: 'starting' | 'fetching_posts' | 'fetching_comments' | 'saving_data' | 'completing';
  currentGroup?: {
    vkId: string;
    name: string;
    progress: number;
  };
  stats: {
    groupsCompleted: number;
    totalGroups: number;
    postsProcessed: number;
    commentsCollected: number;
  };
}

// =============================================================================
// Queue Configuration Types
// =============================================================================

/**
 * Конфигурация Redis соединения для BullMQ
 */
export interface QueueRedisConfig {
  host: string;
  port: number;
  password?: string;
  db?: number;
  maxRetriesPerRequest?: number | null;
  connectTimeout?: number;
  commandTimeout?: number;
  retryDelayOnFailover?: number;
  enableOfflineQueue?: boolean;
  lazyConnect?: boolean;
  keepAlive?: number;
}

/**
 * Опции для BullMQ очередей
 */
export interface QueueConfig {
  redis: QueueRedisConfig;
  defaultJobOptions: JobsOptions;
  concurrency: number;
  removeOnComplete: number;
  removeOnFail: number;
  settings?: {
    stalledInterval?: number;
    maxStalledCount?: number;
  };
}

/**
 * Конфигурация worker'а
 */
export interface WorkerConfig {
  redis: QueueRedisConfig;
  concurrency: number;
  stalledInterval: number;
  maxStalledCount: number;
  retryProcessDelay: number;
  limiter?: {
    max: number;
    duration: number;
  };
  settings?: {
    backoffStrategy?: (attemptsMade: number, type: string, err: Error) => number;
  };
}

// =============================================================================
// Union Types for Type Safety
// =============================================================================

/**
 * Все возможные типы job data
 */
export type AnyJobData = VkCollectJobData | ProcessGroupsJobData | AnalyzePostsJobData;

/**
 * Все возможные типы job results
 */
export type AnyJobResult = VkCollectJobResult | GroupsParseJobResult | any; // Расширится по мере добавления новых типов

/**
 * Все возможные типы job progress
 */
export type AnyJobProgress = VkCollectJobProgress | GroupsParseJobProgress | JobProgress;

// =============================================================================
// BullMQ Typed Wrappers
// =============================================================================

/**
 * Типизированный Job для конкретного типа данных
 */
export type TypedJob<T extends AnyJobData, R = AnyJobResult> = Job<T, R>;

/**
 * Типизированный Worker для конкретного типа данных
 */
export type TypedWorker<T extends AnyJobData, R = AnyJobResult> = Worker<T, R>;

/**
 * Процессор для конкретного типа job'а
 */
export type JobProcessor<T extends AnyJobData, R = AnyJobResult> = (
  job: TypedJob<T, R>
) => Promise<R>;

// =============================================================================
// Service Interface Types
// =============================================================================

/**
 * Интерфейс для Queue Service
 */
export interface IQueueService {
  // Методы для добавления job'ов
  addVkCollectJob(data: Omit<VkCollectJobData, 'taskId'>, taskId: number): Promise<Job<VkCollectJobData>>;
  addProcessGroupsJob(data: Omit<ProcessGroupsJobData, 'taskId'>, taskId: number): Promise<Job<ProcessGroupsJobData>>;

  // Методы для управления очередью
  getJobCounts(): Promise<{ waiting: number; active: number; completed: number; failed: number }>;
  getJob(jobId: string): Promise<Job | null>;
  removeJob(jobId: string): Promise<void>;
  pauseQueue(): Promise<void>;
  resumeQueue(): Promise<void>;

  // Методы для мониторинга
  getQueueEvents(): QueueEvents;
  cleanup(): Promise<void>;
}

/**
 * Интерфейс для Worker Service
 */
export interface IWorkerService {
  // Регистрация процессоров
  registerVkCollectProcessor(processor: JobProcessor<VkCollectJobData, VkCollectJobResult>): void;
  registerProcessGroupsProcessor(processor: JobProcessor<ProcessGroupsJobData>): void;

  // Управление worker'ом
  start(): Promise<void>;
  stop(): Promise<void>;
  pause(): Promise<void>;
  resume(): Promise<void>;

  // Мониторинг
  getWorkerStatus(): {
    isRunning: boolean;
    isPaused: boolean;
    concurrency: number;
    processing: number;
  };
}

// =============================================================================
// Error Types
// =============================================================================

/**
 * Ошибки связанные с очередью
 */
export class QueueError extends Error {
  constructor(
    message: string,
    public code: string,
    public jobId?: string,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'QueueError';
  }
}

/**
 * Ошибки связанные с worker'ом
 */
export class WorkerError extends Error {
  constructor(
    message: string,
    public code: string,
    public jobId?: string,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'WorkerError';
  }
}

/**
 * Ошибки связанные с Redis соединением
 */
export class RedisConnectionError extends Error {
  constructor(
    message: string,
    public originalError?: Error
  ) {
    super(message);
    this.name = 'RedisConnectionError';
  }
}

// =============================================================================
// Worker Base Interface
// =============================================================================

/**
 * Статус worker'а
 */
export interface WorkerStatus {
  isRunning: boolean;
  isPaused: boolean;
  concurrency: number;
  queueName: string;
}

/**
 * Health check worker'а
 */
export interface WorkerHealthCheck {
  status: 'healthy' | 'unhealthy';
  details: {
    isRunning: boolean;
    isPaused: boolean;
    concurrency: number;
    queueName: string;
    uptime?: number;
  };
  error?: string;
}

/**
 * Базовый интерфейс для worker'ов
 * Определяет контракт для всех worker'ов в системе
 */
export interface BaseWorker {
  /**
   * Запуск worker'а
   */
  start(): Promise<void>;

  /**
   * Остановка worker'а
   */
  stop(): Promise<void>;

  /**
   * Приостановка обработки job'ов
   */
  pause(): Promise<void>;

  /**
   * Возобновление обработки job'ов
   */
  resume(): Promise<void>;

  /**
   * Получение текущего статуса worker'а
   */
  getStatus(): WorkerStatus;

  /**
   * Health check worker'а (опционально)
   */
  healthCheck?(): Promise<WorkerHealthCheck>;
}

/**
 * Классификация ошибок для retry стратегии
 */
export enum ErrorSeverity {
  TRANSIENT = 'transient',    // Можно retry (временные ошибки)
  PERMANENT = 'permanent',     // Нельзя retry (постоянные ошибки)
  UNKNOWN = 'unknown'          // Неизвестный тип ошибки
}