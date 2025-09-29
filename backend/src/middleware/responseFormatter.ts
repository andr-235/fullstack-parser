import { Request, Response, NextFunction } from 'express';
import { StatusCodes } from 'http-status-codes';
import logger from '@/utils/logger';
import { ErrorCodes, AppError } from '@/types/express';
import {
  ApiResponse,
  PaginatedResponse,
  ApiErrorResponse,
  ValidationErrorResponse,
  ResponseMeta
} from '@/types/api';

// Расширения интерфейсов Express уже определены в @/types/express.ts

// === УТИЛИТЫ ===

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
  const executionTime = calculateExecutionTime(req.startTime);

  return {
    timestamp: new Date().toISOString(),
    requestId: req.requestId,
    executionTime,
    ...additionalMeta
  };
};

/**
 * Нормализует ошибку для ответа
 */
const normalizeError = (error: string | Error | AppError): { message: string; code?: string; details?: any; stack?: string } => {
  if (typeof error === 'string') {
    return { message: error };
  }

  if (error instanceof Error) {
    const appError = error as AppError;

    return {
      message: appError.message,
      code: appError.code,
      details: appError.details,
      ...(process.env.NODE_ENV === 'development' && { stack: appError.stack })
    };
  }

  return { message: 'Unknown error' };
};

/**
 * Маппинг кодов ошибок на HTTP статусы с использованием http-status-codes
 */
const getStatusCodeFromError = (error: string | Error | AppError): number => {
  if (typeof error === 'string') return StatusCodes.INTERNAL_SERVER_ERROR;

  const appError = error as AppError;
  if (appError.statusCode) return appError.statusCode;

  const errorCodeToStatus: Record<string, number> = {
    [ErrorCodes.VALIDATION_ERROR]: StatusCodes.BAD_REQUEST,
    [ErrorCodes.INVALID_REQUEST]: StatusCodes.BAD_REQUEST,
    [ErrorCodes.NOT_FOUND]: StatusCodes.NOT_FOUND,
    [ErrorCodes.UNAUTHORIZED]: StatusCodes.UNAUTHORIZED,
    [ErrorCodes.FORBIDDEN]: StatusCodes.FORBIDDEN,
    [ErrorCodes.ALREADY_EXISTS]: StatusCodes.CONFLICT,
    [ErrorCodes.RATE_LIMIT_EXCEEDED]: StatusCodes.TOO_MANY_REQUESTS,
    [ErrorCodes.VK_RATE_LIMIT]: StatusCodes.TOO_MANY_REQUESTS,
    [ErrorCodes.SERVICE_UNAVAILABLE]: StatusCodes.SERVICE_UNAVAILABLE,
    [ErrorCodes.INTERNAL_ERROR]: StatusCodes.INTERNAL_SERVER_ERROR
  };

  return errorCodeToStatus[appError.code] || StatusCodes.INTERNAL_SERVER_ERROR;
};

// === ОСНОВНОЕ MIDDLEWARE ===

/**
 * Основное middleware для форматирования ответов
 */
export const responseFormatter = (req: Request, res: Response, next: NextFunction) => {
  /**
   * Стандартизированный успешный ответ
   */
  res.success = function<T>(data?: T, message?: string, meta?: ResponseMeta) {
    const baseResponse = createBaseResponse(req, meta);
    const response: ApiResponse<T> = {
      success: true,
      data,
      message,
      timestamp: baseResponse.timestamp!,
      requestId: baseResponse.requestId!,
      executionTime: baseResponse.executionTime!,
      ...meta
    };

    // Логируем успешный ответ
    logger.info('Successful response', {
      requestId: req.requestId,
      statusCode: this.statusCode || StatusCodes.OK,
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
      timestamp: baseResponse.timestamp!,
      requestId: baseResponse.requestId!,
      executionTime: baseResponse.executionTime!,
      details: {
        code: normalizedError.code || ErrorCodes.INTERNAL_ERROR,
        ...normalizedError.details,
        ...details
      }
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
      timestamp: baseResponse.timestamp!,
      requestId: baseResponse.requestId!,
      executionTime: baseResponse.executionTime!
    };

    // Логируем пагинированный ответ
    logger.info('Paginated response', {
      requestId: req.requestId,
      statusCode: this.statusCode || StatusCodes.OK,
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
      timestamp: baseResponse.timestamp!,
      requestId: baseResponse.requestId!,
      executionTime: baseResponse.executionTime!,
      details: {
        code: ErrorCodes.VALIDATION_ERROR,
        validationErrors: errors
      }
    };

    // Логируем ошибки валидации
    logger.warn('Validation error response', {
      requestId: req.requestId,
      statusCode: StatusCodes.BAD_REQUEST,
      validationErrors: errors,
      executionTime: response.executionTime
    });

    return this.status(StatusCodes.BAD_REQUEST).json(response);
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
  res.error(`Route ${req.method} ${req.path} not found`, StatusCodes.NOT_FOUND, {
    code: ErrorCodes.NOT_FOUND,
    method: req.method,
    path: req.path
  });
};

// === ЭКСПОРТ ===

export default {
  responseFormatter,
  errorHandler,
  notFoundHandler
};