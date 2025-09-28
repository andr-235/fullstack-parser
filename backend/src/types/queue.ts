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
 * Обработка групп из файла
 */
export interface ProcessGroupsJobData extends BullJobData {
  type: 'process_groups';
  metadata: {
    filePath: string;
    originalName: string;
    validationRules?: {
      requireVkId?: boolean;
      requireName?: boolean;
    };
  };
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
export type AnyJobResult = VkCollectJobResult | any; // Расширится по мере добавления новых типов

/**
 * Все возможные типы job progress
 */
export type AnyJobProgress = VkCollectJobProgress | JobProgress;

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