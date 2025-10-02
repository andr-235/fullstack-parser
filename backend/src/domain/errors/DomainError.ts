/**
 * @fileoverview Domain Layer Errors
 *
 * Базовые классы ошибок для Domain Layer.
 * Используются для представления бизнес-правил и инвариантов.
 */

/**
 * Базовая доменная ошибка
 *
 * @description
 * Используется для представления нарушений бизнес-правил и инвариантов.
 * Все доменные ошибки должны наследоваться от этого класса.
 */
export class DomainError extends Error {
  public readonly code: string;
  public readonly details?: Record<string, any>;

  constructor(
    message: string,
    code: string = 'DOMAIN_ERROR',
    details?: Record<string, any>
  ) {
    super(message);
    this.name = 'DomainError';
    this.code = code;
    this.details = details;

    // Сохраняем правильный stack trace
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Ошибка валидации
 *
 * @description
 * Используется когда данные не соответствуют требованиям домена.
 */
export class ValidationError extends DomainError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

/**
 * Ошибка "Не найдено"
 *
 * @description
 * Используется когда сущность не найдена в репозитории.
 */
export class NotFoundError extends DomainError {
  constructor(entityName: string, identifier: string | number, details?: Record<string, any>) {
    super(
      `${entityName} with identifier "${identifier}" not found`,
      'NOT_FOUND',
      { entityName, identifier, ...details }
    );
    this.name = 'NotFoundError';
  }
}

/**
 * Ошибка бизнес-логики
 *
 * @description
 * Используется когда операция нарушает бизнес-правила.
 */
export class BusinessRuleError extends DomainError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'BUSINESS_RULE_VIOLATION', details);
    this.name = 'BusinessRuleError';
  }
}

/**
 * Ошибка конфликта
 *
 * @description
 * Используется когда операция конфликтует с текущим состоянием.
 */
export class ConflictError extends DomainError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, 'CONFLICT', details);
    this.name = 'ConflictError';
  }
}

/**
 * Ошибка нарушения инварианта
 *
 * @description
 * Используется когда нарушается инвариант сущности или агрегата.
 * Инварианты - это правила, которые всегда должны быть истинны.
 */
export class InvariantViolationError extends DomainError {
  constructor(message: string, code?: string, details?: Record<string, any>) {
    super(message, code || 'INVARIANT_VIOLATION', details);
    this.name = 'InvariantViolationError';
  }
}
