/**
 * @fileoverview Общие схемы валидации для HTTP запросов
 *
 * PRESENTATION LAYER
 * - Переиспользуемые схемы для pagination, sorting, filtering
 * - Общие параметры запросов
 * - Type-safe валидация через Zod
 */

import { z } from 'zod';

// ============ Pagination Schemas ============

/**
 * Схема валидации для пагинации на основе номера страницы
 *
 * @example
 * GET /api/items?page=2&limit=50
 */
export const PaginationQuerySchema = z.object({
  page: z.coerce
    .number()
    .int('Номер страницы должен быть целым числом')
    .min(1, 'Номер страницы должен быть больше 0')
    .default(1)
    .describe('Номер страницы (начиная с 1)'),

  limit: z.coerce
    .number()
    .int('Лимит должен быть целым числом')
    .min(1, 'Минимальный лимит: 1')
    .max(10000, 'Максимальный лимит: 10000')
    .default(20)
    .describe('Количество элементов на странице')
});

/**
 * Схема валидации для пагинации на основе offset
 *
 * @example
 * GET /api/items?offset=100&limit=50
 */
export const OffsetPaginationQuerySchema = z.object({
  offset: z.coerce
    .number()
    .int('Offset должен быть целым числом')
    .nonnegative('Offset не может быть отрицательным')
    .default(0)
    .describe('Смещение от начала списка'),

  limit: z.coerce
    .number()
    .int('Лимит должен быть целым числом')
    .min(1, 'Минимальный лимит: 1')
    .max(10000, 'Максимальный лимит: 10000')
    .default(20)
    .describe('Количество элементов')
});

/**
 * Схема для cursor-based пагинации
 *
 * @example
 * GET /api/items?cursor=abc123&limit=50
 */
export const CursorPaginationQuerySchema = z.object({
  cursor: z
    .string()
    .optional()
    .describe('Курсор для следующей страницы'),

  limit: z.coerce
    .number()
    .int()
    .min(1)
    .max(100)
    .default(20)
    .describe('Количество элементов')
});

// ============ Sorting Schemas ============

/**
 * Базовая схема для сортировки
 *
 * @example
 * GET /api/items?sortBy=name&sortOrder=desc
 */
export const SortQuerySchema = z.object({
  sortOrder: z
    .enum(['asc', 'desc', 'ASC', 'DESC'])
    .transform(val => val.toLowerCase() as 'asc' | 'desc')
    .default('asc')
    .describe('Направление сортировки')
});

/**
 * Создает схему сортировки с заданными полями
 *
 * @param fields - Разрешенные поля для сортировки
 * @param defaultField - Поле по умолчанию
 * @returns Zod schema для валидации sortBy и sortOrder
 *
 * @example
 * ```typescript
 * const UserSortSchema = createSortSchema(
 *   ['id', 'name', 'createdAt'] as const,
 *   'createdAt'
 * );
 * ```
 */
export function createSortSchema<const T extends readonly [string, ...string[]]>(
  fields: T,
  defaultField: T[number]
) {
  return z.object({
    sortBy: z
      .enum(fields as any)
      .default(defaultField as any)
      .describe('Поле для сортировки'),

    sortOrder: z
      .enum(['asc', 'desc', 'ASC', 'DESC'])
      .transform(val => val.toLowerCase() as 'asc' | 'desc')
      .default('asc')
      .describe('Направление сортировки')
  });
}

// ============ ID Parameter Schemas ============

/**
 * Схема для числового ID в URL параметрах
 *
 * @example
 * GET /api/users/:id
 */
export const IdParamSchema = z.object({
  id: z.coerce
    .number()
    .int('ID должен быть целым числом')
    .positive('ID должен быть положительным')
    .describe('Числовой идентификатор')
});

/**
 * Схема для UUID в URL параметрах
 *
 * @example
 * GET /api/tasks/:taskId
 */
export const UuidParamSchema = z.object({
  id: z
    .string()
    .uuid('Невалидный UUID формат')
    .describe('UUID идентификатор')
});

/**
 * Создает схему для кастомного ID параметра
 *
 * @param paramName - Имя параметра
 * @param type - Тип ID ('number' | 'uuid' | 'string')
 * @returns Zod schema для валидации параметра
 *
 * @example
 * ```typescript
 * const GroupIdSchema = createIdParamSchema('groupId', 'number');
 * const TaskIdSchema = createIdParamSchema('taskId', 'uuid');
 * ```
 */
export function createIdParamSchema(
  paramName: string,
  type: 'number' | 'uuid' | 'string' = 'number'
) {
  const schemas = {
    number: z.coerce.number().int().positive(),
    uuid: z.string().uuid(),
    string: z.string().min(1)
  };

  return z.object({
    [paramName]: schemas[type].describe(`${paramName} идентификатор`)
  });
}

// ============ Search and Filter Schemas ============

/**
 * Схема для поискового запроса
 *
 * @example
 * GET /api/items?search=keyword
 */
export const SearchQuerySchema = z.object({
  search: z
    .string()
    .max(255, 'Поисковый запрос слишком длинный (макс. 255 символов)')
    .optional()
    .describe('Поисковый запрос')
});

/**
 * Схема для фильтрации по диапазону дат
 *
 * @example
 * GET /api/items?dateFrom=2024-01-01&dateTo=2024-12-31
 */
export const DateRangeQuerySchema = z
  .object({
    dateFrom: z.coerce
      .date()
      .optional()
      .describe('Начальная дата (ISO 8601)'),

    dateTo: z.coerce
      .date()
      .optional()
      .describe('Конечная дата (ISO 8601)')
  })
  .refine(
    data => {
      if (data.dateFrom && data.dateTo) {
        return data.dateFrom <= data.dateTo;
      }
      return true;
    },
    {
      message: 'dateFrom должна быть раньше или равна dateTo',
      path: ['dateFrom']
    }
  );

/**
 * Схема для фильтрации по числовому диапазону
 *
 * @param fieldName - Имя поля для диапазона
 * @returns Zod schema с полями min{Field} и max{Field}
 *
 * @example
 * ```typescript
 * const PriceRangeSchema = createRangeSchema('price');
 * // Создаст поля: minPrice, maxPrice
 * ```
 */
export function createRangeSchema(fieldName: string) {
  const minField = `min${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`;
  const maxField = `max${fieldName.charAt(0).toUpperCase() + fieldName.slice(1)}`;

  return z
    .object({
      [minField]: z.coerce.number().optional(),
      [maxField]: z.coerce.number().optional()
    })
    .refine(
      data => {
        const min = (data as any)[minField];
        const max = (data as any)[maxField];
        if (min !== undefined && max !== undefined) {
          return min <= max;
        }
        return true;
      },
      {
        message: `${minField} должно быть меньше или равно ${maxField}`,
        path: [minField]
      }
    );
}

// ============ Boolean Filter Schemas ============

/**
 * Схема для булевого фильтра из строки
 * Принимает: 'true', 'false', '1', '0', 'yes', 'no'
 *
 * @example
 * GET /api/items?isActive=true
 */
export const BooleanQuerySchema = z
  .enum(['true', 'false', '1', '0', 'yes', 'no'])
  .transform(val => val === 'true' || val === '1' || val === 'yes')
  .optional();

/**
 * Создает булевый фильтр с кастомным именем
 */
export function createBooleanFilter(fieldName: string) {
  return z.object({
    [fieldName]: BooleanQuerySchema.describe(`Фильтр по ${fieldName}`)
  });
}

// ============ Composite Schemas ============

/**
 * Полная схема для списка с пагинацией, сортировкой и поиском
 *
 * @param sortFields - Разрешенные поля для сортировки
 * @param defaultSort - Поле сортировки по умолчанию
 * @returns Объединенная схема
 *
 * @example
 * ```typescript
 * const GetUsersQuerySchema = createListQuerySchema(
 *   ['id', 'name', 'createdAt'],
 *   'createdAt'
 * );
 * ```
 */
export function createListQuerySchema<const T extends readonly [string, ...string[]]>(
  sortFields: T,
  defaultSort: T[number]
) {
  return PaginationQuerySchema
    .merge(createSortSchema(sortFields, defaultSort))
    .merge(SearchQuerySchema);
}

// ============ Auto-Generated Types ============

/**
 * Автогенерированные TypeScript типы из схем
 */
export type PaginationQuery = z.infer<typeof PaginationQuerySchema>;
export type OffsetPaginationQuery = z.infer<typeof OffsetPaginationQuerySchema>;
export type CursorPaginationQuery = z.infer<typeof CursorPaginationQuerySchema>;
export type SortQuery = z.infer<typeof SortQuerySchema>;
export type IdParam = z.infer<typeof IdParamSchema>;
export type UuidParam = z.infer<typeof UuidParamSchema>;
export type SearchQuery = z.infer<typeof SearchQuerySchema>;
export type DateRangeQuery = z.infer<typeof DateRangeQuerySchema>;

/**
 * Helper тип для добавления pagination в response
 */
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/**
 * Helper тип для paginated response
 */
export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
}
