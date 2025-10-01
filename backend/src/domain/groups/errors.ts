/**
 * @fileoverview Custom error classes для Groups domain
 *
 * Все ошибки наследуются от GroupsDomainError
 * Каждая ошибка имеет:
 * - code: Уникальный код для API responses
 * - statusCode: HTTP статус код
 * - details: Дополнительные данные для debugging и logging
 *
 * @example
 * ```typescript
 * throw new DuplicateGroupError(12345);
 * // -> HTTP 409, code: 'DUPLICATE_GROUP', details: { vkId: 12345 }
 * ```
 */

// import { CustomError } from 'ts-custom-error'; // ESM incompatible

/**
 * Base error для Groups domain
 * Все domain-специфичные ошибки наследуются от этого класса
 */
export abstract class GroupsDomainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = this.constructor.name;

    // Для корректного instanceof в TypeScript при transpilation
    Object.setPrototypeOf(this, new.target.prototype);
  }

  /**
   * Сериализация для API response
   */
  toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
    };
  }

  /**
   * Проверка, является ли ошибка клиентской (4xx)
   */
  isClientError(): boolean {
    return this.statusCode >= 400 && this.statusCode < 500;
  }

  /**
   * Проверка, является ли ошибка серверной (5xx)
   */
  isServerError(): boolean {
    return this.statusCode >= 500;
  }

  /**
   * Форматирование для логирования
   */
  toLogFormat(): Record<string, unknown> {
    return {
      errorType: this.name,
      code: this.code,
      message: this.message,
      statusCode: this.statusCode,
      details: this.details,
      stack: this.stack,
    };
  }
}

// ============ Client Errors (4xx) ============

/**
 * Ошибка валидации входных данных
 * HTTP 400 Bad Request
 *
 * @example
 * throw new ValidationError('Invalid file format', 'FILE_FORMAT_ERROR', 400, {
 *   expected: '.txt',
 *   received: '.pdf'
 * });
 */
export class ValidationError extends GroupsDomainError {
  constructor(
    message: string,
    code: string = 'VALIDATION_ERROR',
    statusCode: number = 400,
    details?: Record<string, unknown>
  ) {
    super(message, code, statusCode, details);
  }
}

/**
 * Группа с таким VK ID уже существует в БД
 * HTTP 409 Conflict
 */
export class DuplicateGroupError extends GroupsDomainError {
  constructor(vkId: number) {
    super(
      `Group with VK ID ${vkId} already exists in database`,
      'DUPLICATE_GROUP',
      409,
      { vkId }
    );
  }
}

/**
 * Группа не найдена в БД
 * HTTP 404 Not Found
 */
export class GroupNotFoundError extends GroupsDomainError {
  constructor(identifier: number | string) {
    super(
      `Group not found: ${identifier}`,
      'GROUP_NOT_FOUND',
      404,
      { identifier, identifierType: typeof identifier }
    );
  }
}

/**
 * Задача загрузки не найдена в Redis
 * HTTP 404 Not Found
 */
export class TaskNotFoundError extends GroupsDomainError {
  constructor(taskId: string) {
    super(
      `Upload task not found: ${taskId}`,
      'TASK_NOT_FOUND',
      404,
      { taskId }
    );
  }
}

/**
 * Невалидный формат файла
 * HTTP 422 Unprocessable Entity
 */
export class InvalidFileFormatError extends GroupsDomainError {
  constructor(reason: string, details?: Record<string, unknown>) {
    super(
      `Invalid file format: ${reason}`,
      'INVALID_FILE_FORMAT',
      422,
      details
    );
  }
}

/**
 * Файл превышает допустимый размер
 * HTTP 413 Payload Too Large
 */
export class FileSizeLimitError extends GroupsDomainError {
  constructor(actualSize: number, maxSize: number) {
    super(
      `File size ${actualSize} bytes exceeds maximum ${maxSize} bytes`,
      'FILE_TOO_LARGE',
      413,
      { actualSize, maxSize, maxSizeMB: maxSize / (1024 * 1024) }
    );
  }
}

/**
 * Недопустимая операция над группой
 * HTTP 403 Forbidden
 */
export class ForbiddenOperationError extends GroupsDomainError {
  constructor(operation: string, reason: string) {
    super(
      `Operation '${operation}' is forbidden: ${reason}`,
      'FORBIDDEN_OPERATION',
      403,
      { operation, reason }
    );
  }
}

// ============ External Service Errors (5xx) ============

/**
 * Ошибка VK API
 * HTTP 502 Bad Gateway
 */
export class VkApiError extends GroupsDomainError {
  constructor(
    message: string,
    public readonly vkErrorCode?: number,
    details?: Record<string, unknown>
  ) {
    super(
      message,
      'VK_API_ERROR',
      502,
      { vkErrorCode, ...details }
    );
  }

  /**
   * Проверка на rate limit error
   * VK error code 6 = Too many requests
   */
  isRateLimitError(): boolean {
    return this.vkErrorCode === 6;
  }

  /**
   * Проверка на access denied
   * VK error code 15 = Access denied
   */
  isAccessDeniedError(): boolean {
    return this.vkErrorCode === 15;
  }

  /**
   * Проверка на captcha required
   * VK error code 14 = Captcha needed
   */
  isCaptchaError(): boolean {
    return this.vkErrorCode === 14;
  }

  /**
   * Проверка на invalid token
   * VK error code 5 = User authorization failed
   */
  isAuthError(): boolean {
    return this.vkErrorCode === 5;
  }

  /**
   * Получить рекомендуемую задержку перед retry
   */
  getRetryDelay(): number {
    if (this.isRateLimitError()) {
      return 60000; // 1 минута для rate limit
    }
    if (this.isAccessDeniedError()) {
      return 0; // Не ретраить access denied
    }
    return 5000; // 5 секунд по умолчанию
  }

  /**
   * Проверка, можно ли повторить запрос
   */
  isRetryable(): boolean {
    return !this.isAccessDeniedError() && !this.isAuthError() && !this.isCaptchaError();
  }
}

/**
 * Ошибка обработки файла
 * HTTP 422 Unprocessable Entity
 */
export class FileProcessingError extends GroupsDomainError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(
      message,
      'FILE_PROCESSING_ERROR',
      422,
      details
    );
  }
}

/**
 * Ошибка парсинга файла
 * HTTP 422 Unprocessable Entity
 */
export class FileParsingError extends GroupsDomainError {
  constructor(
    message: string,
    public readonly lineNumber?: number,
    public readonly lineContent?: string
  ) {
    super(
      message,
      'FILE_PARSING_ERROR',
      422,
      { lineNumber, lineContent }
    );
  }
}

// ============ Infrastructure Errors (5xx) ============

/**
 * Ошибка Redis storage
 * HTTP 500 Internal Server Error
 */
export class TaskStorageError extends GroupsDomainError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(
      message,
      'TASK_STORAGE_ERROR',
      500,
      details
    );
  }
}

/**
 * Ошибка при работе с БД (PostgreSQL + Prisma)
 * HTTP 500 Internal Server Error
 */
export class DatabaseError extends GroupsDomainError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(
      message,
      'DATABASE_ERROR',
      500,
      details
    );
  }
}

/**
 * Timeout ошибка
 * HTTP 504 Gateway Timeout
 */
export class TimeoutError extends GroupsDomainError {
  constructor(operation: string, timeout: number) {
    super(
      `Operation '${operation}' timed out after ${timeout}ms`,
      'TIMEOUT_ERROR',
      504,
      { operation, timeout, timeoutSeconds: timeout / 1000 }
    );
  }
}

/**
 * Ошибка при batch обработке
 * HTTP 500 Internal Server Error
 */
export class BatchProcessingError extends GroupsDomainError {
  constructor(
    message: string,
    public readonly batchIndex?: number,
    public readonly failedItems?: unknown[]
  ) {
    super(
      message,
      'BATCH_PROCESSING_ERROR',
      500,
      {
        batchIndex,
        failedItemsCount: failedItems?.length,
        failedItems: failedItems?.slice(0, 5), // Первые 5 для логов
      }
    );
  }
}

/**
 * Неизвестная ошибка (fallback)
 * HTTP 500 Internal Server Error
 */
export class UnknownError extends GroupsDomainError {
  constructor(originalError: unknown) {
    const message = originalError instanceof Error
      ? originalError.message
      : String(originalError);

    const stack = originalError instanceof Error
      ? originalError.stack
      : undefined;

    super(
      `An unknown error occurred: ${message}`,
      'UNKNOWN_ERROR',
      500,
      {
        originalError: message,
        stack,
        errorType: originalError?.constructor?.name,
      }
    );
  }
}

// ============ Error Factory & Utilities ============

/**
 * Фабрика для создания ошибок из различных источников
 */
export class ErrorFactory {
  /**
   * Создает domain error из любой ошибки
   */
  static fromError(error: unknown): GroupsDomainError {
    if (error instanceof GroupsDomainError) {
      return error;
    }

    if (error instanceof Error) {
      // Проверяем на специфичные ошибки Prisma
      if ('code' in error && typeof error.code === 'string') {
        const prismaCode = error.code as string;

        if (prismaCode === 'P2002') {
          // Unique constraint violation
          return new DatabaseError('Duplicate record in database', {
            prismaCode,
            originalMessage: error.message,
          });
        }

        if (prismaCode === 'P2025') {
          // Record not found
          return new DatabaseError('Record not found in database', {
            prismaCode,
            originalMessage: error.message,
          });
        }

        // Другие Prisma ошибки
        return new DatabaseError(error.message, {
          prismaCode,
        });
      }

      return new UnknownError(error);
    }

    return new UnknownError(error);
  }

  /**
   * Создает ValidationError из Zod ошибки
   */
  static fromZodError(zodError: any): ValidationError {
    const issues = zodError.issues?.map((issue: any) => ({
      path: issue.path.join('.'),
      message: issue.message,
      code: issue.code,
    })) || [];

    return new ValidationError(
      'Validation failed',
      'VALIDATION_ERROR',
      400,
      { issues }
    );
  }

  /**
   * Создает VkApiError из VK API response
   */
  static fromVkApiResponse(response: any): VkApiError {
    const errorCode = response?.error?.error_code;
    const errorMsg = response?.error?.error_msg || 'VK API error';

    return new VkApiError(errorMsg, errorCode, {
      requestParams: response?.error?.request_params,
    });
  }
}

/**
 * Type guard для проверки GroupsDomainError
 */
export function isGroupsDomainError(error: unknown): error is GroupsDomainError {
  return error instanceof GroupsDomainError;
}

/**
 * Type guard для проверки клиентской ошибки
 */
export function isClientError(error: unknown): boolean {
  return isGroupsDomainError(error) && error.isClientError();
}

/**
 * Type guard для проверки серверной ошибки
 */
export function isServerError(error: unknown): boolean {
  return isGroupsDomainError(error) && error.isServerError();
}

/**
 * Извлекает HTTP status code из любой ошибки
 */
export function getErrorStatusCode(error: unknown): number {
  if (isGroupsDomainError(error)) {
    return error.statusCode;
  }
  return 500; // Default Internal Server Error
}

/**
 * Извлекает error code из любой ошибки
 */
export function getErrorCode(error: unknown): string {
  if (isGroupsDomainError(error)) {
    return error.code;
  }
  return 'UNKNOWN_ERROR';
}

/**
 * Безопасная сериализация ошибки для API response
 */
export function serializeError(error: unknown): Record<string, unknown> {
  if (isGroupsDomainError(error)) {
    return error.toJSON();
  }

  if (error instanceof Error) {
    return {
      name: error.name,
      code: 'UNKNOWN_ERROR',
      message: error.message,
      statusCode: 500,
    };
  }

  return {
    name: 'UnknownError',
    code: 'UNKNOWN_ERROR',
    message: String(error),
    statusCode: 500,
  };
}
