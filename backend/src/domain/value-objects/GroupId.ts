/**
 * @fileoverview GroupId Value Object
 *
 * Value Object для внутреннего идентификатора группы в системе.
 * Отличается от VkId - это ID в нашей базе данных, а не VK ID.
 */

import { DomainError } from '@domain/errors/DomainError';

/**
 * Value Object для внутреннего ID группы
 *
 * @description
 * Представляет уникальный идентификатор группы в нашей системе (PostgreSQL).
 * Автоинкрементный ID из таблицы groups.
 *
 * @example
 * ```typescript
 * const id = GroupId.create(42);
 * console.log(id.value); // 42
 * ```
 */
export class GroupId {
  private readonly _value: number;

  private constructor(value: number) {
    this._value = value;
  }

  /**
   * Создает GroupId из числа
   *
   * @param value - ID группы (положительное целое число)
   * @throws DomainError если ID невалиден
   */
  public static create(value: number): GroupId {
    if (!GroupId.isValid(value)) {
      throw new DomainError(
        `Invalid Group ID: ${value}. Must be a positive integer.`,
        'INVALID_GROUP_ID'
      );
    }

    return new GroupId(value);
  }

  /**
   * Создает GroupId из строки
   */
  public static fromString(value: string): GroupId {
    const parsed = parseInt(value, 10);

    if (isNaN(parsed)) {
      throw new DomainError(
        `Invalid Group ID string: "${value}". Must be a valid integer.`,
        'INVALID_GROUP_ID_STRING'
      );
    }

    return GroupId.create(parsed);
  }

  /**
   * Проверяет валидность Group ID
   */
  public static isValid(value: number): boolean {
    return Number.isInteger(value) && value > 0;
  }

  /**
   * Получает числовое значение ID
   */
  public get value(): number {
    return this._value;
  }

  /**
   * Сравнивает два GroupId
   */
  public equals(other: GroupId): boolean {
    if (!(other instanceof GroupId)) {
      return false;
    }

    return this._value === other._value;
  }

  /**
   * Возвращает строковое представление
   */
  public toString(): string {
    return this._value.toString();
  }

  /**
   * Возвращает JSON представление
   */
  public toJSON(): number {
    return this._value;
  }
}
