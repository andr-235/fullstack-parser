// Расширения Express типов для middleware

// === СТАНДАРТИЗИРОВАННЫЕ API ОТВЕТЫ ===

/**
 * Базовый интерфейс для всех API ответов
 * Обеспечивает единообразие структуры ответов
 */
export interface BaseApiResponse {
  success: boolean;
  timestamp: string;
  requestId?: string;
}

/**
 * Успешный API ответ с данными
 */
export interface SuccessResponse<T = any> extends BaseApiResponse {
  success: true;
  data: T;
}

/**
 * Ответ с ошибкой
 */
export interface ErrorResponse extends BaseApiResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    stack?: string; // Только для development режима
  };
}

/**
 * Универсальный тип для всех API ответов
 */
export type ApiResponse<T = any> = SuccessResponse<T> | ErrorResponse;

/**
 * Пагинированный ответ
 */
export interface PaginatedSuccessResponse<T> extends BaseApiResponse {
  success: true;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  meta?: {
    totalItems: number;
    itemsPerPage: number;
    firstItem: number;
    lastItem: number;
  };
}

export type PaginatedResponse<T> = PaginatedSuccessResponse<T> | ErrorResponse;

// === ТИПЫ ДЛЯ ЗАДАЧ ===

/**
 * Прогресс выполнения задачи
 */
export interface TaskProgress {
  processed: number;
  total: number;
  percentage: number;
  estimatedTimeRemaining?: number; // в миллисекундах
  processingRate?: number; // элементов в секунду
  currentStage?: string;
  stageProgress?: {
    current: number;
    total: number;
    name: string;
  };
}

/**
 * Метрики задачи
 */
export interface TaskMetrics {
  posts?: number;
  comments?: number;
  groups?: number;
  errors?: number;
  retries?: number;
  averageProcessingTime?: number;
}

/**
 * Статус задачи с расширенной информацией
 */
export interface TaskStatusResponse {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  type: string;
  priority: number;
  progress: TaskProgress;
  metrics: TaskMetrics;
  errors: Array<{
    timestamp: string;
    message: string;
    code?: string;
    details?: any;
  }>;
  result?: any;
  error?: string;
  executionTime?: number;
  startedAt?: string;
  finishedAt?: string;
  completedAt?: string; // Alias для совместимости
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
  groups?: any[];
  parameters?: any;
}

// === ВАЛИДАЦИЯ ===

export interface ValidationError extends Error {
  name: 'ValidationError';
  details: Array<{
    message: string;
    path: string[];
    type: string;
    context?: any;
  }>;
}

export interface ValidationErrorDetails {
  field: string;
  message: string;
  value?: any;
  constraint?: string;
}

// === ПАГИНАЦИЯ ===

export interface PaginationParams {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface SortParams {
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

export interface FilterParams {
  search?: string;
  status?: string;
  type?: string;
  dateFrom?: string;
  dateTo?: string;
}

export interface QueryParams extends PaginationParams, SortParams, FilterParams {}

// === MIDDLEWARE РАСШИРЕНИЯ ===

/**
 * Расширения Express интерфейсов для middleware
 */
declare global {
  namespace Express {
    interface Request {
      id: string;
      requestId: string;
      startTime: number;
      context: {
        requestId: string;
        startTime: number;
        userAgent?: string;
        ip?: string;
        path: string;
        method: string;
      };
      file?: Express.Multer.File;
      files?: Express.Multer.File[] | { [fieldname: string]: Express.Multer.File[] };
    }

    interface Response {
      // Методы для стандартизированных ответов
      success<T>(data?: T, message?: string, meta?: any): Response;
      error(error: string | Error | any, statusCode?: number, details?: any): Response;
      paginated<T>(data: T[], pagination: any, meta?: any): Response;
      validationError(errors: Array<{ field: string; message: string; value?: any }>): Response;
    }
  }
}

// === КОДЫ ОШИБОК ===

export enum ErrorCodes {
  // Валидация
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_REQUEST = 'INVALID_REQUEST',
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD',
  INVALID_JSON = 'INVALID_JSON',
  INVALID_PARAMETER = 'INVALID_PARAMETER',

  // Аутентификация/авторизация
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  INVALID_TOKEN = 'INVALID_TOKEN',

  // Ресурсы
  NOT_FOUND = 'NOT_FOUND',
  ALREADY_EXISTS = 'ALREADY_EXISTS',
  RESOURCE_LOCKED = 'RESOURCE_LOCKED',
  RESOURCE_EXPIRED = 'RESOURCE_EXPIRED',

  // Задачи
  TASK_NOT_FOUND = 'TASK_NOT_FOUND',
  TASK_ALREADY_RUNNING = 'TASK_ALREADY_RUNNING',
  TASK_FAILED = 'TASK_FAILED',
  TASK_CANCELLED = 'TASK_CANCELLED',
  TASK_TIMEOUT = 'TASK_TIMEOUT',

  // VK API
  VK_API_ERROR = 'VK_API_ERROR',
  VK_RATE_LIMIT = 'VK_RATE_LIMIT',
  VK_INVALID_TOKEN = 'VK_INVALID_TOKEN',
  VK_ACCESS_DENIED = 'VK_ACCESS_DENIED',
  VK_API_UNAVAILABLE = 'VK_API_UNAVAILABLE',

  // Сеть и соединения
  CONNECTION_ERROR = 'CONNECTION_ERROR',
  TIMEOUT = 'TIMEOUT',
  CONNECTION_REFUSED = 'CONNECTION_REFUSED',

  // Система
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  MAINTENANCE_MODE = 'MAINTENANCE_MODE',

  // База данных
  DATABASE_ERROR = 'DATABASE_ERROR',
  MIGRATION_ERROR = 'MIGRATION_ERROR',
  TRANSACTION_FAILED = 'TRANSACTION_FAILED',

  // Файлы
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  INVALID_FILE_FORMAT = 'INVALID_FILE_FORMAT',
  FILE_PROCESSING_ERROR = 'FILE_PROCESSING_ERROR',
  FILE_NOT_FOUND = 'FILE_NOT_FOUND',
  DISK_SPACE_ERROR = 'DISK_SPACE_ERROR',

  // Очереди и фоновые задачи
  QUEUE_ERROR = 'QUEUE_ERROR',
  JOB_FAILED = 'JOB_FAILED',
  WORKER_ERROR = 'WORKER_ERROR'
}

// === РАСШИРЕННЫЕ ТИПЫ ОШИБОК ===

/**
 * Базовый интерфейс для приложения ошибок
 */
export interface AppError extends Error {
  name: string;
  message: string;
  code: ErrorCodes;
  statusCode: number;
  isOperational: boolean;
  timestamp: Date;
  requestId?: string;
  userId?: string;
  details?: any;
  cause?: Error;
  context?: Record<string, any>;
  stack?: string;
}

/**
 * Ошибка валидации с детальной информацией
 */
export interface ValidationErrorDetail {
  field: string;
  message: string;
  value?: any;
  constraint?: string;
  code?: string;
}

export interface AppValidationError extends AppError {
  code: ErrorCodes.VALIDATION_ERROR;
  details: ValidationErrorDetail[];
}

/**
 * Ошибка VK API с детальной информацией
 */
export interface VkApiErrorDetails {
  vkErrorCode?: number;
  vkErrorMessage?: string;
  method?: string;
  parameters?: Record<string, any>;
  rateLimitReset?: Date;
}

export interface AppVkApiError extends AppError {
  code: ErrorCodes.VK_API_ERROR | ErrorCodes.VK_RATE_LIMIT | ErrorCodes.VK_INVALID_TOKEN;
  details: VkApiErrorDetails;
}

/**
 * Ошибка задачи с контекстом выполнения
 */
export interface TaskErrorContext {
  taskId: string;
  taskType: string;
  phase?: string;
  progress?: number;
  retryCount?: number;
  maxRetries?: number;
}

export interface AppTaskError extends AppError {
  code: ErrorCodes.TASK_NOT_FOUND | ErrorCodes.TASK_FAILED | ErrorCodes.TASK_TIMEOUT;
  context: TaskErrorContext;
}

/**
 * Ошибка базы данных
 */
export interface DatabaseErrorContext {
  operation: string;
  table?: string;
  query?: string;
  constraint?: string;
  connection?: string;
}

export interface AppDatabaseError extends AppError {
  code: ErrorCodes.DATABASE_ERROR | ErrorCodes.TRANSACTION_FAILED;
  context: DatabaseErrorContext;
}

/**
 * Контекст ошибок для различных операций
 */
export interface ErrorContext {
  // HTTP контекст
  method?: string;
  url?: string;
  userAgent?: string;
  ip?: string;
  headers?: Record<string, string>;
  body?: any;

  // Пользовательский контекст
  userId?: string;
  sessionId?: string;

  // Системный контекст
  version?: string;
  environment?: string;
  hostname?: string;
  pid?: number;

  // Временные метки
  timestamp?: Date;
  duration?: number;

  // Дополнительная информация
  tags?: string[];
  metadata?: Record<string, any>;
}