/**
 * @fileoverview Zod validation schemas для Groups domain
 *
 * Используйте validateSchema() helper для runtime валидации
 * Zod автоматически генерирует TypeScript типы из схем
 *
 * @example
 * import { validateSchema, GetGroupsQuerySchema } from '@/domain/groups/schemas';
 *
 * const validated = validateSchema(GetGroupsQuerySchema, req.query);
 * // validated имеет тип GetGroupsQuery с гарантированной валидностью
 */

import { z } from 'zod';
import { ValidationError } from './errors';

// ============ File Upload Validation ============

/**
 * Схема валидации для загрузки файла с группами
 */
export const UploadGroupsRequestSchema = z.object({
  file: z
    .instanceof(Buffer)
    .refine(
      (buf) => buf.length > 0 && buf.length <= 10 * 1024 * 1024,
      {
        message: 'File must be between 1 byte and 10MB',
      }
    ),
  encoding: z
    .enum(['utf-8', 'utf-16le', 'latin1', 'ascii'])
    .default('utf-8')
    .describe('File encoding for parsing'),
});

/**
 * Схема валидации для VK group ID
 */
export const VkGroupIdSchema = z
  .number()
  .int()
  .positive()
  .max(999_999_999, 'VK group ID must be less than 1 billion')
  .describe('Valid VK group ID');

/**
 * Схема валидации для VK screen_name
 */
export const VkScreenNameSchema = z
  .string()
  .min(5, 'Screen name must be at least 5 characters')
  .max(32, 'Screen name must be at most 32 characters')
  .regex(
    /^[a-zA-Z][a-zA-Z0-9_]{4,31}$/,
    'Screen name must start with a letter and contain only letters, numbers, and underscores'
  )
  .describe('Valid VK screen_name');

// ============ Query Validation ============

/**
 * Схема валидации для получения списка групп
 */
export const GetGroupsQuerySchema = z.object({
  limit: z.coerce
    .number()
    .int()
    .positive()
    .max(10000, 'Maximum limit is 10000')
    .default(20)
    .describe('Количество записей на странице (1-10000)'),

  offset: z.coerce
    .number()
    .int()
    .nonnegative()
    .default(0)
    .describe('Смещение для пагинации (0+)'),

  status: z
    .enum(['all', 'valid', 'invalid', 'duplicate'])
    .default('all')
    .describe('Фильтр по статусу группы'),

  search: z
    .string()
    .max(255, 'Search query too long')
    .optional()
    .describe('Поиск по ID или названию группы'),

  sortBy: z
    .enum(['uploaded_at', 'name', 'members_count', 'status'])
    .default('uploaded_at')
    .describe('Поле для сортировки'),

  sortOrder: z
    .enum(['asc', 'desc'])
    .default('desc')
    .describe('Направление сортировки (asc/desc)'),
});

/**
 * Схема валидации для получения конкретной группы
 */
export const GetGroupByIdSchema = z.object({
  groupId: z.coerce
    .number()
    .int()
    .positive()
    .describe('ID группы в базе данных'),
});

/**
 * Схема валидации для получения статуса задачи
 */
export const GetTaskStatusSchema = z.object({
  taskId: z
    .string()
    .uuid('Task ID must be a valid UUID')
    .describe('UUID задачи загрузки'),
});

// ============ Mutation Validation ============

/**
 * Схема валидации для удаления одной группы
 */
export const DeleteGroupSchema = z.object({
  groupId: z.coerce
    .number()
    .int()
    .positive()
    .describe('ID группы для удаления'),
});

/**
 * Схема валидации для массового удаления групп
 */
export const DeleteGroupsRequestSchema = z.object({
  groupIds: z
    .array(z.number().int().positive())
    .min(1, 'At least one group ID is required')
    .max(1000, 'Maximum 1000 groups can be deleted at once')
    .describe('Массив ID групп для удаления'),
});

/**
 * Схема валидации для обновления статуса группы
 */
export const UpdateGroupStatusSchema = z.object({
  groupId: z.coerce
    .number()
    .int()
    .positive()
    .describe('ID группы для обновления'),

  status: z
    .enum(['valid', 'invalid', 'duplicate'])
    .describe('Новый статус группы'),
});

/**
 * Схема валидации для cleanup параметров
 */
export const CleanupOldTasksSchema = z.object({
  olderThanHours: z
    .number()
    .int()
    .positive()
    .max(720, 'Maximum 30 days (720 hours)')
    .default(24)
    .describe('Удалить задачи старше N часов'),
});

// ============ Auto-Generated TypeScript Types ============

/**
 * Автогенерированные TypeScript типы из Zod схем
 * Используйте эти типы вместо ручного определения интерфейсов
 */
export type UploadGroupsRequest = z.infer<typeof UploadGroupsRequestSchema>;
export type GetGroupsQuery = z.infer<typeof GetGroupsQuerySchema>;
export type GetGroupByIdParams = z.infer<typeof GetGroupByIdSchema>;
export type GetTaskStatusParams = z.infer<typeof GetTaskStatusSchema>;
export type DeleteGroupParams = z.infer<typeof DeleteGroupSchema>;
export type DeleteGroupsRequest = z.infer<typeof DeleteGroupsRequestSchema>;
export type UpdateGroupStatusRequest = z.infer<typeof UpdateGroupStatusSchema>;
export type CleanupOldTasksParams = z.infer<typeof CleanupOldTasksSchema>;

// ============ Runtime Validation Helpers ============

/**
 * Валидирует данные через Zod schema (синхронно)
 *
 * @throws ValidationError если данные не валидны
 * @returns Провалидированные и типизированные данные
 *
 * @example
 * ```typescript
 * const query = validateSchema(GetGroupsQuerySchema, req.query);
 * // query гарантированно имеет тип GetGroupsQuery и валиден
 * ```
 */
export function validateSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): T {
  const result = schema.safeParse(data);

  if (!result.success) {
    const fieldErrors = result.error.flatten().fieldErrors;
    const formattedErrors = result.error.flatten().formErrors;

    throw new ValidationError(
      'Schema validation failed',
      'SCHEMA_VALIDATION_ERROR',
      400,
      {
        fieldErrors,
        formErrors: formattedErrors,
        issues: result.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message,
          code: issue.code,
        })),
      }
    );
  }

  return result.data;
}

/**
 * Async версия validateSchema для асинхронных схем с refinements
 *
 * @throws ValidationError если данные не валидны
 * @returns Promise с провалидированными данными
 */
export async function validateSchemaAsync<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): Promise<T> {
  const result = await schema.safeParseAsync(data);

  if (!result.success) {
    const fieldErrors = result.error.flatten().fieldErrors;
    const formattedErrors = result.error.flatten().formErrors;

    throw new ValidationError(
      'Schema validation failed',
      'SCHEMA_VALIDATION_ERROR',
      400,
      {
        fieldErrors,
        formErrors: formattedErrors,
        issues: result.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message,
          code: issue.code,
        })),
      }
    );
  }

  return result.data;
}

/**
 * Парсит данные через схему, возвращая результат или null
 * Не выбрасывает ошибки, полезно для optional validation
 *
 * @returns Провалидированные данные или null если невалидны
 */
export function tryValidateSchema<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): T | null {
  const result = schema.safeParse(data);
  return result.success ? result.data : null;
}

/**
 * Проверяет валидность данных без парсинга
 * Полезно для быстрой проверки без создания нового объекта
 */
export function isSchemaValid<T>(
  schema: z.ZodSchema<T>,
  data: unknown
): boolean {
  return schema.safeParse(data).success;
}

// ============ Composite Schemas ============

/**
 * Схема для batch операций с группами
 */
export const BatchGroupOperationSchema = z.object({
  groupIds: z
    .array(z.number().int().positive())
    .min(1)
    .max(1000),
  operation: z.enum(['delete', 'activate', 'deactivate', 'mark_invalid']),
});

export type BatchGroupOperation = z.infer<typeof BatchGroupOperationSchema>;

/**
 * Схема для фильтров в поиске групп
 */
export const GroupFiltersSchema = z.object({
  minMembers: z.number().int().nonnegative().optional(),
  maxMembers: z.number().int().positive().optional(),
  isClosed: z.enum(['0', '1', '2']).optional(),
  hasDescription: z.boolean().optional(),
  uploadedAfter: z.coerce.date().optional(),
  uploadedBefore: z.coerce.date().optional(),
}).refine(
  (data) => {
    if (data.minMembers && data.maxMembers) {
      return data.minMembers <= data.maxMembers;
    }
    return true;
  },
  {
    message: 'minMembers must be less than or equal to maxMembers',
    path: ['minMembers'],
  }
).refine(
  (data) => {
    if (data.uploadedAfter && data.uploadedBefore) {
      return data.uploadedAfter <= data.uploadedBefore;
    }
    return true;
  },
  {
    message: 'uploadedAfter must be before uploadedBefore',
    path: ['uploadedAfter'],
  }
);

export type GroupFilters = z.infer<typeof GroupFiltersSchema>;

/**
 * Схема для экспорта групп
 */
export const ExportGroupsSchema = z.object({
  format: z.enum(['json', 'csv', 'txt']),
  filters: GroupFiltersSchema.optional(),
  includeFields: z
    .array(z.enum(['id', 'vkId', 'name', 'screenName', 'membersCount', 'description', 'status']))
    .optional(),
});

export type ExportGroupsParams = z.infer<typeof ExportGroupsSchema>;
