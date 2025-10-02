/**
 * @fileoverview TaskId Value Object
 *
 * Value Object для идентификатора задачи (обычно UUID v4).
 */

import { DomainError } from '@domain/errors/DomainError';

/**
 * Value Object для ID задачи
 *
 * @description
 * Представляет уникальный идентификатор задачи в системе.
 * Обычно UUID v4 формата.
 *
 * @example
 * ```typescript
 * const id = TaskId.create('550e8400-e29b-41d4-a716-446655440000');
 * console.log(id.value); // '550e8400-e29b-41d4-a716-446655440000'
 * ```
 */
export class TaskId {
  private readonly _value: string;

  // UUID v4 regex pattern
  private static readonly UUID_V4_PATTERN =
    /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

  private constructor(value: string) {
    this._value = value;
  }

  /**
   * Создает TaskId из строки
   *
   * @param value - UUID v4 строка
   * @throws DomainError если ID невалиден
   */
  public static create(value: string): TaskId {
    if (!TaskId.isValid(value)) {
      throw new DomainError(
        `Invalid Task ID: "${value}". Must be a valid UUID v4.`,
        'INVALID_TASK_ID'
      );
    }

    return new TaskId(value.toLowerCase());
  }

  /**
   * Создает новый случайный TaskId
   * Использует crypto.randomUUID() если доступен, иначе fallback
   */
  public static generate(): TaskId {
    // В Node.js 14.17+ доступен crypto.randomUUID()
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return new TaskId(crypto.randomUUID());
    }

    // Fallback для старых версий Node.js
    return TaskId.generateV4();
  }

  /**
   * Генерирует UUID v4 вручную (fallback)
   */
  private static generateV4(): TaskId {
    const hex = '0123456789abcdef';
    let uuid = '';

    for (let i = 0; i < 36; i++) {
      if (i === 8 || i === 13 || i === 18 || i === 23) {
        uuid += '-';
      } else if (i === 14) {
        uuid += '4'; // Версия 4
      } else if (i === 19) {
        uuid += hex[(Math.random() * 4) | 8]; // Вариант RFC4122
      } else {
        uuid += hex[(Math.random() * 16) | 0];
      }
    }

    return new TaskId(uuid);
  }

  /**
   * Проверяет валидность Task ID (UUID v4)
   */
  public static isValid(value: string): boolean {
    if (typeof value !== 'string') {
      return false;
    }

    return TaskId.UUID_V4_PATTERN.test(value);
  }

  /**
   * Получает строковое значение ID
   */
  public get value(): string {
    return this._value;
  }

  /**
   * Сравнивает два TaskId
   */
  public equals(other: TaskId): boolean {
    if (!(other instanceof TaskId)) {
      return false;
    }

    return this._value === other._value;
  }

  /**
   * Возвращает строковое представление
   */
  public toString(): string {
    return this._value;
  }

  /**
   * Возвращает JSON представление
   */
  public toJSON(): string {
    return this._value;
  }

  /**
   * Возвращает короткую версию ID (первые 8 символов)
   * Полезно для логирования
   */
  public toShort(): string {
    return this._value.substring(0, 8);
  }
}
