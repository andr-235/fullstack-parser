# План рефакторинга QueueService

**Дата создания**: 2025-10-01
**Файл**: `backend/src/services/queueService.ts`
**Статус**: Готов к выполнению

---

## 🎯 Цели рефакторинга

Применить паттерн **Handler'ов** из GroupsService для разделения ответственности и улучшения архитектуры.

### Принципы из GroupsService

1. **Разделение на специализированные Handler'ы** - каждый handler отвечает за свой аспект
2. **Фасад паттерн** - главный сервис делегирует работу handler'ам
3. **Dependency Injection** - handler'ы получают зависимости через конструктор
4. **Обратная совместимость** - публичные методы сохраняют сигнатуры
5. **Сокращение кода** - из 606 строк до ~150 в фасаде

---

## 📊 Текущая архитектура QueueService

### Текущая структура (606 строк)

```
QueueService (606 строк)
├── Инициализация (initialize, initializeWorkers)
├── Job Management (addVkCollectJob, addProcessGroupsJob)
├── Job Operations (getJob, removeJob)
├── Queue Control (pauseQueue, resumeQueue)
├── Statistics (getJobCounts)
├── Health Check (healthCheck)
├── Events (setupQueueEventHandlers)
└── Cleanup (cleanup)
```

### Проблемы

- ❌ Дублирование в `addVkCollectJob` и `addProcessGroupsJob` (строки 211-295)
- ❌ Смешение ответственности (управление очередями + workers + события)
- ❌ 600+ строк в одном файле
- ❌ Сложность тестирования
- ❌ BaseWorker интерфейс определен локально (строки 21-36)

---

## 🏗️ Новая архитектура (по паттерну GroupsService)

### Структура модулей

```
backend/src/services/queue/
├── QueueService.ts                 # Фасад (~150 строк)
├── QueueInitHandler.ts             # Инициализация очередей и workers
├── QueueJobHandler.ts              # Управление jobs (add, get, remove)
├── QueueControlHandler.ts          # Управление очередями (pause, resume)
├── QueueMonitoringHandler.ts      # Статистика и health checks
└── types.ts                        # Локальные типы (если нужно)

backend/src/types/queue.ts          # Добавить BaseWorker интерфейс сюда
```

### Разделение ответственности

#### 1. **QueueService** (Фасад)

```typescript
/**
 * Фасад над специализированными handler'ами
 * - QueueInitHandler - инициализация и cleanup
 * - QueueJobHandler - операции с jobs
 * - QueueControlHandler - управление очередями
 * - QueueMonitoringHandler - мониторинг и health checks
 */
class QueueService implements IQueueService {
  private initHandler: QueueInitHandler;
  private jobHandler: QueueJobHandler;
  private controlHandler: QueueControlHandler;
  private monitoringHandler: QueueMonitoringHandler;

  constructor() {
    // Dependency Injection
    this.initHandler = new QueueInitHandler();
    this.jobHandler = new QueueJobHandler(/* queues */);
    this.controlHandler = new QueueControlHandler(/* queues */);
    this.monitoringHandler = new QueueMonitoringHandler(/* queues, workers */);
  }

  // Делегируем методы handler'ам
  async initialize() {
    return this.initHandler.initialize();
  }

  async addVkCollectJob(data, taskId, options) {
    return this.jobHandler.addVkCollectJob(data, taskId, options);
  }

  async healthCheck() {
    return this.monitoringHandler.healthCheck();
  }

  // ...другие методы делегирования
}
```

#### 2. **QueueInitHandler** - Инициализация

**Ответственность**:
- Инициализация очередей (BullMQ Queue)
- Инициализация QueueEvents
- Регистрация workers
- Настройка event handlers
- Cleanup ресурсов

**Методы**:
```typescript
class QueueInitHandler {
  async initialize(): Promise<void>
  private async initializeQueues(): Promise<void>
  private async initializeWorkers(): Promise<void>
  private setupQueueEventHandlers(queueName, events): void
  async cleanup(): Promise<void>
}
```

**Зависимости**: `QUEUE_CONFIGS`, `createQueueRedisConnection`, workers

#### 3. **QueueJobHandler** - Управление Jobs

**Ответственность**:
- Добавление jobs в очереди (generic метод)
- Получение job по ID
- Удаление jobs
- Получение jobs по статусу
- Retry failed jobs

**Методы**:
```typescript
class QueueJobHandler {
  constructor(private queues: Map<string, Queue>) {}

  // Generic метод для устранения дублирования
  private async addGenericJob<T extends AnyJobData>(
    queueName: string,
    jobName: string,
    data: T,
    options?: JobsOptions
  ): Promise<Job<T>>

  async addVkCollectJob(data, taskId, options): Promise<Job<VkCollectJobData>>
  async addProcessGroupsJob(data, taskId, options): Promise<Job<ProcessGroupsJobData>>

  async getJob(jobId: string): Promise<Job | null>
  async removeJob(jobId: string): Promise<void>
  async retryJob(jobId: string): Promise<void>
}
```

**Использование p-retry** для надежности:
```typescript
import pRetry from 'p-retry';

private async addGenericJob<T extends AnyJobData>(...) {
  return pRetry(
    async () => {
      const queue = this.getQueue(queueName);
      const jobData = { ...data, taskId } as T;
      const jobOptions = this.buildJobOptions(queueName, options);
      return await queue.add(jobName, jobData, jobOptions);
    },
    {
      retries: 3,
      onFailedAttempt: (error) => {
        logger.warn('Failed to add job, retrying', {
          queueName,
          attempt: error.attemptNumber,
          error: error.message
        });
      }
    }
  );
}
```

#### 4. **QueueControlHandler** - Управление очередями

**Ответственность**:
- Пауза/возобновление очередей
- Управление workers (start/stop/pause/resume)
- Получение QueueEvents

**Методы**:
```typescript
class QueueControlHandler {
  constructor(
    private queues: Map<string, Queue>,
    private workers: Map<string, BaseWorker>
  ) {}

  async pauseQueue(): Promise<void>
  async resumeQueue(): Promise<void>
  async pauseWorkers(): Promise<void>
  async resumeWorkers(): Promise<void>
  getQueueEvents(queueName: string): QueueEvents
}
```

#### 5. **QueueMonitoringHandler** - Мониторинг

**Ответственность**:
- Получение статистики jobs
- Health checks очередей
- Health checks workers
- Детальный мониторинг

**Методы**:
```typescript
class QueueMonitoringHandler {
  constructor(
    private queues: Map<string, Queue>,
    private workers: Map<string, BaseWorker>
  ) {}

  async getJobCounts(): Promise<JobCountsResult>
  async getQueueStats(queueName: string): Promise<QueueStats>
  async healthCheck(): Promise<HealthCheckResult>
  private async checkRedisConnection(): Promise<boolean>
  private async checkQueueBacklog(): Promise<BacklogStatus>
  private async checkWorkersHealth(): Promise<WorkerHealth[]>
}
```

**Улучшенный Health Check**:
```typescript
async healthCheck() {
  const checks = await Promise.all([
    this.checkRedisConnection(),
    this.checkQueueBacklog(),
    this.checkWorkersHealth(),
    this.getJobCounts()
  ]);

  const [redisOk, backlogOk, workersHealth, jobCounts] = checks;

  const allWorkersHealthy = workersHealth.every(w => w.status === 'healthy');
  const overallStatus = redisOk && backlogOk && allWorkersHealthy
    ? 'healthy'
    : 'unhealthy';

  return {
    status: overallStatus,
    details: {
      redis: { connected: redisOk },
      queues: { backlogOk, counts: jobCounts },
      workers: workersHealth,
      timestamp: new Date()
    }
  };
}
```

---

## 🔧 Конкретные изменения по файлам

### 1. Переместить BaseWorker в типы

**Файл**: `backend/src/types/queue.ts`

**Добавить**:
```typescript
/**
 * Базовый интерфейс для worker'ов
 */
export interface BaseWorker {
  start(): Promise<void>;
  stop(): Promise<void>;
  pause(): Promise<void>;
  resume(): Promise<void>;
  getStatus(): WorkerStatus;
  healthCheck?(): Promise<WorkerHealthCheck>;
}

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
 * Классификация ошибок
 */
export enum ErrorSeverity {
  TRANSIENT = 'transient',    // Можно retry
  PERMANENT = 'permanent',     // Нельзя retry
  UNKNOWN = 'unknown'
}
```

### 2. Создать QueueJobHandler

**Файл**: `backend/src/services/queue/QueueJobHandler.ts`

```typescript
import { Queue, Job, JobsOptions } from 'bullmq';
import pRetry from 'p-retry';
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
 * Использует generic методы для устранения дублирования
 */
export class QueueJobHandler {
  constructor(private readonly queues: Map<string, Queue>) {}

  /**
   * Generic метод для добавления jobs любого типа
   * Устраняет дублирование между addVkCollectJob и addProcessGroupsJob
   */
  private async addGenericJob<T extends AnyJobData>(
    queueName: string,
    jobName: string,
    data: Omit<T, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<T>> {
    return pRetry(
      async () => {
        const queue = this.getQueue(queueName);
        const jobData = { ...data, taskId } as T;

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
      },
      {
        retries: 3,
        minTimeout: 1000,
        onFailedAttempt: (error) => {
          logger.warn('Failed to add job, retrying', {
            queueName,
            jobName,
            taskId,
            attempt: error.attemptNumber,
            retriesLeft: error.retriesLeft,
            error: error.message,
          });
        },
      }
    );
  }

  /**
   * Добавляет VK collect job
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
   * Добавляет process groups job
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
   * Retry failed job
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
```

### 3. Создать QueueInitHandler

**Файл**: `backend/src/services/queue/QueueInitHandler.ts`

```typescript
import { Queue, QueueEvents } from 'bullmq';
import {
  QUEUE_NAMES,
  QUEUE_CONFIGS,
  createQueueRedisConnection,
  createQueueEventsRedisConnection,
} from '@/config/queue';
import { vkCollectWorker } from '@/workers';
import { BaseWorker, QueueError } from '@/types/queue';
import logger from '@/utils/logger';

/**
 * Handler для инициализации очередей и workers
 */
export class QueueInitHandler {
  private queues: Map<string, Queue> = new Map();
  private queueEvents: Map<string, QueueEvents> = new Map();
  private workers: Map<string, BaseWorker> = new Map();
  private isInitialized = false;

  /**
   * Инициализация всех очередей и workers
   */
  async initialize(): Promise<{
    queues: Map<string, Queue>;
    queueEvents: Map<string, QueueEvents>;
    workers: Map<string, BaseWorker>;
  }> {
    if (this.isInitialized) {
      logger.warn('QueueService already initialized');
      return {
        queues: this.queues,
        queueEvents: this.queueEvents,
        workers: this.workers,
      };
    }

    try {
      logger.info('Initializing BullMQ queues...');

      await this.initializeQueues();
      await this.initializeWorkers();

      this.isInitialized = true;
      logger.info('All BullMQ queues and workers initialized successfully');

      return {
        queues: this.queues,
        queueEvents: this.queueEvents,
        workers: this.workers,
      };
    } catch (error) {
      logger.error('Failed to initialize BullMQ queues', {
        error: (error as Error).message,
        stack: (error as Error).stack,
      });
      throw new QueueError(
        'Queue initialization failed',
        'INIT_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Инициализация очередей
   */
  private async initializeQueues(): Promise<void> {
    const queueConnection = createQueueRedisConnection();
    const eventsConnection = createQueueEventsRedisConnection();

    for (const [queueName, config] of Object.entries(QUEUE_CONFIGS)) {
      const queue = new Queue(queueName, {
        connection: queueConnection,
        defaultJobOptions: config.defaultJobOptions,
      });

      const events = new QueueEvents(queueName, {
        connection: eventsConnection,
      });

      this.setupQueueEventHandlers(queueName, events);

      this.queues.set(queueName, queue);
      this.queueEvents.set(queueName, events);

      logger.info(`Queue initialized: ${queueName}`, {
        concurrency: config.concurrency,
        attempts: config.defaultJobOptions.attempts,
      });
    }
  }

  /**
   * Инициализация workers
   */
  private async initializeWorkers(): Promise<void> {
    try {
      logger.info('Initializing BullMQ workers...');

      await vkCollectWorker.start();
      this.workers.set(QUEUE_NAMES.VK_COLLECT, vkCollectWorker);

      logger.info('VkCollectWorker started', {
        queueName: QUEUE_NAMES.VK_COLLECT,
        status: vkCollectWorker.getStatus(),
      });

      logger.info('All BullMQ workers initialized successfully', {
        workersCount: this.workers.size,
      });
    } catch (error) {
      logger.error('Failed to initialize BullMQ workers', {
        error: (error as Error).message,
        stack: (error as Error).stack,
      });
      throw new QueueError(
        'Workers initialization failed',
        'WORKERS_INIT_FAILED',
        undefined,
        error as Error
      );
    }
  }

  /**
   * Настройка обработчиков событий для очереди
   */
  private setupQueueEventHandlers(queueName: string, events: QueueEvents): void {
    events.on('waiting', ({ jobId }) => {
      logger.debug(`Job waiting: ${jobId}`, { queue: queueName });
    });

    events.on('active', ({ jobId }) => {
      logger.info(`Job started: ${jobId}`, { queue: queueName });
    });

    events.on('completed', ({ jobId, returnvalue }) => {
      logger.info(`Job completed: ${jobId}`, {
        queue: queueName,
        returnValue: returnvalue,
      });
    });

    events.on('failed', ({ jobId, failedReason }) => {
      logger.error(`Job failed: ${jobId}`, {
        queue: queueName,
        reason: failedReason,
      });
    });

    events.on('progress', ({ jobId, data }) => {
      logger.debug(`Job progress: ${jobId}`, {
        queue: queueName,
        progress: data,
      });
    });

    events.on('removed', ({ jobId }) => {
      logger.debug(`Job removed: ${jobId}`, { queue: queueName });
    });

    events.on('stalled', ({ jobId }) => {
      logger.warn(`Job stalled: ${jobId}`, { queue: queueName });
    });
  }

  /**
   * Очистка ресурсов
   */
  async cleanup(): Promise<void> {
    try {
      logger.info('Cleaning up BullMQ queues and workers...');

      // Останавливаем workers
      for (const [workerName, worker] of this.workers) {
        try {
          await worker.stop();
          logger.debug(`Worker stopped: ${workerName}`);
        } catch (error) {
          logger.warn(`Failed to stop worker ${workerName}`, {
            error: (error as Error).message,
          });
        }
      }

      // Закрываем QueueEvents
      for (const [queueName, events] of this.queueEvents) {
        await events.close();
        logger.debug(`Queue events closed: ${queueName}`);
      }

      // Закрываем очереди
      for (const [queueName, queue] of this.queues) {
        await queue.close();
        logger.debug(`Queue closed: ${queueName}`);
      }

      this.workers.clear();
      this.queues.clear();
      this.queueEvents.clear();
      this.isInitialized = false;

      logger.info('BullMQ queues and workers cleanup completed');
    } catch (error) {
      logger.error('Failed to cleanup BullMQ queues', {
        error: (error as Error).message,
      });
      throw new QueueError(
        'Cleanup failed',
        'CLEANUP_FAILED',
        undefined,
        error as Error
      );
    }
  }

  isReady(): boolean {
    return this.isInitialized;
  }
}
```

### 4. Создать остальные Handler'ы

**QueueControlHandler** и **QueueMonitoringHandler** создаются аналогично с перемещением соответствующих методов.

### 5. Обновить QueueService (Фасад)

**Файл**: `backend/src/services/queueService.ts`

```typescript
/**
 * @fileoverview QueueService - Рефакторированный сервис управления очередями
 *
 * ✅ ВЫПОЛНЕНО:
 * - Разделен на специализированные handler'ы
 * - Сокращен с 606 до ~150 строк
 * - Сохранена полная обратная совместимость
 * - Устранено дублирование кода
 * - Добавлена библиотека p-retry
 *
 * Архитектура (по паттерну GroupsService):
 * - QueueInitHandler - инициализация и cleanup
 * - QueueJobHandler - операции с jobs
 * - QueueControlHandler - управление очередями
 * - QueueMonitoringHandler - мониторинг и health checks
 */

import { Job, QueueEvents, JobsOptions } from 'bullmq';
import {
  IQueueService,
  VkCollectJobData,
  ProcessGroupsJobData,
} from '@/types/queue';

// Handler'ы для разделения ответственности
import { QueueInitHandler } from './queue/QueueInitHandler';
import { QueueJobHandler } from './queue/QueueJobHandler';
import { QueueControlHandler } from './queue/QueueControlHandler';
import { QueueMonitoringHandler } from './queue/QueueMonitoringHandler';

/**
 * Сервис управления BullMQ очередями
 *
 * Фасад над специализированными handler'ами:
 * - QueueInitHandler - инициализация и cleanup
 * - QueueJobHandler - операции с jobs
 * - QueueControlHandler - управление очередями
 * - QueueMonitoringHandler - мониторинг и health checks
 */
export class QueueService implements IQueueService {
  private initHandler!: QueueInitHandler;
  private jobHandler!: QueueJobHandler;
  private controlHandler!: QueueControlHandler;
  private monitoringHandler!: QueueMonitoringHandler;

  private isInitialized = false;

  /**
   * Инициализация всех очередей
   */
  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    // Инициализируем init handler
    this.initHandler = new QueueInitHandler();
    const { queues, queueEvents, workers } = await this.initHandler.initialize();

    // Инициализируем остальные handler'ы с зависимостями
    this.jobHandler = new QueueJobHandler(queues);
    this.controlHandler = new QueueControlHandler(queues, queueEvents, workers);
    this.monitoringHandler = new QueueMonitoringHandler(queues, workers);

    this.isInitialized = true;
  }

  // ============ Job Operations (делегирование JobHandler) ============

  async addVkCollectJob(
    data: Omit<VkCollectJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<VkCollectJobData>> {
    return this.jobHandler.addVkCollectJob(data, taskId, options);
  }

  async addProcessGroupsJob(
    data: Omit<ProcessGroupsJobData, 'taskId'>,
    taskId: number,
    options?: JobsOptions
  ): Promise<Job<ProcessGroupsJobData>> {
    return this.jobHandler.addProcessGroupsJob(data, taskId, options);
  }

  async getJob(jobId: string) {
    return this.jobHandler.getJob(jobId);
  }

  async removeJob(jobId: string): Promise<void> {
    return this.jobHandler.removeJob(jobId);
  }

  // ============ Queue Control (делегирование ControlHandler) ============

  async pauseQueue(): Promise<void> {
    return this.controlHandler.pauseQueue();
  }

  async resumeQueue(): Promise<void> {
    return this.controlHandler.resumeQueue();
  }

  getQueueEvents(): QueueEvents {
    return this.controlHandler.getQueueEvents();
  }

  // ============ Monitoring (делегирование MonitoringHandler) ============

  async getJobCounts() {
    return this.monitoringHandler.getJobCounts();
  }

  async healthCheck() {
    return this.monitoringHandler.healthCheck();
  }

  // ============ Lifecycle (делегирование InitHandler) ============

  async cleanup(): Promise<void> {
    return this.initHandler.cleanup();
  }
}

// Singleton instance
export const queueService = new QueueService();
```

---

## 📦 Библиотеки для использования

### p-retry - Умные retry стратегии

```bash
npm install p-retry
npm install -D @types/p-retry
```

**Использование**: Автоматические повторы при temporary failures в `addGenericJob`

---

## 🧪 План тестирования

### Unit тесты

**Файлы**:
- `backend/tests/unit/services/queue/QueueJobHandler.test.ts`
- `backend/tests/unit/services/queue/QueueInitHandler.test.ts`
- `backend/tests/unit/services/queue/QueueMonitoringHandler.test.ts`

**Тесты**:
```typescript
describe('QueueJobHandler', () => {
  describe('addGenericJob', () => {
    it('should add job with correct options', async () => {});
    it('should retry on failure', async () => {});
    it('should throw QueueError when queue not found', async () => {});
  });

  describe('getJob', () => {
    it('should return job when found', async () => {});
    it('should return null when not found', async () => {});
  });
});
```

### Integration тесты

**Файл**: `backend/tests/integration/queue/QueueService.integration.test.ts`

```typescript
describe('QueueService Integration', () => {
  beforeAll(async () => {
    await queueService.initialize();
  });

  afterAll(async () => {
    await queueService.cleanup();
  });

  it('should process VK collect job end-to-end', async () => {
    // Test full job lifecycle
  });
});
```

---

## 📋 Чеклист выполнения

### Фаза 1: Подготовка (30 мин)
- [ ] Создать ветку `refactor/queue-service-handlers`
- [ ] Установить p-retry: `npm install p-retry @types/p-retry`
- [ ] Создать структуру `services/queue/`
- [ ] Переместить `BaseWorker` в `types/queue.ts`

### Фаза 2: Создание Handler'ов (3-4 часа)
- [ ] Создать `QueueJobHandler.ts` с generic методом
- [ ] Создать `QueueInitHandler.ts`
- [ ] Создать `QueueControlHandler.ts`
- [ ] Создать `QueueMonitoringHandler.ts`

### Фаза 3: Рефакторинг QueueService (1-2 часа)
- [ ] Превратить QueueService в фасад
- [ ] Добавить делегирование всех методов
- [ ] Убедиться в обратной совместимости
- [ ] Удалить старый код

### Фаза 4: Обновление Worker'ов (1 час)
- [ ] Добавить `pause()` и `resume()` в VkCollectWorker
- [ ] Убедиться что реализован `healthCheck()`

### Фаза 5: Тестирование (2-3 часа)
- [ ] Написать unit тесты для handler'ов
- [ ] Написать integration тесты
- [ ] Manual testing с реальными jobs
- [ ] Проверить health check endpoints

### Фаза 6: Документация (30 мин)
- [ ] Обновить JSDoc комментарии
- [ ] Обновить CLAUDE.md
- [ ] Создать файл REFACTORING_PHASE_2_COMPLETED.md
- [ ] Code review и merge

**Общее время**: ~8-11 часов

---

## 🚀 Преимущества после рефакторинга

### Сокращение кода
- ✅ **QueueService**: с 606 до ~150 строк (-75%)
- ✅ Устранено ~80 строк дублирования в job operations

### Архитектура
- ✅ Четкое разделение ответственности
- ✅ Handler pattern как в GroupsService
- ✅ Dependency Injection
- ✅ Легкое тестирование изолированных компонентов

### Надежность
- ✅ Автоматические retry с p-retry
- ✅ Улучшенный error handling
- ✅ Расширенный health check

### Поддерживаемость
- ✅ Модульная структура
- ✅ Generic методы вместо дублирования
- ✅ Понятная архитектура
- ✅ Полная обратная совместимость

---

## 📝 Примечания

### Обратная совместимость
✅ Все публичные методы `IQueueService` сохраняют свои сигнатуры

### Миграция данных
✅ Не требуется - jobs в Redis остаются совместимыми

### Deployment
✅ Можно делать без downtime

### Вдохновение
Архитектура основана на успешном рефакторинге GroupsService (750 → 100 строк)

---

**Автор**: Claude Code AI Assistant
**Версия**: 2.0
**Статус**: Готов к выполнению
**Паттерн**: Handler-based Architecture (из GroupsService)
