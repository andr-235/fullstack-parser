/**
 * @fileoverview HTTP схемы валидации для Tasks API endpoints
 *
 * PRESENTATION LAYER
 * - Валидация HTTP запросов для операций с задачами
 * - Схемы для создания, получения и управления задачами
 * - Type-safe через Zod
 */

import { z } from 'zod';
import {
  PaginationQuerySchema,
  createSortSchema,
  createIdParamSchema,
  DateRangeQuerySchema
} from './common.schemas';

// ============ Create Task Schemas ============

/**
 * Схема для создания задачи сбора комментариев из VK
 *
 * @example
 * POST /api/tasks
 * Body: {
 *   postUrl: "https://vk.com/wall-12345_67890",
 *   depth: 2
 * }
 */
export const CreateVkCollectTaskBodySchema = z.object({
  postUrl: z
    .string()
    .url('Невалидный URL')
    .regex(
      /^https?:\/\/(www\.)?vk\.com\/wall-?\d+_\d+/,
      'URL должен быть ссылкой на пост VK (например: https://vk.com/wall-123_456)'
    )
    .describe('URL поста VK для сбора комментариев'),

  depth: z
    .number()
    .int('Глубина должна быть целым числом')
    .min(1, 'Минимальная глубина: 1')
    .max(10, 'Максимальная глубина: 10')
    .default(1)
    .describe('Глубина вложенности комментариев (1-10)'),

  includeReplies: z
    .boolean()
    .default(true)
    .describe('Собирать ли ответы на комментарии'),

  maxComments: z
    .number()
    .int()
    .positive()
    .max(100000, 'Максимум 100000 комментариев')
    .optional()
    .describe('Максимальное количество комментариев для сбора')
});

/**
 * Схема для создания generic задачи
 *
 * @example
 * POST /api/tasks
 * Body: {
 *   type: "vk_collect",
 *   params: { ... }
 * }
 */
export const CreateTaskBodySchema = z.object({
  type: z
    .enum(['vk_collect', 'group_upload', 'data_export'])
    .describe('Тип задачи'),

  params: z
    .record(z.string(), z.any())
    .describe('Параметры задачи (зависят от типа)'),

  priority: z
    .enum(['low', 'normal', 'high', 'critical'])
    .default('normal')
    .describe('Приоритет выполнения задачи'),

  scheduledAt: z.coerce
    .date()
    .optional()
    .describe('Время запланированного запуска (если не сразу)')
});

// ============ Get Tasks Schemas ============

/**
 * Схема для получения списка задач
 *
 * @example
 * GET /api/tasks?page=1&limit=20&status=completed&type=vk_collect
 */
const tasksSortSchema = createSortSchema(
  ['id', 'createdAt', 'updatedAt', 'status', 'priority'] as const,
  'createdAt'
);

export const GetTasksQuerySchema = z.object({
  ...PaginationQuerySchema.shape,
  ...tasksSortSchema.shape,
  ...DateRangeQuerySchema.shape,
  status: z
    .enum(['all', 'pending', 'processing', 'completed', 'failed', 'cancelled'])
    .default('all')
    .describe('Фильтр по статусу задачи'),

  type: z
    .enum(['all', 'vk_collect', 'group_upload', 'data_export'])
    .default('all')
    .describe('Фильтр по типу задачи'),

  priority: z
    .enum(['all', 'low', 'normal', 'high', 'critical'])
    .default('all')
    .describe('Фильтр по приоритету')
});

/**
 * Схема для получения одной задачи по ID
 *
 * @example
 * GET /api/tasks/:id
 */
export const GetTaskByIdParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для получения задачи по UUID
 *
 * @example
 * GET /api/tasks/:taskId
 */
export const GetTaskByUuidParamSchema = z.object({
  taskId: z
    .string()
    .uuid('Task ID должен быть валидным UUID')
    .describe('UUID задачи')
});

// ============ Update Task Schemas ============

/**
 * Схема для обновления статуса задачи
 *
 * @example
 * PATCH /api/tasks/:id/status
 * Body: { status: "cancelled", reason: "User requested" }
 */
export const UpdateTaskStatusParamSchema = createIdParamSchema('id', 'number');

export const UpdateTaskStatusBodySchema = z.object({
  status: z
    .enum(['pending', 'processing', 'completed', 'failed', 'cancelled'])
    .describe('Новый статус задачи'),

  reason: z
    .string()
    .max(500, 'Причина не может превышать 500 символов')
    .optional()
    .describe('Причина изменения статуса')
});

/**
 * Схема для обновления приоритета задачи
 *
 * @example
 * PATCH /api/tasks/:id/priority
 * Body: { priority: "high" }
 */
export const UpdateTaskPriorityBodySchema = z.object({
  priority: z
    .enum(['low', 'normal', 'high', 'critical'])
    .describe('Новый приоритет задачи')
});

// ============ Task Results Schemas ============

/**
 * Схема для получения результатов задачи
 *
 * @example
 * GET /api/tasks/:id/results?format=json
 */
export const GetTaskResultsParamSchema = createIdParamSchema('id', 'number');

export const GetTaskResultsQuerySchema = z.object({
  format: z
    .enum(['json', 'csv', 'txt'])
    .default('json')
    .describe('Формат результатов'),

  download: z
    .enum(['true', 'false', '1', '0'])
    .transform(val => val === 'true' || val === '1')
    .optional()
    .describe('Скачать как файл или вернуть в ответе')
});

// ============ Task Progress Schemas ============

/**
 * Схема для получения прогресса задачи
 *
 * @example
 * GET /api/tasks/:id/progress
 */
export const GetTaskProgressParamSchema = createIdParamSchema('id', 'number');

// ============ Cancel/Delete Task Schemas ============

/**
 * Схема для отмены задачи
 *
 * @example
 * POST /api/tasks/:id/cancel
 */
export const CancelTaskParamSchema = createIdParamSchema('id', 'number');

export const CancelTaskBodySchema = z.object({
  reason: z
    .string()
    .max(500)
    .optional()
    .describe('Причина отмены задачи')
});

/**
 * Схема для удаления задачи
 *
 * @example
 * DELETE /api/tasks/:id
 */
export const DeleteTaskParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для массового удаления задач
 *
 * @example
 * DELETE /api/tasks
 * Body: { taskIds: [1, 2, 3] }
 */
export const BatchDeleteTasksBodySchema = z.object({
  taskIds: z
    .array(z.number().int().positive())
    .min(1, 'Необходимо указать хотя бы один ID задачи')
    .max(100, 'Максимум 100 задач за раз')
    .describe('Массив ID задач для удаления'),

  deleteResults: z
    .boolean()
    .default(false)
    .describe('Удалить ли также результаты задач')
});

// ============ Task Statistics Schemas ============

/**
 * Схема для получения статистики по задачам
 *
 * @example
 * GET /api/tasks/stats?period=week
 */
export const GetTaskStatsQuerySchema = z.object({
  period: z
    .enum(['day', 'week', 'month', 'year', 'all'])
    .default('week')
    .describe('Период для статистики'),

  groupBy: z
    .enum(['status', 'type', 'priority', 'day'])
    .default('status')
    .describe('Группировка статистики')
});

// ============ Auto-Generated Types ============

/**
 * Автогенерированные TypeScript типы из Zod схем
 */
export type CreateVkCollectTaskBody = z.infer<typeof CreateVkCollectTaskBodySchema>;
export type CreateTaskBody = z.infer<typeof CreateTaskBodySchema>;
export type GetTasksQuery = z.infer<typeof GetTasksQuerySchema>;
export type GetTaskByIdParam = z.infer<typeof GetTaskByIdParamSchema>;
export type GetTaskByUuidParam = z.infer<typeof GetTaskByUuidParamSchema>;
export type UpdateTaskStatusParam = z.infer<typeof UpdateTaskStatusParamSchema>;
export type UpdateTaskStatusBody = z.infer<typeof UpdateTaskStatusBodySchema>;
export type UpdateTaskPriorityBody = z.infer<typeof UpdateTaskPriorityBodySchema>;
export type GetTaskResultsParam = z.infer<typeof GetTaskResultsParamSchema>;
export type GetTaskResultsQuery = z.infer<typeof GetTaskResultsQuerySchema>;
export type GetTaskProgressParam = z.infer<typeof GetTaskProgressParamSchema>;
export type CancelTaskParam = z.infer<typeof CancelTaskParamSchema>;
export type CancelTaskBody = z.infer<typeof CancelTaskBodySchema>;
export type DeleteTaskParam = z.infer<typeof DeleteTaskParamSchema>;
export type BatchDeleteTasksBody = z.infer<typeof BatchDeleteTasksBodySchema>;
export type GetTaskStatsQuery = z.infer<typeof GetTaskStatsQuerySchema>;

// ============ Response Types (документация) ============

/**
 * Типы для ответов API (не валидируются, только для документации)
 */
export interface TaskListItem {
  id: number;
  type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  priority: 'low' | 'normal' | 'high' | 'critical';
  progress: {
    total: number;
    processed: number;
    percentage: number;
  };
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
}

export interface TaskDetails extends TaskListItem {
  params: Record<string, any>;
  result?: any;
  error?: string;
  logs?: string[];
}

export interface TaskStats {
  total: number;
  byStatus: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
    cancelled: number;
  };
  byType: Record<string, number>;
  byPriority: {
    low: number;
    normal: number;
    high: number;
    critical: number;
  };
}
