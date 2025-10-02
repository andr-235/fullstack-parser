/**
 * @fileoverview Task Entity - сущность задачи обработки
 *
 * Представляет задачу в системе (загрузка групп, сбор данных VK и т.д.)
 */

import { TaskId } from '@domain/value-objects/TaskId';
import { InvariantViolationError, ValidationError } from '@domain/errors/DomainError';

/**
 * Статус задачи
 */
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Базовый интерфейс прогресса задачи
 */
export interface TaskProgress {
  readonly total: number;
  readonly processed: number;
}

/**
 * Параметры для создания Task entity
 */
export interface CreateTaskProps<TProgress extends TaskProgress = TaskProgress> {
  readonly id?: TaskId;
  readonly status: TaskStatus;
  readonly progress: TProgress;
  readonly errors: readonly string[];
  readonly createdAt?: Date;
  readonly startedAt?: Date | null;
  readonly completedAt?: Date | null;
  readonly failureReason?: string;
}

/**
 * Task Entity - базовая сущность задачи
 *
 * @description
 * Представляет задачу обработки в системе.
 * Может быть расширена конкретными типами задач.
 *
 * Инварианты:
 * - Задача не может быть завершена без startedAt
 * - processed не может быть больше total
 * - completedAt не может быть раньше startedAt
 * - failed задачи должны иметь failureReason
 *
 * @example
 * ```typescript
 * const task = Task.create({
 *   status: 'pending',
 *   progress: { total: 100, processed: 0 },
 *   errors: []
 * });
 *
 * task.start();
 * task.updateProgress(50);
 * task.complete();
 * ```
 */
export class Task<TProgress extends TaskProgress = TaskProgress> {
  protected readonly _id: TaskId;
  protected _status: TaskStatus;
  protected _progress: TProgress;
  protected _errors: string[];
  protected readonly _createdAt: Date;
  protected _startedAt: Date | null;
  protected _completedAt: Date | null;
  protected _failureReason?: string;

  protected constructor(props: CreateTaskProps<TProgress>) {
    this._id = props.id || TaskId.generate();
    this._status = props.status;
    this._progress = props.progress;
    this._errors = [...props.errors];
    this._createdAt = props.createdAt || new Date();
    this._startedAt = props.startedAt || null;
    this._completedAt = props.completedAt || null;
    this._failureReason = props.failureReason;

    this.validate();
  }

  /**
   * Создает новую задачу
   */
  public static create<TProgress extends TaskProgress = TaskProgress>(
    props: CreateTaskProps<TProgress>
  ): Task<TProgress> {
    return new Task<TProgress>(props);
  }

  /**
   * Восстанавливает задачу из хранилища
   * Дочерние классы должны переопределить этот метод
   */
  public static restore<TProgress extends TaskProgress = TaskProgress>(
    props: CreateTaskProps<TProgress> & { id: TaskId }
  ): Task<TProgress> {
    return new Task<TProgress>(props);
  }

  /**
   * Создает экземпляр из сохраненных данных (для наследования)
   */
  protected static fromProps<TProgress extends TaskProgress>(
    props: CreateTaskProps<TProgress> & { id: TaskId }
  ): Task<TProgress> {
    return new Task<TProgress>(props);
  }

  /**
   * Валидация инвариантов
   */
  protected validate(): void {
    // processed не может быть больше total
    if (this._progress.processed > this._progress.total) {
      throw new InvariantViolationError(
        `Processed count (${this._progress.processed}) cannot exceed total (${this._progress.total})`,
        'INVALID_PROGRESS',
        { taskId: this._id.value }
      );
    }

    // Завершенная задача должна иметь startedAt
    if (this._status === 'completed' && !this._startedAt) {
      throw new InvariantViolationError(
        'Completed task must have startedAt timestamp',
        'MISSING_STARTED_AT',
        { taskId: this._id.value }
      );
    }

    // completedAt не может быть раньше startedAt
    if (this._completedAt && this._startedAt && this._completedAt < this._startedAt) {
      throw new InvariantViolationError(
        'completedAt cannot be earlier than startedAt',
        'INVALID_TIMESTAMPS',
        { taskId: this._id.value }
      );
    }

    // Failed задачи должны иметь failureReason
    if (this._status === 'failed' && !this._failureReason) {
      throw new InvariantViolationError(
        'Failed task must have a failure reason',
        'MISSING_FAILURE_REASON',
        { taskId: this._id.value }
      );
    }

    // total и processed не могут быть отрицательными
    if (this._progress.total < 0 || this._progress.processed < 0) {
      throw new InvariantViolationError(
        'Progress values cannot be negative',
        'NEGATIVE_PROGRESS',
        { taskId: this._id.value }
      );
    }
  }

  // ============ Геттеры ============

  public get id(): TaskId {
    return this._id;
  }

  public get status(): TaskStatus {
    return this._status;
  }

  public get progress(): TProgress {
    return this._progress;
  }

  public get errors(): readonly string[] {
    return [...this._errors];
  }

  public get createdAt(): Date {
    return this._createdAt;
  }

  public get startedAt(): Date | null {
    return this._startedAt;
  }

  public get completedAt(): Date | null {
    return this._completedAt;
  }

  public get failureReason(): string | undefined {
    return this._failureReason;
  }

  // ============ Бизнес-методы ============

  /**
   * Запускает выполнение задачи
   *
   * @throws ValidationError если задача уже запущена
   */
  public start(): void {
    if (this._status !== 'pending') {
      throw new ValidationError(
        `Cannot start task in ${this._status} status`,
        { field: 'status', currentStatus: this._status }
      );
    }

    this._status = 'processing';
    this._startedAt = new Date();
  }

  /**
   * Обновляет прогресс задачи
   *
   * @param processed - количество обработанных элементов
   */
  public updateProgress(processed: number): void {
    if (processed < 0) {
      throw new ValidationError(
        'Processed count cannot be negative',
        { field: 'processed', value: processed }
      );
    }

    if (processed > this._progress.total) {
      throw new ValidationError(
        `Processed count (${processed}) cannot exceed total (${this._progress.total})`,
        { field: 'processed', value: processed, total: this._progress.total }
      );
    }

    this._progress = {
      ...this._progress,
      processed
    } as TProgress;
  }

  /**
   * Добавляет ошибку к задаче
   */
  public addError(error: string): void {
    if (!error || error.trim().length === 0) {
      return;
    }

    this._errors.push(error.trim());
  }

  /**
   * Завершает задачу успешно
   *
   * @throws ValidationError если задача не в processing статусе
   */
  public complete(): void {
    if (this._status !== 'processing') {
      throw new ValidationError(
        `Cannot complete task in ${this._status} status`,
        { field: 'status', currentStatus: this._status }
      );
    }

    this._status = 'completed';
    this._completedAt = new Date();
  }

  /**
   * Помечает задачу как проваленную
   *
   * @param reason - причина провала
   */
  public fail(reason: string): void {
    if (!reason || reason.trim().length === 0) {
      throw new ValidationError(
        'Failure reason cannot be empty',
        { field: 'failureReason' }
      );
    }

    this._status = 'failed';
    this._failureReason = reason.trim();
    this._completedAt = new Date();

    if (!this._startedAt) {
      this._startedAt = this._createdAt;
    }
  }

  // ============ Проверки состояния ============

  /**
   * Проверяет, ожидает ли задача выполнения
   */
  public isPending(): boolean {
    return this._status === 'pending';
  }

  /**
   * Проверяет, выполняется ли задача
   */
  public isProcessing(): boolean {
    return this._status === 'processing';
  }

  /**
   * Проверяет, завершена ли задача
   */
  public isCompleted(): boolean {
    return this._status === 'completed';
  }

  /**
   * Проверяет, провалена ли задача
   */
  public isFailed(): boolean {
    return this._status === 'failed';
  }

  /**
   * Проверяет, завершена ли задача (успешно или с ошибкой)
   */
  public isFinished(): boolean {
    return this._status === 'completed' || this._status === 'failed';
  }

  /**
   * Получает процент выполнения
   */
  public getProgressPercent(): number {
    if (this._progress.total === 0) {
      return 0;
    }

    return Math.round((this._progress.processed / this._progress.total) * 100);
  }

  /**
   * Получает длительность выполнения в миллисекундах
   */
  public getDuration(): number | null {
    if (!this._startedAt) {
      return null;
    }

    const endTime = this._completedAt || new Date();
    return endTime.getTime() - this._startedAt.getTime();
  }

  /**
   * Получает количество ошибок
   */
  public getErrorCount(): number {
    return this._errors.length;
  }

  /**
   * Проверяет, есть ли ошибки
   */
  public hasErrors(): boolean {
    return this._errors.length > 0;
  }

  // ============ Сравнение ============

  /**
   * Сравнивает две задачи по ID
   */
  public equals(other: Task): boolean {
    if (!(other instanceof Task)) {
      return false;
    }

    return this._id.equals(other._id);
  }

  // ============ Сериализация ============

  /**
   * Преобразует в plain object для хранилища
   */
  public toPersistence(): {
    taskId: string;
    status: TaskStatus;
    progress: TProgress;
    errors: string[];
    createdAt: Date;
    startedAt: Date | null;
    completedAt: Date | null;
    failureReason?: string;
  } {
    return {
      taskId: this._id.value,
      status: this._status,
      progress: this._progress,
      errors: [...this._errors],
      createdAt: this._createdAt,
      startedAt: this._startedAt,
      completedAt: this._completedAt,
      failureReason: this._failureReason
    };
  }

  /**
   * Преобразует в JSON для API
   */
  public toJSON(): object {
    return {
      id: this._id.value,
      status: this._status,
      progress: {
        ...this._progress,
        percent: this.getProgressPercent()
      },
      errors: [...this._errors],
      errorCount: this.getErrorCount(),
      createdAt: this._createdAt.toISOString(),
      startedAt: this._startedAt?.toISOString() || null,
      completedAt: this._completedAt?.toISOString() || null,
      duration: this.getDuration(),
      failureReason: this._failureReason
    };
  }
}
