import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import logger from '@/utils/logger';
import {
  BaseApiResponse,
  SuccessResponse,
  ErrorResponse,
  PaginatedSuccessResponse,
  ErrorCodes
} from '@/types/express';

/**
 * Middleware для генерации requestId
 * Гарантирует наличие уникального ID для каждого запроса
 */
export const requestIdMiddleware = (req: Request, res: Response, next: NextFunction): void => {
  // Генерируем requestId если его нет
  if (!req.id) {
    req.id = uuidv4();
  }

  // Добавляем requestId в заголовки ответа для отладки
  res.set('X-Request-ID', req.id);

  next();
};

/**
 * Middleware для стандартизации API ответов
 * Добавляет методы success(), error(), paginated() к объекту Response
 */
export const responseHandler = (req: Request, res: Response, next: NextFunction): void => {
  const timestamp = new Date().toISOString();
  const requestId = req.id;

  /**
   * Метод для успешных ответов
   */
  res.success = function<T>(data: T, meta?: any): Response {
    const response: SuccessResponse<T> = {
      success: true,
      timestamp,
      requestId,
      data
    };

    // Добавляем мета-информацию если она есть
    if (meta) {
      (response as any).meta = meta;
    }

    logger.info('API Success Response', {
      requestId,
      method: req.method,
      url: req.url,
      statusCode: res.statusCode || 200,
      dataType: typeof data,
      hasData: data !== null && data !== undefined
    });

    return this.json(response);
  };

  /**
   * Метод для ответов с ошибками
   */
  res.error = function(error: string | Error | any, statusCode?: number, details?: any): Response {
    let errorMessage: string;
    let errorCode: string;
    let finalStatusCode = statusCode || 500;

    // Обрабатываем различные типы ошибок
    if (typeof error === 'string') {
      errorMessage = error;
      errorCode = 'GENERAL_ERROR';
    } else if (error instanceof Error) {
      errorMessage = error.message;
      errorCode = (error as any).code || 'INTERNAL_ERROR';
      // Если у ошибки есть statusCode, используем его
      if ((error as any).statusCode) {
        finalStatusCode = (error as any).statusCode;
      }
    } else {
      errorMessage = 'Unknown error';
      errorCode = 'UNKNOWN_ERROR';
    }

    const response: ErrorResponse = {
      success: false,
      timestamp,
      requestId,
      error: {
        code: errorCode,
        message: errorMessage,
        details
      }
    };

    // Добавляем stack trace только в development режиме
    if (process.env.NODE_ENV === 'development' && error instanceof Error) {
      response.error.stack = error.stack;
    }

    logger.warn('API Error Response', {
      requestId,
      method: req.method,
      url: req.url,
      statusCode: finalStatusCode,
      errorCode,
      errorMessage,
      hasDetails: !!details
    });

    return this.status(finalStatusCode).json(response);
  };

  /**
   * Метод для пагинированных ответов
   */
  res.paginated = function<T>(
    data: T[],
    pagination: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    },
    meta?: any
  ): Response {
    const response: PaginatedSuccessResponse<T> = {
      success: true,
      timestamp,
      requestId,
      data,
      pagination: {
        ...pagination,
        hasNext: pagination.page < pagination.totalPages,
        hasPrev: pagination.page > 1
      },
      meta: {
        totalItems: pagination.total,
        itemsPerPage: pagination.limit,
        firstItem: (pagination.page - 1) * pagination.limit + 1,
        lastItem: Math.min(pagination.page * pagination.limit, pagination.total),
        ...meta
      }
    };

    logger.info('API Paginated Response', {
      requestId,
      method: req.method,
      url: req.url,
      statusCode: res.statusCode || 200,
      itemsCount: data.length,
      page: pagination.page,
      totalPages: pagination.totalPages,
      total: pagination.total
    });

    return this.json(response);
  };

  next();
};

/**
 * Расширенный middleware для обработки всех типов ошибок
 */
export const errorHandler = (
  error: any,
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  // Если ответ уже отправлен, передаем ошибку дальше
  if (res.headersSent) {
    return next(error);
  }

  const timestamp = new Date().toISOString();
  const requestId = req.id;

  // Импортируем ErrorUtils для работы с ошибками
  const { ErrorUtils } = require('@/utils/errors');

  // Преобразуем ошибку в AppError если это необходимо
  const appError = ErrorUtils.toAppError(error);

  // Создаем контекст запроса для детального логирования
  const requestContext = ErrorUtils.createRequestContext(req);

  // Определяем уровень логирования на основе типа ошибки
  const isOperational = ErrorUtils.isOperationalError(appError);
  const logLevel = isOperational ? 'warn' : 'error';

  // Структурированное логирование ошибки
  logger[logLevel]('Application Error', {
    // Основная информация об ошибке
    errorName: appError.name,
    errorCode: appError.code,
    errorMessage: appError.message,
    statusCode: appError.statusCode,
    isOperational: appError.isOperational,

    // Контекст запроса
    requestId,
    method: req.method,
    url: req.url,
    userAgent: req.get('User-Agent'),
    ip: req.ip,

    // Детали ошибки
    details: appError.details,
    context: appError.context,

    // Техническая информация
    timestamp: appError.timestamp,
    stack: appError.stack,

    // Причинная ошибка
    cause: appError.cause ? {
      name: appError.cause.name,
      message: appError.cause.message,
      stack: appError.cause.stack
    } : undefined,

    // Системная информация
    environment: process.env.NODE_ENV,
    version: process.env.npm_package_version,
    hostname: require('os').hostname(),
    pid: process.pid
  });

  // Определяем детали ответа на основе типа ошибки
  let responseDetails: any = undefined;

  if (process.env.NODE_ENV === 'development') {
    responseDetails = {
      originalError: error.message,
      stack: appError.stack,
      cause: appError.cause ? {
        name: appError.cause.name,
        message: appError.cause.message
      } : undefined,
      context: appError.context,
      details: appError.details
    };
  } else {
    // В production показываем детали только для операционных ошибок
    if (isOperational && appError.details) {
      responseDetails = appError.details;
    }
  }

  // Создаем стандартизированный ответ
  const response: ErrorResponse = {
    success: false,
    timestamp,
    requestId,
    error: {
      code: appError.code,
      message: appError.message,
      details: responseDetails
    }
  };

  // Добавляем заголовки для специфичных ошибок
  if (appError.code === ErrorCodes.RATE_LIMIT_EXCEEDED) {
    const retryAfter = appError.details?.retryAfter || 60;
    res.set('Retry-After', retryAfter.toString());
  }

  if (appError.code === ErrorCodes.VK_RATE_LIMIT) {
    const rateLimitReset = appError.details?.rateLimitReset;
    if (rateLimitReset) {
      res.set('X-RateLimit-Reset', Math.floor(rateLimitReset.getTime() / 1000).toString());
    }
  }

  // Отправляем ответ
  res.status(appError.statusCode).json(response);

  // Дополнительные действия для критических ошибок
  if (!isOperational) {
    logger.error('Critical non-operational error detected', {
      requestId,
      errorCode: appError.code,
      errorMessage: appError.message,
      stack: appError.stack
    });

    // В production можем отправить уведомления в системы мониторинга
    if (process.env.NODE_ENV === 'production') {
      // TODO: Интеграция с системами мониторинга (Sentry, DataDog, etc.)
      // notificationService.sendCriticalError(appError, requestContext);
    }
  }
};

/**
 * Middleware для логирования всех HTTP ответов
 */
export const responseLogger = (req: Request, res: Response, next: NextFunction): void => {
  const startTime = Date.now();

  // Перехватываем оригинальный метод res.json
  const originalJson = res.json;

  res.json = function(body: any) {
    const responseTime = Date.now() - startTime;

    logger.info('HTTP Response', {
      requestId: req.id,
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      responseTime: `${responseTime}ms`,
      userAgent: req.get('User-Agent'),
      ip: req.ip,
      success: body?.success !== false
    });

    return originalJson.call(this, body);
  };

  next();
};

/**
 * Вспомогательные функции для создания стандартизированных ответов
 */
export class ApiResponseBuilder {
  private timestamp: string;
  private requestId?: string;

  constructor(requestId?: string) {
    this.timestamp = new Date().toISOString();
    this.requestId = requestId;
  }

  /**
   * Создает успешный ответ
   */
  success<T>(data: T, meta?: any): SuccessResponse<T> {
    const response: SuccessResponse<T> = {
      success: true,
      timestamp: this.timestamp,
      requestId: this.requestId,
      data
    };

    if (meta) {
      (response as any).meta = meta;
    }

    return response;
  }

  /**
   * Создает ответ с ошибкой
   */
  error(code: string, message: string, details?: any): ErrorResponse {
    return {
      success: false,
      timestamp: this.timestamp,
      requestId: this.requestId,
      error: {
        code,
        message,
        details,
        stack: process.env.NODE_ENV === 'development' && details instanceof Error
          ? details.stack
          : undefined
      }
    };
  }

  /**
   * Создает пагинированный ответ
   */
  paginated<T>(
    data: T[],
    pagination: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    },
    meta?: any
  ): PaginatedSuccessResponse<T> {
    return {
      success: true,
      timestamp: this.timestamp,
      requestId: this.requestId,
      data,
      pagination: {
        ...pagination,
        hasNext: pagination.page < pagination.totalPages,
        hasPrev: pagination.page > 1
      },
      meta: {
        totalItems: pagination.total,
        itemsPerPage: pagination.limit,
        firstItem: (pagination.page - 1) * pagination.limit + 1,
        lastItem: Math.min(pagination.page * pagination.limit, pagination.total),
        ...meta
      }
    };
  }
}

/**
 * Утилита для валидации параметров пагинации
 */
export const validatePagination = (page?: number, limit?: number) => {
  const validatedPage = Math.max(1, Number(page) || 1);
  const validatedLimit = Math.min(Math.max(1, Number(limit) || 10), 100);
  const offset = (validatedPage - 1) * validatedLimit;

  return {
    page: validatedPage,
    limit: validatedLimit,
    offset
  };
};

/**
 * Утилита для создания объекта пагинации
 */
export const createPagination = (page: number, limit: number, total: number) => {
  const totalPages = Math.ceil(total / limit);

  return {
    page,
    limit,
    total,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1
  };
};

/**
 * Middleware для установки стандартных заголовков
 */
export const responseHeaders = (req: Request, res: Response, next: NextFunction): void => {
  // Устанавливаем стандартные заголовки безопасности
  res.set('X-Content-Type-Options', 'nosniff');
  res.set('X-Frame-Options', 'DENY');
  res.set('X-XSS-Protection', '1; mode=block');

  // Указываем формат API ответа
  res.set('Content-Type', 'application/json; charset=utf-8');

  next();
};

/**
 * Middleware для обработки 404 ошибок
 */
export const notFoundHandler = (req: Request, res: Response): void => {
  const requestId = req.id;

  logger.warn('404 Not Found', {
    method: req.method,
    url: req.url,
    query: req.query,
    userAgent: req.get('User-Agent'),
    ip: req.ip,
    requestId
  });

  res.status(404).json({
    success: false,
    timestamp: new Date().toISOString(),
    requestId,
    error: {
      code: ErrorCodes.NOT_FOUND,
      message: `Route ${req.method} ${req.url} not found`,
      details: {
        method: req.method,
        path: req.url
      }
    }
  });
};

/**
 * Middleware для установки правильного имени как responseFormatter
 * (для совместимости с существующим кодом)
 */
export const responseFormatter = responseHandler;