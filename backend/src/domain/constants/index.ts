/**
 * Константы для статусов и типов задач, групп и других сущностей
 */

// Статусы задач
export const TASK_STATUSES = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
} as const;

// Типы задач
export const TASK_TYPES = {
  FETCH_COMMENTS: 'fetch_comments',
  PROCESS_GROUPS: 'process_groups',
  ANALYZE_POSTS: 'analyze_posts'
} as const;

// Статусы групп
export const GROUP_STATUSES = {
  VALID: 'valid',
  INVALID: 'invalid',
  DUPLICATE: 'duplicate'
} as const;

// Настройки пагинации по умолчанию
export const PAGINATION_DEFAULTS = {
  LIMIT: 20,
  OFFSET: 0,
  MAX_LIMIT: 1000
} as const;

// Приоритеты задач
export const TASK_PRIORITIES = {
  LOW: 0,
  NORMAL: 5,
  HIGH: 10,
  CRITICAL: 15
} as const;

// Системные значения по умолчанию
export const DEFAULT_VALUES = {
  CREATED_BY: 'system',
  LIKES_COUNT: 0,
  PROGRESS_INITIAL: 0,
  IS_CLOSED_DEFAULT: 0
} as const;

// Настройки сортировки
export const SORT_ORDERS = {
  ASC: 'asc',
  DESC: 'desc'
} as const;

// Типы для TypeScript
export type TaskStatus = typeof TASK_STATUSES[keyof typeof TASK_STATUSES];
export type TaskType = typeof TASK_TYPES[keyof typeof TASK_TYPES];
export type GroupStatus = typeof GROUP_STATUSES[keyof typeof GROUP_STATUSES];
export type SortOrder = typeof SORT_ORDERS[keyof typeof SORT_ORDERS];
export type TaskPriority = typeof TASK_PRIORITIES[keyof typeof TASK_PRIORITIES];