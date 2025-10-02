/**
 * Константы для сообщений об ошибках
 */

export const ERROR_MESSAGES = {
  // Ошибки задач
  TASK_NOT_FOUND: 'Task not found',
  TASK_CREATION_FAILED: 'Failed to create task',
  TASK_UPDATE_FAILED: 'Failed to update task',
  TASK_DELETE_FAILED: 'Failed to delete task data',

  // Ошибки постов
  POST_CREATION_FAILED: 'Failed to create posts',
  POST_UPSERT_FAILED: 'Failed to upsert posts',
  POST_NOT_FOUND: 'Post not found',

  // Ошибки комментариев
  COMMENT_CREATION_FAILED: 'Failed to create comments',
  COMMENT_UPSERT_FAILED: 'Failed to upsert comments',

  // Ошибки групп
  GROUP_NOT_FOUND: 'Group not found',
  GROUP_CREATION_FAILED: 'Failed to create groups',
  GROUP_UPDATE_FAILED: 'Failed to update group',
  GROUP_DELETE_FAILED: 'Failed to delete group',
  GROUP_STATS_FAILED: 'Failed to get groups stats',

  // Общие ошибки
  VALIDATION_ERROR: 'Validation error',
  DATABASE_ERROR: 'Database operation failed',
  UNKNOWN_ERROR: 'Unknown error occurred',

  // Ошибки получения данных
  FETCH_TASKS_FAILED: 'Failed to get tasks',
  FETCH_RESULTS_FAILED: 'Failed to get results',
  FETCH_STATS_FAILED: 'Failed to get stats'
} as const;

export const ERROR_CODES = {
  ENTITY_NOT_FOUND: 'ENTITY_NOT_FOUND',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  DUPLICATE_ENTITY: 'DUPLICATE_ENTITY',
  PERMISSION_DENIED: 'PERMISSION_DENIED'
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];