/**
 * Стандартизированные типы для API ответов
 * Дополняет существующие типы в express.ts
 */

// === БАЗОВЫЕ ИНТЕРФЕЙСЫ ===

/**
 * Стандартизированный базовый ответ API
 */
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
  requestId: string;
  executionTime?: number;
}

/**
 * Пагинированный ответ API
 */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
  executionTime?: number;
}

/**
 * Ответ с прогрессом задачи
 */
export interface TaskProgressResponse extends ApiResponse {
  data: {
    id: number;
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
    type: string;
    progress: {
      processed: number;
      total: number;
      percentage: number;
      phase?: 'groups' | 'posts' | 'comments';
      estimatedTimeRemaining?: number;
      processingRate?: number;
    };
    metrics: {
      posts: number;
      comments: number;
      groups?: number;
      errors: number;
    };
    startedAt?: string;
    completedAt?: string;
    error?: string;
    result?: any;
  };
}

// === РАСШИРЕННЫЕ ОШИБКИ ===

/**
 * Детализированная ошибка API
 */
export interface ApiErrorResponse extends ApiResponse {
  success: false;
  error: string;
  details?: {
    code: string;
    field?: string;
    value?: any;
    constraint?: string;
    stack?: string; // Только для development
  };
}

/**
 * Ошибка валидации
 */
export interface ValidationErrorResponse extends ApiErrorResponse {
  success: false;
  details: {
    code: 'VALIDATION_ERROR';
    validationErrors: Array<{
      code?: string;
      field: string;
      message: string;
      value?: any;
      constraint?: string;
    }>;
    stack?: string;
  };
  executionTime?: number;
}

// === ТИПЫ ДЛЯ КОНКРЕТНЫХ КОНТРОЛЛЕРОВ ===

/**
 * Ответ создания задачи
 */
export interface TaskCreateResponse extends ApiResponse {
  data: {
    taskId: number;
    status: 'created' | 'pending';
    type: string;
    createdAt: string;
  };
}

/**
 * Ответ списка задач
 */
export interface TaskListResponse extends PaginatedResponse<{
  id: number;
  status: string;
  type: string;
  priority: number;
  progress: {
    processed: number;
    total: number;
    percentage: number;
  };
  metrics: {
    posts: number;
    comments: number;
    errors: number;
  };
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
}> {}

/**
 * Ответ загрузки групп
 */
export interface GroupsUploadResponse extends ApiResponse {
  data: {
    taskId: string;
    totalGroups: number;
    validGroups: number;
    invalidGroups: number;
    duplicateGroups: number;
    status: 'processing' | 'completed' | 'failed';
  };
}

/**
 * Ответ списка групп
 */
export interface GroupsListResponse extends PaginatedResponse<GroupsListItem> {}

/**
 * Ответ статистики групп
 */
export interface GroupsStatsResponse extends ApiResponse {
  data: {
    totalGroups: number;
    activeGroups: number;
    inactiveGroups: number;
    errorGroups: number;
    totalPosts: number;
    totalComments: number;
    lastUpdated: string;
    groupsByStatus: Record<string, number>;
  };
}

// Новые типы для groupsController рефакторинга
export interface BatchDeleteRequest {
  groupIds: number[];
}

export interface GetGroupsRequest extends PaginationQuery {
  status?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

export interface GroupsDeleteResponse extends ApiResponse {
  data?: {
    deletedCount: number;
    message: string;
  };
}

export interface GroupsListItem {
  id: number;
  vkId: number;
  name: string;
  status: string;
  uploadedAt: string;
  taskId?: string;
  lastProcessedAt?: string;
  postsCount?: number;
  commentsCount?: number;
}

// Улучшенный тип для upload status
export interface GroupsUploadStatusResponse extends ApiResponse {
  data: {
    taskId: string;
    status: 'created' | 'processing' | 'completed' | 'failed';
    progress: {
      processed: number;
      total: number;
      percentage: number;
    };
    errors: string[];
    validGroups: number;
    invalidGroups: number;
    duplicates: number;
  };
}

// === УТИЛИТАРНЫЕ ТИПЫ ===

/**
 * Статус ответа HTTP
 */
export type ApiStatusCode = 200 | 201 | 400 | 401 | 403 | 404 | 409 | 422 | 429 | 500 | 503;

/**
 * Метаданные ответа
 */
export interface ResponseMeta {
  executionTime?: number;
  cacheHit?: boolean;
  rateLimitRemaining?: number;
  deprecation?: {
    version: string;
    sunset: string;
    link: string;
  };
}

/**
 * Расширенный API ответ с метаданными
 */
export interface ApiResponseWithMeta<T = any> extends ApiResponse<T> {
  executionTime?: number;
  meta?: ResponseMeta;
}

/**
 * Расширенный пагинированный ответ с метаданными
 */
export interface PaginatedResponseWithMeta<T> extends PaginatedResponse<T> {
  executionTime?: number;
  meta?: ResponseMeta;
}

/**
 * Расширенный ответ ошибки валидации с метаданными
 */
export interface ValidationErrorResponseWithMeta extends ValidationErrorResponse {
  executionTime?: number;
  meta?: ResponseMeta;
}

// === ТИПЫ ДЛЯ MIDDLEWARE ===

/**
 * Контекст запроса для форматирования ответов
 */
export interface RequestContext {
  requestId: string;
  startTime: number;
  userAgent?: string;
  ip?: string;
  path: string;
  method: string;
}

/**
 * Опции форматирования ответа
 */
export interface ResponseFormatOptions {
  includeTimestamp?: boolean;
  includeRequestId?: boolean;
  includeMeta?: boolean;
  sanitizeError?: boolean;
}

// === КОНФИГУРАЦИЯ ===

/**
 * Настройки форматирования API ответов
 */
export interface ApiResponseConfig {
  includeStackTrace: boolean;
  sanitizeErrors: boolean;
  defaultPaginationLimit: number;
  maxPaginationLimit: number;
  timestampFormat: 'iso' | 'unix' | 'custom';
  errorCodes: Record<string, { message: string; statusCode: number }>;
}

// === ВАЛИДАЦИОННЫЕ СХЕМЫ ===

/**
 * Типы для валидации пагинации
 */
export interface PaginationQuery {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

/**
 * Типы для валидации фильтров
 */
export interface FilterQuery {
  search?: string;
  status?: string;
  type?: string;
  dateFrom?: string;
  dateTo?: string;
}

/**
 * Объединенные параметры запроса
 */
export interface StandardQuery extends PaginationQuery, FilterQuery {}

// === ЭКСПОРТ СОВМЕСТИМОСТИ ===

/**
 * Legacy типы для обратной совместимости
 * @deprecated Используйте новые типы выше
 */
export type LegacyApiResponse<T = any> = {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
};

/**
 * Legacy пагинированный ответ
 * @deprecated Используйте PaginatedResponse
 */
export type LegacyPaginatedResponse<T> = {
  success: boolean;
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
};