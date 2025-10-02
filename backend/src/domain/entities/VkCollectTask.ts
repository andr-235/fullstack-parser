/**
 * @fileoverview VkCollectTask Entity - задача сбора данных из VK
 *
 * Специализированная задача для сбора комментариев, постов и другой информации из VK.
 */

import { Task, TaskProgress, CreateTaskProps } from './Task';
import { TaskId } from '@domain/value-objects/TaskId';
import { ValidationError } from '@domain/errors/DomainError';

/**
 * Прогресс сбора данных VK
 */
export interface VkCollectProgress extends TaskProgress {
  readonly total: number;
  readonly processed: number;
  readonly successful: number;
  readonly failed: number;
  readonly currentBatch?: number;
  readonly totalBatches?: number;
}

/**
 * Параметры для создания VkCollectTask
 */
export interface CreateVkCollectTaskProps extends CreateTaskProps<VkCollectProgress> {
  readonly collectType?: 'comments' | 'posts' | 'groups' | 'members';
  readonly targetId?: string; // ID поста, группы и т.д.
  readonly batchSize?: number;
}

/**
 * VkCollectTask Entity - задача сбора данных из VK
 *
 * @description
 * Расширяет базовый Task логикой для сбора данных из VK API.
 * Отслеживает успешные и проваленные запросы, батчи.
 *
 * Дополнительные инварианты:
 * - successful + failed должно быть <= processed
 * - currentBatch <= totalBatches
 *
 * @example
 * ```typescript
 * const task = VkCollectTask.createNew({
 *   total: 1000,
 *   collectType: 'comments',
 *   targetId: '-123456_789',
 *   batchSize: 100
 * });
 *
 * task.start();
 * task.startBatch(1);
 * task.incrementSuccessful(50);
 * task.incrementFailed(5);
 * task.complete();
 * ```
 */
export class VkCollectTask extends Task<VkCollectProgress> {
  private _collectType?: 'comments' | 'posts' | 'groups' | 'members';
  private _targetId?: string;
  private _batchSize?: number;

  private constructor(props: CreateVkCollectTaskProps) {
    super(props);
    this._collectType = props.collectType;
    this._targetId = props.targetId;
    this._batchSize = props.batchSize;
  }

  /**
   * Создает новую задачу сбора данных VK
   */
  public static createNew(params: {
    total: number;
    collectType?: 'comments' | 'posts' | 'groups' | 'members';
    targetId?: string;
    batchSize?: number;
  }): VkCollectTask {
    const totalBatches = params.batchSize
      ? Math.ceil(params.total / params.batchSize)
      : undefined;

    return new VkCollectTask({
      status: 'pending',
      progress: {
        total: params.total,
        processed: 0,
        successful: 0,
        failed: 0,
        currentBatch: 0,
        totalBatches
      },
      errors: [],
      collectType: params.collectType,
      targetId: params.targetId,
      batchSize: params.batchSize
    });
  }

  /**
   * Восстанавливает задачу из хранилища (переопределение для типа)
   */
  public static restoreVkCollectTask(
    props: CreateVkCollectTaskProps & { id: TaskId }
  ): VkCollectTask {
    return new VkCollectTask(props);
  }

  /**
   * Дополнительная валидация для VkCollectTask
   */
  protected validate(): void {
    super.validate();

    const { successful, failed, processed, currentBatch, totalBatches } = this._progress;

    // Сумма successful + failed не должна превышать processed
    const resultsSum = successful + failed;
    if (resultsSum > processed) {
      throw new ValidationError(
        `Sum of results (${resultsSum}) cannot exceed processed count (${processed})`,
        { field: 'progress', resultsSum, processed }
      );
    }

    // currentBatch не может быть больше totalBatches
    if (currentBatch !== undefined && totalBatches !== undefined && currentBatch > totalBatches) {
      throw new ValidationError(
        `Current batch (${currentBatch}) cannot exceed total batches (${totalBatches})`,
        { field: 'progress', currentBatch, totalBatches }
      );
    }

    // Все счетчики должны быть неотрицательными
    if (successful < 0 || failed < 0) {
      throw new ValidationError(
        'Progress counters cannot be negative',
        { field: 'progress', successful, failed }
      );
    }
  }

  // ============ Геттеры ============

  public get collectType(): string | undefined {
    return this._collectType;
  }

  public get targetId(): string | undefined {
    return this._targetId;
  }

  public get batchSize(): number | undefined {
    return this._batchSize;
  }

  public get successfulCount(): number {
    return this._progress.successful;
  }

  public get failedCount(): number {
    return this._progress.failed;
  }

  public get currentBatch(): number | undefined {
    return this._progress.currentBatch;
  }

  public get totalBatches(): number | undefined {
    return this._progress.totalBatches;
  }

  // ============ Специфичные методы ============

  /**
   * Увеличивает счетчик успешных операций
   */
  public incrementSuccessful(count: number = 1): void {
    if (count < 0) {
      throw new ValidationError('Count cannot be negative', { field: 'count', value: count });
    }

    this._progress = {
      ...this._progress,
      successful: this._progress.successful + count,
      processed: this._progress.processed + count
    };

    this.validate();
  }

  /**
   * Увеличивает счетчик проваленных операций
   */
  public incrementFailed(count: number = 1): void {
    if (count < 0) {
      throw new ValidationError('Count cannot be negative', { field: 'count', value: count });
    }

    this._progress = {
      ...this._progress,
      failed: this._progress.failed + count,
      processed: this._progress.processed + count
    };

    this.validate();
  }

  /**
   * Начинает обработку нового батча
   */
  public startBatch(batchNumber: number): void {
    if (batchNumber < 1) {
      throw new ValidationError(
        'Batch number must be positive',
        { field: 'batchNumber', value: batchNumber }
      );
    }

    if (this._progress.totalBatches && batchNumber > this._progress.totalBatches) {
      throw new ValidationError(
        `Batch number (${batchNumber}) exceeds total batches (${this._progress.totalBatches})`,
        { field: 'batchNumber', value: batchNumber, totalBatches: this._progress.totalBatches }
      );
    }

    this._progress = {
      ...this._progress,
      currentBatch: batchNumber
    };
  }

  /**
   * Обновляет прогресс пакетом
   */
  public updateBatchProgress(params: {
    successful?: number;
    failed?: number;
  }): void {
    const successfulDelta = params.successful || 0;
    const failedDelta = params.failed || 0;

    this._progress = {
      ...this._progress,
      successful: this._progress.successful + successfulDelta,
      failed: this._progress.failed + failedDelta,
      processed: this._progress.processed + successfulDelta + failedDelta
    };

    this.validate();
  }

  /**
   * Устанавливает общее количество для сбора
   */
  public setTotal(total: number): void {
    if (total < 0) {
      throw new ValidationError('Total cannot be negative', { field: 'total', value: total });
    }

    if (total < this._progress.processed) {
      throw new ValidationError(
        `Total (${total}) cannot be less than processed (${this._progress.processed})`,
        { field: 'total', value: total, processed: this._progress.processed }
      );
    }

    // Пересчитываем количество батчей если задан batchSize
    const totalBatches = this._batchSize
      ? Math.ceil(total / this._batchSize)
      : this._progress.totalBatches;

    this._progress = {
      ...this._progress,
      total,
      totalBatches
    };
  }

  // ============ Проверки ============

  /**
   * Проверяет, все ли элементы обработаны
   */
  public isFullyProcessed(): boolean {
    return this._progress.processed === this._progress.total;
  }

  /**
   * Проверяет, были ли успешные операции
   */
  public hasSuccessful(): boolean {
    return this._progress.successful > 0;
  }

  /**
   * Проверяет, были ли провалы
   */
  public hasFailed(): boolean {
    return this._progress.failed > 0;
  }

  /**
   * Проверяет, все ли батчи обработаны
   */
  public allBatchesProcessed(): boolean {
    if (!this._progress.currentBatch || !this._progress.totalBatches) {
      return false;
    }

    return this._progress.currentBatch >= this._progress.totalBatches;
  }

  /**
   * Получает процент успешных операций
   */
  public getSuccessRate(): number {
    if (this._progress.processed === 0) {
      return 0;
    }

    return Math.round((this._progress.successful / this._progress.processed) * 100);
  }

  /**
   * Получает процент неудач
   */
  public getFailureRate(): number {
    if (this._progress.processed === 0) {
      return 0;
    }

    return Math.round((this._progress.failed / this._progress.processed) * 100);
  }

  /**
   * Получает прогресс батчей в процентах
   */
  public getBatchProgress(): number {
    if (!this._progress.currentBatch || !this._progress.totalBatches) {
      return 0;
    }

    return Math.round((this._progress.currentBatch / this._progress.totalBatches) * 100);
  }

  /**
   * Получает статистику в человекочитаемом виде
   */
  public getStatsSummary(): string {
    const { total, processed, successful, failed } = this._progress;
    const batchInfo = this._progress.totalBatches
      ? ` (batch ${this._progress.currentBatch}/${this._progress.totalBatches})`
      : '';

    return `Processed ${processed}/${total}${batchInfo}: ${successful} successful, ${failed} failed`;
  }

  // ============ Сериализация ============

  /**
   * Преобразует в JSON с дополнительными полями
   */
  public toJSON(): object {
    return {
      ...super.toJSON(),
      collectType: this._collectType,
      targetId: this._targetId,
      batchSize: this._batchSize,
      statistics: {
        successRate: this.getSuccessRate(),
        failureRate: this.getFailureRate(),
        batchProgress: this.getBatchProgress(),
        summary: this.getStatsSummary()
      }
    };
  }
}
