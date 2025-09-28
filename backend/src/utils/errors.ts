import {
  AppError,
  AppValidationError,
  AppVkApiError,
  AppTaskError,
  AppDatabaseError,
  ErrorCodes,
  ValidationErrorDetail,
  VkApiErrorDetails,
  TaskErrorContext,
  DatabaseErrorContext,
  ErrorContext
} from '@/types/express';

/**
 * Базовый класс для всех ошибок приложения
 */
export class BaseAppError extends Error implements AppError {
  public readonly name: string;
  public readonly code: ErrorCodes;
  public readonly statusCode: number;
  public readonly isOperational: boolean;
  public readonly timestamp: Date;
  public readonly requestId?: string;
  public readonly userId?: string;
  public readonly details?: any;
  public readonly cause?: Error;
  public readonly context?: Record<string, any>;

  constructor(
    message: string,
    code: ErrorCodes,
    statusCode: number = 500,
    isOperational: boolean = true,
    details?: any,
    cause?: Error
  ) {
    super(message);

    this.name = this.constructor.name;
    this.code = code;
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.timestamp = new Date();
    this.details = details;
    this.cause = cause;

    // Захватываем stack trace, исключая конструктор
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * Устанавливает ID запроса для трассировки
   */
  setRequestId(requestId: string): this {
    (this as any).requestId = requestId;
    return this;
  }

  /**
   * Устанавливает ID пользователя
   */
  setUserId(userId: string): this {
    (this as any).userId = userId;
    return this;
  }

  /**
   * Добавляет контекстную информацию
   */
  setContext(context: Record<string, any>): this {
    (this as any).context = { ...(this.context || {}), ...context };
    return this;
  }

  /**
   * Преобразует ошибку в JSON для логирования
   */
  toJSON(): object {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      statusCode: this.statusCode,
      isOperational: this.isOperational,
      timestamp: this.timestamp.toISOString(),
      requestId: this.requestId,
      userId: this.userId,
      details: this.details,
      context: this.context,
      stack: this.stack,
      cause: this.cause ? {
        name: this.cause.name,
        message: this.cause.message,
        stack: this.cause.stack
      } : undefined
    };
  }
}

/**
 * Ошибка валидации
 */
export class ValidationError extends BaseAppError implements AppValidationError {
  public readonly code: ErrorCodes.VALIDATION_ERROR = ErrorCodes.VALIDATION_ERROR;
  public readonly details: ValidationErrorDetail[];

  constructor(
    message: string = 'Validation failed',
    details: ValidationErrorDetail[] = [],
    cause?: Error
  ) {
    super(message, ErrorCodes.VALIDATION_ERROR, 400, true, details, cause);
    this.details = details;
  }

  /**
   * Создает ошибку валидации из Joi error
   */
  static fromJoi(joiError: any): ValidationError {
    const details: ValidationErrorDetail[] = joiError.details?.map((detail: any) => ({
      field: detail.path?.join('.') || 'unknown',
      message: detail.message,
      value: detail.context?.value,
      constraint: detail.type,
      code: detail.context?.key
    })) || [];

    return new ValidationError(
      joiError.message || 'Validation failed',
      details,
      joiError
    );
  }

  /**
   * Добавляет ошибку валидации поля
   */
  addFieldError(field: string, message: string, value?: any, constraint?: string): this {
    this.details.push({
      field,
      message,
      value,
      constraint
    });
    return this;
  }
}

/**
 * Ошибка VK API
 */
export class VkApiError extends BaseAppError implements AppVkApiError {
  public readonly code: ErrorCodes.VK_API_ERROR | ErrorCodes.VK_RATE_LIMIT | ErrorCodes.VK_INVALID_TOKEN;
  public readonly details: VkApiErrorDetails;

  constructor(
    message: string,
    code: ErrorCodes.VK_API_ERROR | ErrorCodes.VK_RATE_LIMIT | ErrorCodes.VK_INVALID_TOKEN = ErrorCodes.VK_API_ERROR,
    details: VkApiErrorDetails = {},
    cause?: Error
  ) {
    const statusCode = code === ErrorCodes.VK_RATE_LIMIT ? 429 : 502;
    super(message, code, statusCode, true, details, cause);
    this.code = code;
    this.details = details;
  }

  /**
   * Создает ошибку из ответа VK API
   */
  static fromVkResponse(vkError: any, method?: string, parameters?: Record<string, any>): VkApiError {
    const errorCode = vkError.error_code;
    const errorMessage = vkError.error_msg || 'VK API Error';

    let appErrorCode = ErrorCodes.VK_API_ERROR;
    if (errorCode === 6) {
      appErrorCode = ErrorCodes.VK_RATE_LIMIT;
    } else if (errorCode === 5) {
      appErrorCode = ErrorCodes.VK_INVALID_TOKEN;
    }

    const details: VkApiErrorDetails = {
      vkErrorCode: errorCode,
      vkErrorMessage: errorMessage,
      method,
      parameters
    };

    return new VkApiError(
      `VK API Error ${errorCode}: ${errorMessage}`,
      appErrorCode,
      details
    );
  }

  /**
   * Создает ошибку rate limit с временем сброса
   */
  static rateLimitError(retryAfter?: number): VkApiError {
    const details: VkApiErrorDetails = {
      vkErrorCode: 6,
      vkErrorMessage: 'Too many requests per second',
      rateLimitReset: retryAfter ? new Date(Date.now() + retryAfter * 1000) : undefined
    };

    return new VkApiError(
      'VK API rate limit exceeded',
      ErrorCodes.VK_RATE_LIMIT,
      details
    );
  }
}

/**
 * Ошибка задачи
 */
export class TaskError extends BaseAppError implements AppTaskError {
  public readonly code: ErrorCodes.TASK_NOT_FOUND | ErrorCodes.TASK_FAILED | ErrorCodes.TASK_TIMEOUT;
  public readonly context: TaskErrorContext;

  constructor(
    message: string,
    code: ErrorCodes.TASK_NOT_FOUND | ErrorCodes.TASK_FAILED | ErrorCodes.TASK_TIMEOUT,
    context: TaskErrorContext,
    cause?: Error
  ) {
    const statusCode = code === ErrorCodes.TASK_NOT_FOUND ? 404 : 500;
    super(message, code, statusCode, true, context, cause);
    this.code = code;
    this.context = context;
  }

  /**
   * Создает ошибку "задача не найдена"
   */
  static notFound(taskId: string): TaskError {
    return new TaskError(
      `Task ${taskId} not found`,
      ErrorCodes.TASK_NOT_FOUND,
      { taskId, taskType: 'unknown' }
    );
  }

  /**
   * Создает ошибку выполнения задачи
   */
  static failed(taskId: string, taskType: string, phase?: string, cause?: Error): TaskError {
    return new TaskError(
      `Task ${taskId} failed` + (phase ? ` during ${phase}` : ''),
      ErrorCodes.TASK_FAILED,
      { taskId, taskType, phase },
      cause
    );
  }

  /**
   * Создает ошибку таймаута задачи
   */
  static timeout(taskId: string, taskType: string, progress?: number): TaskError {
    return new TaskError(
      `Task ${taskId} timed out`,
      ErrorCodes.TASK_TIMEOUT,
      { taskId, taskType, progress }
    );
  }
}

/**
 * Ошибка базы данных
 */
export class DatabaseError extends BaseAppError implements AppDatabaseError {
  public readonly code: ErrorCodes.DATABASE_ERROR | ErrorCodes.TRANSACTION_FAILED;
  public readonly context: DatabaseErrorContext;

  constructor(
    message: string,
    operation: string,
    code: ErrorCodes.DATABASE_ERROR | ErrorCodes.TRANSACTION_FAILED = ErrorCodes.DATABASE_ERROR,
    context: Partial<DatabaseErrorContext> = {},
    cause?: Error
  ) {
    super(message, code, 500, true, context, cause);
    this.code = code;
    this.context = { operation, ...context };
  }

  /**
   * Создает ошибку из Prisma ошибки
   */
  static fromPrisma(prismaError: any, operation: string): DatabaseError {
    let message = 'Database operation failed';
    let context: Partial<DatabaseErrorContext> = { operation };

    if (prismaError.code === 'P2002') {
      message = 'Unique constraint violation';
      context.constraint = prismaError.meta?.target;
    } else if (prismaError.code === 'P2025') {
      message = 'Record not found';
    } else if (prismaError.code === 'P2003') {
      message = 'Foreign key constraint violation';
      context.constraint = prismaError.meta?.field_name;
    }

    return new DatabaseError(
      message,
      operation,
      ErrorCodes.DATABASE_ERROR,
      context,
      prismaError
    );
  }
}

/**
 * Ошибка ресурса не найден
 */
export class NotFoundError extends BaseAppError {
  constructor(resource: string, identifier?: string, cause?: Error) {
    const message = identifier
      ? `${resource} with id ${identifier} not found`
      : `${resource} not found`;

    super(message, ErrorCodes.NOT_FOUND, 404, true, { resource, identifier }, cause);
  }
}

/**
 * Ошибка неавторизованного доступа
 */
export class UnauthorizedError extends BaseAppError {
  constructor(message: string = 'Unauthorized access', cause?: Error) {
    super(message, ErrorCodes.UNAUTHORIZED, 401, true, undefined, cause);
  }
}

/**
 * Ошибка запрещенного доступа
 */
export class ForbiddenError extends BaseAppError {
  constructor(message: string = 'Access forbidden', cause?: Error) {
    super(message, ErrorCodes.FORBIDDEN, 403, true, undefined, cause);
  }
}

/**
 * Ошибка превышения лимита запросов
 */
export class RateLimitError extends BaseAppError {
  constructor(message: string = 'Rate limit exceeded', retryAfter?: number, cause?: Error) {
    super(message, ErrorCodes.RATE_LIMIT_EXCEEDED, 429, true, { retryAfter }, cause);
  }
}

/**
 * Ошибка внутреннего сервера
 */
export class InternalServerError extends BaseAppError {
  constructor(message: string = 'Internal server error', cause?: Error) {
    super(message, ErrorCodes.INTERNAL_ERROR, 500, false, undefined, cause);
  }
}

/**
 * Ошибка недоступности сервиса
 */
export class ServiceUnavailableError extends BaseAppError {
  constructor(message: string = 'Service temporarily unavailable', cause?: Error) {
    super(message, ErrorCodes.SERVICE_UNAVAILABLE, 503, true, undefined, cause);
  }
}

/**
 * Утилиты для работы с ошибками
 */
export class ErrorUtils {
  /**
   * Проверяет, является ли ошибка операционной
   */
  static isOperationalError(error: any): boolean {
    if (error instanceof BaseAppError) {
      return error.isOperational;
    }
    return false;
  }

  /**
   * Извлекает код ошибки
   */
  static getErrorCode(error: any): ErrorCodes {
    if (error instanceof BaseAppError) {
      return error.code;
    }

    // Определяем код на основе типа ошибки
    if (error.name === 'ValidationError') {
      return ErrorCodes.VALIDATION_ERROR;
    }
    if (error.code === 'ECONNREFUSED') {
      return ErrorCodes.CONNECTION_REFUSED;
    }
    if (error.code === 'ENOTFOUND') {
      return ErrorCodes.CONNECTION_ERROR;
    }
    if (error.code === 'ETIMEDOUT') {
      return ErrorCodes.TIMEOUT;
    }

    return ErrorCodes.INTERNAL_ERROR;
  }

  /**
   * Определяет HTTP статус код для ошибки
   */
  static getStatusCode(error: any): number {
    if (error instanceof BaseAppError) {
      return error.statusCode;
    }

    // Стандартные HTTP ошибки
    const code = ErrorUtils.getErrorCode(error);
    switch (code) {
      case ErrorCodes.VALIDATION_ERROR:
      case ErrorCodes.INVALID_REQUEST:
        return 400;
      case ErrorCodes.UNAUTHORIZED:
        return 401;
      case ErrorCodes.FORBIDDEN:
        return 403;
      case ErrorCodes.NOT_FOUND:
        return 404;
      case ErrorCodes.RATE_LIMIT_EXCEEDED:
        return 429;
      case ErrorCodes.SERVICE_UNAVAILABLE:
        return 503;
      default:
        return 500;
    }
  }

  /**
   * Создает контекст ошибки из Express запроса
   */
  static createRequestContext(req: any): ErrorContext {
    return {
      method: req.method,
      url: req.url,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      timestamp: new Date(),
      version: process.env.npm_package_version,
      environment: process.env.NODE_ENV,
      hostname: require('os').hostname(),
      pid: process.pid
    };
  }

  /**
   * Преобразует любую ошибку в AppError
   */
  static toAppError(error: any, defaultMessage?: string): BaseAppError {
    if (error instanceof BaseAppError) {
      return error;
    }

    // Создаем AppError на основе типа исходной ошибки
    const code = ErrorUtils.getErrorCode(error);
    const statusCode = ErrorUtils.getStatusCode(error);
    const message = error.message || defaultMessage || 'An error occurred';

    return new BaseAppError(message, code, statusCode, true, undefined, error);
  }
}

/**
 * Типизированные ошибки для экспорта
 */
export {
  ValidationError as AppValidationError,
  VkApiError as AppVkApiError,
  TaskError as AppTaskError,
  DatabaseError as AppDatabaseError
};