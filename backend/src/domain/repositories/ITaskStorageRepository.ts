/**
 * @fileoverview Интерфейс репозитория хранилища задач (Domain Layer)
 *
 * Определяет контракт для работы с временным хранилищем задач (обычно Redis).
 * Реализация находится в Infrastructure Layer.
 */

/**
 * Базовая информация о задаче
 */
export interface TaskInfo<TProgress = any> {
  readonly taskId: string;
  readonly status: 'pending' | 'processing' | 'completed' | 'failed';
  readonly progress: TProgress;
  readonly errors: readonly string[];
  readonly createdAt: Date;
  readonly startedAt: Date | null;
  readonly completedAt: Date | null;
  readonly failureReason?: string;
}

/**
 * Прогресс загрузки групп
 */
export interface GroupUploadProgress {
  readonly total: number;
  readonly processed: number;
  readonly valid: number;
  readonly invalid: number;
  readonly duplicates: number;
}

/**
 * Прогресс сбора данных VK
 */
export interface VkCollectProgress {
  readonly total: number;
  readonly processed: number;
  readonly successful: number;
  readonly failed: number;
  readonly currentBatch?: number;
  readonly totalBatches?: number;
}

/**
 * Задача загрузки групп
 */
export type GroupUploadTask = TaskInfo<GroupUploadProgress>;

/**
 * Задача сбора данных VK
 */
export type VkCollectTask = TaskInfo<VkCollectProgress>;

/**
 * Интерфейс репозитория для временного хранилища задач
 *
 * @description
 * Предоставляет методы для работы с задачами в кэше (Redis).
 * Используется для отслеживания прогресса долгих операций.
 */
export interface ITaskStorageRepository {
  /**
   * Сохраняет задачу в хранилище
   *
   * @param taskId - уникальный идентификатор задачи
   * @param task - данные задачи
   * @param ttl - время жизни в секундах (optional)
   */
  saveTask<T extends TaskInfo>(taskId: string, task: T, ttl?: number): Promise<void>;

  /**
   * Получает задачу из хранилища
   *
   * @param taskId - уникальный идентификатор задачи
   * @returns задача или null если не найдена
   */
  getTask<T extends TaskInfo>(taskId: string): Promise<T | null>;

  /**
   * Обновляет статус задачи
   *
   * @param taskId - уникальный идентификатор задачи
   * @param status - новый статус
   * @param updates - дополнительные поля для обновления
   */
  updateTaskStatus<T extends TaskInfo>(
    taskId: string,
    status: T['status'],
    updates?: Partial<Omit<T, 'taskId' | 'status'>>
  ): Promise<void>;

  /**
   * Обновляет прогресс задачи
   *
   * @param taskId - уникальный идентификатор задачи
   * @param progress - новые данные прогресса
   */
  updateTaskProgress<TProgress>(taskId: string, progress: Partial<TProgress>): Promise<void>;

  /**
   * Удаляет задачу из хранилища
   *
   * @param taskId - уникальный идентификатор задачи
   * @returns true если задача была удалена
   */
  deleteTask(taskId: string): Promise<boolean>;

  /**
   * Удаляет все задачи определенного типа
   *
   * @param pattern - паттерн для поиска задач (например, 'group-upload:*')
   * @returns количество удаленных задач
   */
  deleteTasksByPattern(pattern: string): Promise<number>;

  /**
   * Получает все задачи по паттерну
   *
   * @param pattern - паттерн для поиска (например, 'group-upload:*')
   * @returns массив задач
   */
  findTasksByPattern<T extends TaskInfo>(pattern: string): Promise<readonly T[]>;

  /**
   * Проверяет существование задачи
   *
   * @param taskId - уникальный идентификатор задачи
   * @returns true если задача существует
   */
  taskExists(taskId: string): Promise<boolean>;

  /**
   * Продлевает время жизни задачи
   *
   * @param taskId - уникальный идентификатор задачи
   * @param ttl - новое время жизни в секундах
   */
  extendTaskTTL(taskId: string, ttl: number): Promise<void>;

  /**
   * Очищает завершенные задачи старше указанного времени
   *
   * @param olderThanHours - удалить задачи старше N часов
   * @returns количество удаленных задач
   */
  cleanupOldTasks(olderThanHours: number): Promise<number>;
}
