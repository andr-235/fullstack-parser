import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import logger from '@/utils/logger';
import { ErrorCodes, AppError } from '@/types/express';
import {
  ApiResponse,
  PaginatedResponse,
  ApiErrorResponse,
  ValidationErrorResponse,
  ResponseMeta,
  RequestContext
} from '@/types/api';

// === РАСШИРЕНИЕ EXPRESS ТИПОВ ===

declare global {
  namespace Express {
    interface Request {
      requestId: string;
      startTime: number;
      context: RequestContext;
    }

    interface Response {
      success<T>(data?: T, message?: string, meta?: ResponseMeta): Response;
      error(error: string | Error | AppError | any, statusCode?: number, details?: any): Response;
      paginated<T>(data: T[], pagination: any, meta?: ResponseMeta): Response;
      validationError(errors: Array<{ field: string; message: string; value?: any }>): Response;
    }
  }
}

// === КОНФИГУРАЦИЯ ===

interface ResponseFormatterConfig {
  includeStackTrace: boolean;
  sanitizeErrors: boolean;
  includeExecutionTime: boolean;
  includeRequestId: boolean;
  timestampFormat: 'iso' | 'unix';
}

const getConfig = (): ResponseFormatterConfig => ({
  includeStackTrace: process.env.NODE_ENV === 'development',
  sanitizeErrors: process.env.NODE_ENV === 'production',
  includeExecutionTime: true,
  includeRequestId: true,
  timestampFormat: 'iso'
});

// === УТИЛИТАРНЫЕ ФУНКЦИИ ===

/**
 * Генерирует timestamp в зависимости от конфигурации
 */
const generateTimestamp = (format: 'iso' | 'unix'): string => {
  const now = new Date();
  return format === 'iso' ? now.toISOString() : Math.floor(now.getTime() / 1000).toString();
};

/**
 * Вычисляет время выполнения запроса
 */
const calculateExecutionTime = (startTime: number): number => {
  return Date.now() - startTime;
};

/**
 * Создает базовый ответ с метаданными
 */
const createBaseResponse = (req: Request, additionalMeta?: ResponseMeta): Partial<ApiResponse> => {
  const config = getConfig();
  const executionTime = config.includeExecutionTime ? calculateExecutionTime(req.startTime) : undefined;

  return {
    timestamp: generateTimestamp(config.timestampFormat),
    requestId: config.includeRequestId ? req.requestId : undefined,
    ...(executionTime !== undefined && { executionTime }),
    ...additionalMeta
  };
};

/**
 * Нормализует ошибку для ответа
 */
const normalizeError = (error: string | Error | AppError): { message: string; code?: string; details?: any; stack?: string } => {
  const config = getConfig();

  if (typeof error === 'string') {
    return { message: error };
  }

  if (error instanceof Error) {
    const appError = error as AppError;

    return {
      message: appError.message,
      code: appError.code,
      details: appError.details,
      ...(config.includeStackTrace && { stack: appError.stack })
    };
  }

  return { message: 'Unknown error' };
};

/**
 * Определяет HTTP статус код на основе ошибки
 */
const getStatusCodeFromError = (error: string | Error | AppError): number => {
  if (typeof error === 'string') return 500;

  const appError = error as AppError;
  if (appError.statusCode) return appError.statusCode;

  // Маппинг кодов ошибок на HTTP статусы
  const errorCodeToStatus: Record<string, number> = {
    [ErrorCodes.VALIDATION_ERROR]: 400,
    [ErrorCodes.INVALID_REQUEST]: 400,
    [ErrorCodes.NOT_FOUND]: 404,
    [ErrorCodes.UNAUTHORIZED]: 401,
    [ErrorCodes.FORBIDDEN]: 403,
    [ErrorCodes.ALREADY_EXISTS]: 409,
    [ErrorCodes.RATE_LIMIT_EXCEEDED]: 429,
    [ErrorCodes.VK_RATE_LIMIT]: 429,
    [ErrorCodes.SERVICE_UNAVAILABLE]: 503,
    [ErrorCodes.INTERNAL_ERROR]: 500
  };

  return errorCodeToStatus[appError.code] || 500;
};

// === ОСНОВНОЕ MIDDLEWARE ===

/**
 * Middleware для добавления requestId и инициализации контекста
 */
export const requestIdMiddleware = (req: Request, res: Response, next: NextFunction) => {
  req.requestId = uuidv4();
  req.startTime = Date.now();

  req.context = {
    requestId: req.requestId,
    startTime: req.startTime,
    userAgent: req.get('User-Agent'),
    ip: req.ip || req.connection.remoteAddress,
    path: req.path,
    method: req.method
  };

  // Логируем входящий запрос
  logger.info('Incoming request', {
    requestId: req.requestId,
    method: req.method,
    path: req.path,
    userAgent: req.context.userAgent,
    ip: req.context.ip
  });

  next();
};

/**
 * Основное middleware для форматирования ответов
 */
export const responseFormatter = (req: Request, res: Response, next: NextFunction) => {
  /**
   * Стандартизированный успешный ответ
   */
  res.success = function<T>(data?: T, message?: string, meta?: ResponseMeta) {
    const baseResponse = createBaseResponse(req, meta);
    const response = {
      success: true,
      data,
      message,
      timestamp: baseResponse.timestamp || generateTimestamp('iso'),
      requestId: baseResponse.requestId || req.requestId,
      ...(baseResponse.executionTime && { executionTime: baseResponse.executionTime }),
      ...meta
    };

    // Логируем успешный ответ
    logger.info('Successful response', {
      requestId: req.requestId,
      statusCode: this.statusCode || 200,
      hasData: data !== undefined,
      message,
      executionTime: response.executionTime
    });

    return this.json(response);
  };

  /**
   * Стандартизированный ответ с ошибкой
   */
  res.error = function(error: string | Error | AppError, statusCode?: number, details?: any) {
    const normalizedError = normalizeError(error);
    const finalStatusCode = statusCode || getStatusCodeFromError(error);

    const baseResponse = createBaseResponse(req);
    const response: ApiErrorResponse = {
      success: false,
      error: normalizedError.message,
      timestamp: baseResponse.timestamp || generateTimestamp('iso'),
      requestId: baseResponse.requestId || req.requestId,
      details: {
        code: normalizedError.code || ErrorCodes.INTERNAL_ERROR,
        ...normalizedError.details,
        ...details
      },
      ...(baseResponse.executionTime && { executionTime: baseResponse.executionTime })
    };

    // Логируем ошибку
    logger.error('Error response', {
      requestId: req.requestId,
      statusCode: finalStatusCode,
      error: normalizedError.message,
      code: normalizedError.code,
      stack: normalizedError.stack,
      details: response.details
    });

    return this.status(finalStatusCode).json(response);
  };

  /**
   * Стандартизированный пагинированный ответ
   */
  res.paginated = function<T>(data: T[], pagination: any, meta?: ResponseMeta) {
    const baseResponse = createBaseResponse(req, meta);
    const response: PaginatedResponse<T> = {
      success: true,
      data,
      pagination: {
        page: pagination.page || 1,
        limit: pagination.limit || 20,
        total: pagination.total || data.length,
        totalPages: pagination.totalPages || Math.ceil((pagination.total || data.length) / (pagination.limit || 20)),
        hasNext: pagination.hasNext || false,
        hasPrev: pagination.hasPrev || false
      },
      timestamp: baseResponse.timestamp || generateTimestamp('iso'),
      requestId: baseResponse.requestId || req.requestId,
      ...(baseResponse.executionTime && { executionTime: baseResponse.executionTime })
    };

    // Логируем пагинированный ответ
    logger.info('Paginated response', {
      requestId: req.requestId,
      statusCode: this.statusCode || 200,
      itemsCount: data.length,
      pagination: response.pagination,
      executionTime: response.executionTime
    });

    return this.json(response);
  };

  /**
   * Специализированный ответ для ошибок валидации
   */
  res.validationError = function(errors: Array<{ field: string; message: string; value?: any }>) {
    const baseResponse = createBaseResponse(req);
    const response: ValidationErrorResponse = {
      success: false,
      error: 'Validation failed',
      timestamp: baseResponse.timestamp || generateTimestamp('iso'),
      requestId: baseResponse.requestId || req.requestId,
      details: {
        code: ErrorCodes.VALIDATION_ERROR,
        validationErrors: errors
      },
      ...(baseResponse.executionTime && { executionTime: baseResponse.executionTime })
    };

    // Логируем ошибки валидации
    logger.warn('Validation error response', {
      requestId: req.requestId,
      statusCode: 400,
      validationErrors: errors,
      executionTime: response.executionTime
    });

    return this.status(400).json(response);
  };

  next();
};

// === MIDDLEWARE ДЛЯ ОБРАБОТКИ ОШИБОК ===

/**
 * Глобальный обработчик ошибок с стандартизированными ответами
 */
export const errorHandler = (error: Error | AppError, req: Request, res: Response, next: NextFunction) => {
  // Если ответ уже был отправлен, передаем ошибку дальше
  if (res.headersSent) {
    return next(error);
  }

  // Используем стандартизированный метод error
  res.error(error);
};

/**
 * Обработчик для несуществующих маршрутов
 */
export const notFoundHandler = (req: Request, res: Response) => {
  res.error(`Route ${req.method} ${req.path} not found`, 404, {
    code: ErrorCodes.NOT_FOUND,
    method: req.method,
    path: req.path
  });
};

// === ВСПОМОГАТЕЛЬНЫЕ MIDDLEWARE ===

/**
 * Middleware для логирования всех исходящих ответов
 */
export const responseLogger = (req: Request, res: Response, next: NextFunction) => {
  const originalSend = res.send;

  res.send = function(data) {
    // Логируем исходящий ответ
    logger.debug('Outgoing response', {
      requestId: req.requestId,
      statusCode: res.statusCode,
      contentLength: data ? data.length : 0,
      contentType: res.get('Content-Type'),
      executionTime: calculateExecutionTime(req.startTime)
    });

    return originalSend.call(this, data);
  };

  next();
};

/**
 * Middleware для установки стандартных заголовков ответа
 */
export const responseHeaders = (req: Request, res: Response, next: NextFunction) => {
  // Устанавливаем стандартные заголовки
  res.setHeader('X-Request-ID', req.requestId);
  res.setHeader('X-API-Version', process.env.API_VERSION || '1.0.0');
  res.setHeader('X-Powered-By', 'VK Analytics API');

  // Заголовки безопасности
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');

  next();
};

// === ЭКСПОРТ ===

export default {
  requestIdMiddleware,
  responseFormatter,
  errorHandler,
  notFoundHandler,
  responseLogger,
  responseHeaders
};