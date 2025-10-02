/**
 * @fileoverview HTTP схемы валидации для Groups API endpoints
 *
 * PRESENTATION LAYER
 * - Валидация HTTP запросов для операций с группами
 * - Переиспользует domain схемы для бизнес-правил
 * - Type-safe через Zod
 */

import { z } from 'zod';
import {
  PaginationQuerySchema,
  createSortSchema,
  SearchQuerySchema,
  createIdParamSchema,
  createRangeSchema
} from './common.schemas';

// ============ File Upload Schemas ============

/**
 * Схема для query параметров при загрузке файла
 *
 * @example
 * POST /api/groups/upload?encoding=utf-8
 */
export const UploadGroupsQuerySchema = z.object({
  encoding: z
    .enum(['utf-8', 'utf8', 'utf-16le', 'latin1', 'ascii', 'base64', 'hex'])
    .default('utf-8')
    .transform(val => (val === 'utf8' ? 'utf-8' : val) as BufferEncoding)
    .describe('Кодировка файла для парсинга')
});

/**
 * Валидация загруженного файла (используется в multer middleware)
 * Эта схема не используется напрямую, но документирует ожидаемую структуру
 */
export const UploadedFileSchema = z.object({
  fieldname: z.string(),
  originalname: z.string().min(1, 'Имя файла не может быть пустым'),
  encoding: z.string(),
  mimetype: z.string(),
  size: z
    .number()
    .positive('Размер файла должен быть больше 0')
    .max(10 * 1024 * 1024, 'Максимальный размер файла: 10MB'),
  buffer: z.instanceof(Buffer)
});

// ============ Get Groups Schemas ============

/**
 * Схема для получения списка групп с фильтрацией
 *
 * @example
 * GET /api/groups?page=1&limit=20&status=valid&search=музыка&sortBy=name&sortOrder=asc
 */
export const GetGroupsQuerySchema = PaginationQuerySchema
  .merge(
    createSortSchema(
      ['id', 'name', 'vkId', 'createdAt', 'updatedAt', 'uploadedAt', 'uploaded_at'] as const,
      'id'
    )
  )
  .merge(SearchQuerySchema)
  .extend({
    status: z
      .enum(['all', 'valid', 'invalid', 'duplicate'])
      .default('all')
      .describe('Фильтр по статусу группы'),

    // Дополнительные фильтры
    isClosed: z
      .enum(['0', '1', '2'])
      .optional()
      .describe('Фильтр по типу группы (0=открытая, 1=закрытая, 2=частная)'),

    hasDescription: z
      .enum(['true', 'false', '1', '0'])
      .transform(val => val === 'true' || val === '1')
      .optional()
      .describe('Фильтр по наличию описания')
  })
  .merge(createRangeSchema('members')); // minMembers, maxMembers

/**
 * Схема для получения одной группы по ID
 *
 * @example
 * GET /api/groups/:id
 */
export const GetGroupByIdParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для получения статистики по группам
 * Нет параметров, но включаем для полноты
 *
 * @example
 * GET /api/groups/stats
 */
export const GetGroupStatsQuerySchema = z.object({}).optional();

// ============ Delete Groups Schemas ============

/**
 * Схема для удаления одной группы
 *
 * @example
 * DELETE /api/groups/:id
 */
export const DeleteGroupParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для массового удаления групп
 *
 * @example
 * DELETE /api/groups
 * Body: { groupIds: [1, 2, 3] }
 */
export const BatchDeleteGroupsBodySchema = z.object({
  groupIds: z
    .array(z.number().int().positive())
    .min(1, 'Необходимо указать хотя бы один ID группы')
    .max(1000, 'Максимум 1000 групп за раз')
    .describe('Массив ID групп для удаления')
});

// ============ Update Group Schemas ============

/**
 * Схема для обновления статуса группы
 *
 * @example
 * PATCH /api/groups/:id/status
 * Body: { status: "invalid" }
 */
export const UpdateGroupStatusParamSchema = createIdParamSchema('id', 'number');

export const UpdateGroupStatusBodySchema = z.object({
  status: z
    .enum(['valid', 'invalid', 'duplicate'])
    .describe('Новый статус группы'),

  reason: z
    .string()
    .max(500, 'Причина не может превышать 500 символов')
    .optional()
    .describe('Причина изменения статуса (опционально)')
});

// ============ Export/Import Schemas ============

/**
 * Схема для экспорта групп в различных форматах
 *
 * @example
 * GET /api/groups/export?format=csv&status=valid
 */
export const ExportGroupsQuerySchema = z.object({
  format: z
    .enum(['json', 'csv', 'txt', 'xlsx'])
    .default('json')
    .describe('Формат экспорта'),

  status: z
    .enum(['all', 'valid', 'invalid', 'duplicate'])
    .default('all')
    .describe('Фильтр по статусу для экспорта'),

  includeFields: z
    .array(
      z.enum([
        'id',
        'vkId',
        'name',
        'screenName',
        'membersCount',
        'description',
        'status',
        'photo50',
        'isClosed',
        'uploadedAt'
      ])
    )
    .optional()
    .describe('Поля для включения в экспорт (если не указано - все)')
});

// ============ Batch Operations Schemas ============

/**
 * Схема для batch операций над группами
 *
 * @example
 * POST /api/groups/batch
 * Body: { groupIds: [1,2,3], operation: "mark_invalid" }
 */
export const BatchGroupOperationBodySchema = z.object({
  groupIds: z
    .array(z.number().int().positive())
    .min(1, 'Необходимо указать хотя бы один ID')
    .max(1000, 'Максимум 1000 групп за раз'),

  operation: z
    .enum([
      'delete',
      'mark_valid',
      'mark_invalid',
      'mark_duplicate',
      'refresh_info'
    ])
    .describe('Операция для выполнения'),

  reason: z
    .string()
    .max(500)
    .optional()
    .describe('Причина операции (для mark_invalid)')
});

// ============ Task Status Schemas ============

/**
 * Схема для получения статуса задачи загрузки
 *
 * @example
 * GET /api/groups/tasks/:taskId
 */
export const GetGroupTaskStatusParamSchema = z.object({
  taskId: z
    .string()
    .uuid('Task ID должен быть валидным UUID')
    .describe('UUID задачи загрузки групп')
});

// ============ Auto-Generated Types ============

/**
 * Автогенерированные TypeScript типы из Zod схем
 * Используйте эти типы в контроллерах и handlers
 */
export type UploadGroupsQuery = z.infer<typeof UploadGroupsQuerySchema>;
export type UploadedFile = z.infer<typeof UploadedFileSchema>;
export type GetGroupsQuery = z.infer<typeof GetGroupsQuerySchema>;
export type GetGroupByIdParam = z.infer<typeof GetGroupByIdParamSchema>;
export type GetGroupStatsQuery = z.infer<typeof GetGroupStatsQuerySchema>;
export type DeleteGroupParam = z.infer<typeof DeleteGroupParamSchema>;
export type BatchDeleteGroupsBody = z.infer<typeof BatchDeleteGroupsBodySchema>;
export type UpdateGroupStatusParam = z.infer<typeof UpdateGroupStatusParamSchema>;
export type UpdateGroupStatusBody = z.infer<typeof UpdateGroupStatusBodySchema>;
export type ExportGroupsQuery = z.infer<typeof ExportGroupsQuerySchema>;
export type BatchGroupOperationBody = z.infer<typeof BatchGroupOperationBodySchema>;
export type GetGroupTaskStatusParam = z.infer<typeof GetGroupTaskStatusParamSchema>;

// ============ Response Types (документация) ============

/**
 * Типы для ответов API (не валидируются, только для документации)
 */
export interface GroupListItem {
  id: number;
  vkId: number;
  name: string;
  screenName: string | null;
  photo50: string | null;
  description: string | null;
  membersCount: number | null;
  isClosed: number;
  status: string;
  uploadedAt: string;
  vkUrl: string;
}

export interface GroupStats {
  total: number;
  valid: number;
  invalid: number;
  duplicate: number;
  byIsClosed: {
    open: number;
    closed: number;
    private: number;
  };
}

export interface UploadTaskStatus {
  taskId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: {
    total: number;
    processed: number;
    valid: number;
    invalid: number;
    duplicate: number;
  };
  errors?: string[];
  startedAt?: string;
  completedAt?: string;
}
