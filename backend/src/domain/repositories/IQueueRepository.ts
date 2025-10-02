/**
 * @fileoverview Интерфейс репозитория очередей задач (Domain Layer)
 *
 * Определяет контракт для работы с очередями фоновых задач (обычно BullMQ).
 * Реализация находится в Infrastructure Layer.
 */

/**
 * Опции для добавления задачи в очередь
 */
export interface QueueJobOptions {
  /** Приоритет задачи (чем меньше число, тем выше приоритет) */
  readonly priority?: number;

  /** Задержка перед выполнением в миллисекундах */
  readonly delay?: number;

  /** Количество попыток при ошибке */
  readonly attempts?: number;

  /** Задержка между попытками (экспоненциальная) */
  readonly backoff?: {
    readonly type: 'exponential' | 'fixed';
    readonly delay: number;
  };

  /** Удалить задачу после завершения */
  readonly removeOnComplete?: boolean | number;

  /** Удалить задачу после ошибки */
  readonly removeOnFail?: boolean | number;

  /** Таймаут выполнения задачи в миллисекундах */
  readonly timeout?: number;
}

/**
 * Статус задачи в очереди
 */
export type JobStatus =
  | 'waiting'
  | 'active'
  | 'completed'
  | 'failed'
  | 'delayed'
  | 'paused';

/**
 * Информация о задаче в очереди
 */
export interface QueueJob<TData = any, TResult = any> {
  readonly id: string;
  readonly name: string;
  readonly data: TData;
  readonly status: JobStatus;
  readonly progress: number;
  readonly attemptsMade: number;
  readonly finishedOn?: Date;
  readonly processedOn?: Date;
  readonly failedReason?: string;
  readonly returnvalue?: TResult;
}

/**
 * Статистика очереди
 */
export interface QueueStats {
  readonly waiting: number;
  readonly active: number;
  readonly completed: number;
  readonly failed: number;
  readonly delayed: number;
  readonly paused: number;
}

/**
 * Интерфейс репозитория для работы с очередями задач
 *
 * @description
 * Предоставляет методы для управления фоновыми задачами.
 * Абстрагирует детали работы с BullMQ от domain логики.
 */
export interface IQueueRepository {
  /**
   * Добавляет задачу в очередь
   *
   * @param queueName - имя очереди
   * @param jobName - имя задачи
   * @param data - данные для обработки
   * @param options - опции задачи
   * @returns ID созданной задачи
   */
  addJob<TData>(
    queueName: string,
    jobName: string,
    data: TData,
    options?: QueueJobOptions
  ): Promise<string>;

  /**
   * Получает задачу по ID
   *
   * @param queueName - имя очереди
   * @param jobId - ID задачи
   * @returns информация о задаче или null
   */
  getJob<TData, TResult>(
    queueName: string,
    jobId: string
  ): Promise<QueueJob<TData, TResult> | null>;

  /**
   * Получает статус задачи
   *
   * @param queueName - имя очереди
   * @param jobId - ID задачи
   * @returns статус или null если задача не найдена
   */
  getJobStatus(queueName: string, jobId: string): Promise<JobStatus | null>;

  /**
   * Удаляет задачу из очереди
   *
   * @param queueName - имя очереди
   * @param jobId - ID задачи
   * @returns true если задача была удалена
   */
  removeJob(queueName: string, jobId: string): Promise<boolean>;

  /**
   * Получает задачи по статусу
   *
   * @param queueName - имя очереди
   * @param status - статус задач
   * @param start - начальный индекс
   * @param end - конечный индекс
   * @returns массив задач
   */
  getJobsByStatus<TData, TResult>(
    queueName: string,
    status: JobStatus,
    start?: number,
    end?: number
  ): Promise<readonly QueueJob<TData, TResult>[]>;

  /**
   * Получает статистику очереди
   *
   * @param queueName - имя очереди
   * @returns статистика по всем статусам
   */
  getQueueStats(queueName: string): Promise<QueueStats>;

  /**
   * Очищает очередь от завершенных задач
   *
   * @param queueName - имя очереди
   * @param grace - время в миллисекундах (удалить старше этого времени)
   * @returns количество удаленных задач
   */
  cleanQueue(queueName: string, grace?: number): Promise<number>;

  /**
   * Приостанавливает очередь
   *
   * @param queueName - имя очереди
   */
  pauseQueue(queueName: string): Promise<void>;

  /**
   * Возобновляет очередь
   *
   * @param queueName - имя очереди
   */
  resumeQueue(queueName: string): Promise<void>;

  /**
   * Очищает все задачи в очереди
   *
   * @param queueName - имя очереди
   * @returns количество удаленных задач
   */
  obliterateQueue(queueName: string): Promise<number>;

  /**
   * Проверяет здоровье очереди
   *
   * @param queueName - имя очереди
   * @returns true если очередь работает нормально
   */
  isQueueHealthy(queueName: string): Promise<boolean>;

  /**
   * Регистрирует обработчик задач
   *
   * @param queueName - имя очереди
   * @param processor - функция обработки задач
   */
  registerProcessor<TData, TResult>(
    queueName: string,
    processor: (job: QueueJob<TData, any>) => Promise<TResult>
  ): Promise<void>;
}
