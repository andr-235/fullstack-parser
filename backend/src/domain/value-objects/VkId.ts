/**
 * @fileoverview VkId Value Object
 *
 * Value Object для идентификатора VK группы или пользователя.
 * Инкапсулирует валидацию и бизнес-правила для VK ID.
 *
 * ПРИНЦИПЫ VALUE OBJECT:
 * - Неизменяемый (immutable)
 * - Сравнивается по значению, а не по ссылке
 * - Валидация в конструкторе
 * - Не имеет идентификатора
 */

import { DomainError } from '@domain/errors/DomainError';

/**
 * Value Object для VK ID
 *
 * @description
 * Представляет идентификатор объекта ВКонтакте (группа, пользователь и т.д.)
 * Гарантирует, что ID всегда валиден и соответствует правилам VK.
 *
 * Правила VK ID:
 * - Целое число
 * - Положительное значение для пользователей и групп
 * - Диапазон: 1 до 999,999,999 (менее миллиарда)
 *
 * @example
 * ```typescript
 * const groupId = VkId.create(123456);
 * console.log(groupId.value); // 123456
 * console.log(groupId.toString()); // "123456"
 *
 * // Создание с отрицательным ID для группы
 * const groupIdNegative = VkId.create(-123456);
 * console.log(groupIdNegative.toPositive()); // 123456
 * ```
 */
export class VkId {
  private readonly _value: number;

  private constructor(value: number) {
    this._value = value;
  }

  /**
   * Создает VkId из числа
   *
   * @param value - VK ID (положительное или отрицательное число)
   * @throws DomainError если ID невалиден
   */
  public static create(value: number): VkId {
    if (!VkId.isValid(value)) {
      throw new DomainError(
        `Invalid VK ID: ${value}. Must be a non-zero integer within valid VK range.`,
        'INVALID_VK_ID'
      );
    }

    return new VkId(value);
  }

  /**
   * Создает VkId из строки
   *
   * @param value - строковое представление ID
   * @throws DomainError если строка не может быть преобразована в валидный ID
   */
  public static fromString(value: string): VkId {
    const parsed = parseInt(value, 10);

    if (isNaN(parsed)) {
      throw new DomainError(
        `Invalid VK ID string: "${value}". Must be a valid integer.`,
        'INVALID_VK_ID_STRING'
      );
    }

    return VkId.create(parsed);
  }

  /**
   * Проверяет валидность VK ID
   *
   * @param value - значение для проверки
   * @returns true если ID валиден
   */
  public static isValid(value: number): boolean {
    return (
      Number.isInteger(value) &&
      value !== 0 &&
      Math.abs(value) > 0 &&
      Math.abs(value) < 1_000_000_000 // VK ID меньше миллиарда
    );
  }

  /**
   * Получает числовое значение ID
   */
  public get value(): number {
    return this._value;
  }

  /**
   * Возвращает положительное значение ID
   * Полезно для групп, которые могут иметь отрицательный ID в API
   */
  public toPositive(): number {
    return Math.abs(this._value);
  }

  /**
   * Возвращает отрицательное значение ID
   * Используется для некоторых методов VK API
   */
  public toNegative(): number {
    return -Math.abs(this._value);
  }

  /**
   * Проверяет, является ли ID отрицательным
   */
  public isNegative(): boolean {
    return this._value < 0;
  }

  /**
   * Проверяет, является ли ID положительным
   */
  public isPositive(): boolean {
    return this._value > 0;
  }

  /**
   * Сравнивает два VkId
   *
   * @param other - другой VkId для сравнения
   * @returns true если ID равны по абсолютному значению
   */
  public equals(other: VkId): boolean {
    if (!(other instanceof VkId)) {
      return false;
    }

    return this.toPositive() === other.toPositive();
  }

  /**
   * Строгое сравнение с учетом знака
   */
  public strictEquals(other: VkId): boolean {
    if (!(other instanceof VkId)) {
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

  /**
   * Создает копию с положительным значением
   */
  public asPositive(): VkId {
    return VkId.create(this.toPositive());
  }

  /**
   * Создает копию с отрицательным значением
   */
  public asNegative(): VkId {
    return VkId.create(this.toNegative());
  }
}
