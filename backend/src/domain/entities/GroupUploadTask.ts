/**
 * @fileoverview GroupUploadTask Entity - задача загрузки групп
 *
 * Специализированная задача для процесса загрузки и валидации групп из файла.
 */

import { Task, TaskProgress, CreateTaskProps } from './Task';
import { TaskId } from '@domain/value-objects/TaskId';
import { ValidationError } from '@domain/errors/DomainError';

/**
 * Прогресс загрузки групп
 */
export interface GroupUploadProgress extends TaskProgress {
  readonly total: number;
  readonly processed: number;
  readonly valid: number;
  readonly invalid: number;
  readonly duplicates: number;
}

/**
 * Параметры для создания GroupUploadTask
 */
export interface CreateGroupUploadTaskProps extends CreateTaskProps<GroupUploadProgress> {
  readonly fileName?: string;
  readonly fileSize?: number;
}

/**
 * GroupUploadTask Entity - задача загрузки групп
 *
 * @description
 * Расширяет базовый Task специфичной логикой для загрузки групп.
 * Отслеживает валидные, невалидные группы и дубликаты.
 *
 * Дополнительные инварианты:
 * - valid + invalid + duplicates должно быть <= processed
 * - processed <= total
 *
 * @example
 * ```typescript
 * const task = GroupUploadTask.createNew({
 *   total: 100,
 *   fileName: 'groups.txt',
 *   fileSize: 1024
 * });
 *
 * task.start();
 * task.incrementValid();
 * task.incrementInvalid();
 * task.complete();
 * ```
 */
export class GroupUploadTask extends Task<GroupUploadProgress> {
  private _fileName?: string;
  private _fileSize?: number;

  private constructor(props: CreateGroupUploadTaskProps) {
    super(props);
    this._fileName = props.fileName;
    this._fileSize = props.fileSize;
  }

  /**
   * Создает новую задачу загрузки групп
   */
  public static createNew(params: {
    total: number;
    fileName?: string;
    fileSize?: number;
  }): GroupUploadTask {
    return new GroupUploadTask({
      status: 'pending',
      progress: {
        total: params.total,
        processed: 0,
        valid: 0,
        invalid: 0,
        duplicates: 0
      },
      errors: [],
      fileName: params.fileName,
      fileSize: params.fileSize
    });
  }

  /**
   * Восстанавливает задачу из хранилища (переопределение для типа)
   */
  public static restoreGroupUploadTask(
    props: CreateGroupUploadTaskProps & { id: TaskId }
  ): GroupUploadTask {
    return new GroupUploadTask(props);
  }

  /**
   * Дополнительная валидация для GroupUploadTask
   */
  protected validate(): void {
    super.validate();

    const { valid, invalid, duplicates, processed } = this._progress;

    // Сумма категорий не должна превышать обработанные
    const categoriesSum = valid + invalid + duplicates;
    if (categoriesSum > processed) {
      throw new ValidationError(
        `Sum of categories (${categoriesSum}) cannot exceed processed count (${processed})`,
        { field: 'progress', categoriesSum, processed }
      );
    }

    // Все счетчики должны быть неотрицательными
    if (valid < 0 || invalid < 0 || duplicates < 0) {
      throw new ValidationError(
        'Progress counters cannot be negative',
        { field: 'progress', valid, invalid, duplicates }
      );
    }
  }

  // ============ Геттеры ============

  public get fileName(): string | undefined {
    return this._fileName;
  }

  public get fileSize(): number | undefined {
    return this._fileSize;
  }

  public get validCount(): number {
    return this._progress.valid;
  }

  public get invalidCount(): number {
    return this._progress.invalid;
  }

  public get duplicatesCount(): number {
    return this._progress.duplicates;
  }

  // ============ Специфичные методы ============

  /**
   * Увеличивает счетчик валидных групп
   */
  public incrementValid(): void {
    this._progress = {
      ...this._progress,
      valid: this._progress.valid + 1,
      processed: this._progress.processed + 1
    };

    this.validate();
  }

  /**
   * Увеличивает счетчик невалидных групп
   */
  public incrementInvalid(): void {
    this._progress = {
      ...this._progress,
      invalid: this._progress.invalid + 1,
      processed: this._progress.processed + 1
    };

    this.validate();
  }

  /**
   * Увеличивает счетчик дубликатов
   */
  public incrementDuplicate(): void {
    this._progress = {
      ...this._progress,
      duplicates: this._progress.duplicates + 1,
      processed: this._progress.processed + 1
    };

    this.validate();
  }

  /**
   * Обновляет прогресс пакетом
   */
  public updateBatchProgress(params: {
    valid?: number;
    invalid?: number;
    duplicates?: number;
  }): void {
    const validDelta = params.valid || 0;
    const invalidDelta = params.invalid || 0;
    const duplicatesDelta = params.duplicates || 0;

    this._progress = {
      ...this._progress,
      valid: this._progress.valid + validDelta,
      invalid: this._progress.invalid + invalidDelta,
      duplicates: this._progress.duplicates + duplicatesDelta,
      processed: this._progress.processed + validDelta + invalidDelta + duplicatesDelta
    };

    this.validate();
  }

  /**
   * Устанавливает общее количество для обработки
   */
  public setTotal(total: number): void {
    if (total < 0) {
      throw new ValidationError(
        'Total cannot be negative',
        { field: 'total', value: total }
      );
    }

    if (total < this._progress.processed) {
      throw new ValidationError(
        `Total (${total}) cannot be less than processed (${this._progress.processed})`,
        { field: 'total', value: total, processed: this._progress.processed }
      );
    }

    this._progress = {
      ...this._progress,
      total
    };
  }

  // ============ Проверки ============

  /**
   * Проверяет, все ли группы обработаны
   */
  public isFullyProcessed(): boolean {
    return this._progress.processed === this._progress.total;
  }

  /**
   * Проверяет, были ли найдены валидные группы
   */
  public hasValidGroups(): boolean {
    return this._progress.valid > 0;
  }

  /**
   * Проверяет, были ли ошибки при обработке
   */
  public hasInvalidGroups(): boolean {
    return this._progress.invalid > 0;
  }

  /**
   * Проверяет, были ли найдены дубликаты
   */
  public hasDuplicates(): boolean {
    return this._progress.duplicates > 0;
  }

  /**
   * Получает процент валидных групп от общего числа
   */
  public getValidPercent(): number {
    if (this._progress.total === 0) {
      return 0;
    }

    return Math.round((this._progress.valid / this._progress.total) * 100);
  }

  /**
   * Получает процент невалидных групп
   */
  public getInvalidPercent(): number {
    if (this._progress.total === 0) {
      return 0;
    }

    return Math.round((this._progress.invalid / this._progress.total) * 100);
  }

  /**
   * Получает процент дубликатов
   */
  public getDuplicatesPercent(): number {
    if (this._progress.total === 0) {
      return 0;
    }

    return Math.round((this._progress.duplicates / this._progress.total) * 100);
  }

  /**
   * Получает статистику в человекочитаемом виде
   */
  public getStatsSummary(): string {
    const { total, processed, valid, invalid, duplicates } = this._progress;
    return `Processed ${processed}/${total} groups: ${valid} valid, ${invalid} invalid, ${duplicates} duplicates`;
  }

  // ============ Сериализация ============

  /**
   * Преобразует в JSON с дополнительными полями
   */
  public toJSON(): object {
    return {
      ...super.toJSON(),
      fileName: this._fileName,
      fileSize: this._fileSize,
      statistics: {
        validPercent: this.getValidPercent(),
        invalidPercent: this.getInvalidPercent(),
        duplicatesPercent: this.getDuplicatesPercent(),
        summary: this.getStatsSummary()
      }
    };
  }
}
