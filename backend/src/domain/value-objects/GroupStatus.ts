/**
 * @fileoverview GroupStatus Value Object
 *
 * Value Object для статуса группы.
 * Обертка над Prisma enum для добавления domain логики.
 */

import { GroupStatus as PrismaGroupStatus } from '@prisma/client';
import { DomainError } from '@domain/errors/DomainError';

/**
 * Value Object для статуса группы
 *
 * @description
 * Представляет статус группы в системе с валидацией и бизнес-логикой.
 * Использует Prisma enum как основу, но добавляет domain методы.
 *
 * Возможные статусы:
 * - valid: группа валидна и доступна
 * - invalid: группа не найдена или недоступна через VK API
 * - duplicate: группа уже существует в системе
 *
 * @example
 * ```typescript
 * const status = GroupStatus.create('valid');
 * console.log(status.isValid()); // true
 * console.log(status.canBeProcessed()); // true
 * ```
 */
export class GroupStatus {
  private readonly _value: PrismaGroupStatus;

  private constructor(value: PrismaGroupStatus) {
    this._value = value;
  }

  /**
   * Создает GroupStatus из строки
   *
   * @param value - статус ('valid', 'invalid', 'duplicate')
   * @throws DomainError если статус невалиден
   */
  public static create(value: string): GroupStatus {
    if (!GroupStatus.isValid(value)) {
      throw new DomainError(
        `Invalid GroupStatus: "${value}". Must be one of: valid, invalid, duplicate.`,
        'INVALID_GROUP_STATUS'
      );
    }

    return new GroupStatus(value as PrismaGroupStatus);
  }

  /**
   * Создает GroupStatus из Prisma enum
   */
  public static fromPrisma(value: PrismaGroupStatus): GroupStatus {
    return new GroupStatus(value);
  }

  /**
   * Создает статус "valid"
   */
  public static valid(): GroupStatus {
    return new GroupStatus('valid');
  }

  /**
   * Создает статус "invalid"
   */
  public static invalid(): GroupStatus {
    return new GroupStatus('invalid');
  }

  /**
   * Создает статус "duplicate"
   */
  public static duplicate(): GroupStatus {
    return new GroupStatus('duplicate');
  }

  /**
   * Проверяет валидность статуса
   */
  public static isValid(value: string): value is PrismaGroupStatus {
    return ['valid', 'invalid', 'duplicate'].includes(value);
  }

  /**
   * Получает значение статуса
   */
  public get value(): PrismaGroupStatus {
    return this._value;
  }

  /**
   * Проверяет, является ли группа валидной
   */
  public isValid(): boolean {
    return this._value === 'valid';
  }

  /**
   * Проверяет, является ли группа невалидной
   */
  public isInvalid(): boolean {
    return this._value === 'invalid';
  }

  /**
   * Проверяет, является ли группа дубликатом
   */
  public isDuplicate(): boolean {
    return this._value === 'duplicate';
  }

  /**
   * Проверяет, можно ли обрабатывать группу
   * (только валидные группы могут быть обработаны)
   */
  public canBeProcessed(): boolean {
    return this.isValid();
  }

  /**
   * Проверяет, нужно ли исключить группу из обработки
   */
  public shouldBeExcluded(): boolean {
    return this.isInvalid() || this.isDuplicate();
  }

  /**
   * Получает человекочитаемое описание статуса
   */
  public getDescription(): string {
    switch (this._value) {
      case 'valid':
        return 'Группа валидна и доступна';
      case 'invalid':
        return 'Группа не найдена или недоступна';
      case 'duplicate':
        return 'Группа уже существует в системе';
      default:
        return 'Неизвестный статус';
    }
  }

  /**
   * Сравнивает два GroupStatus
   */
  public equals(other: GroupStatus): boolean {
    if (!(other instanceof GroupStatus)) {
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
   * Преобразует в Prisma enum
   */
  public toPrisma(): PrismaGroupStatus {
    return this._value;
  }
}
