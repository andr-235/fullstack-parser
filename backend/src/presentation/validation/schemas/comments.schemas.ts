/**
 * @fileoverview HTTP схемы валидации для Comments API endpoints
 *
 * PRESENTATION LAYER
 * - Валидация HTTP запросов для операций с комментариями VK
 * - Схемы для получения, фильтрации и экспорта комментариев
 * - Type-safe через Zod
 */

import { z } from 'zod';
import {
  PaginationQuerySchema,
  createSortSchema,
  createIdParamSchema,
  DateRangeQuerySchema,
  SearchQuerySchema,
  createRangeSchema
} from './common.schemas';

// ============ Get Comments Schemas ============

/**
 * Схема для получения списка комментариев с фильтрацией
 *
 * @example
 * GET /api/comments?page=1&limit=50&taskId=123&sentiment=positive&minLikes=10
 */
export const GetCommentsQuerySchema = PaginationQuerySchema
  .merge(
    createSortSchema(
      ['id', 'createdAt', 'likes', 'text', 'depth'] as const,
      'createdAt'
    )
  )
  .merge(SearchQuerySchema)
  .merge(DateRangeQuerySchema)
  .extend({
    taskId: z.coerce
      .number()
      .int()
      .positive()
      .optional()
      .describe('Фильтр по ID задачи'),

    postId: z.coerce
      .number()
      .int()
      .optional()
      .describe('Фильтр по ID поста VK'),

    authorId: z.coerce
      .number()
      .int()
      .optional()
      .describe('Фильтр по ID автора комментария'),

    sentiment: z
      .enum(['all', 'positive', 'negative', 'neutral'])
      .default('all')
      .describe('Фильтр по тональности комментария'),

    hasAttachments: z
      .enum(['true', 'false', '1', '0'])
      .transform(val => val === 'true' || val === '1')
      .optional()
      .describe('Фильтр по наличию вложений'),

    isReply: z
      .enum(['true', 'false', '1', '0'])
      .transform(val => val === 'true' || val === '1')
      .optional()
      .describe('Только ответы на комментарии'),

    depth: z.coerce
      .number()
      .int()
      .min(0)
      .max(10)
      .optional()
      .describe('Фильтр по глубине вложенности'),

    minTextLength: z.coerce
      .number()
      .int()
      .nonnegative()
      .optional()
      .describe('Минимальная длина текста комментария'),

    maxTextLength: z.coerce
      .number()
      .int()
      .positive()
      .optional()
      .describe('Максимальная длина текста комментария')
  })
  .merge(createRangeSchema('likes')); // minLikes, maxLikes

/**
 * Схема для получения одного комментария по ID
 *
 * @example
 * GET /api/comments/:id
 */
export const GetCommentByIdParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для получения вложенных комментариев
 *
 * @example
 * GET /api/comments/:id/replies?page=1&limit=20
 */
export const GetCommentRepliesParamSchema = createIdParamSchema('id', 'number');

export const GetCommentRepliesQuerySchema = PaginationQuerySchema.merge(
  createSortSchema(['createdAt', 'likes'] as const, 'createdAt')
);

// ============ Comment Statistics Schemas ============

/**
 * Схема для получения статистики по комментариям
 *
 * @example
 * GET /api/comments/stats?taskId=123&groupBy=sentiment
 */
export const GetCommentStatsQuerySchema = z.object({
  taskId: z.coerce
    .number()
    .int()
    .positive()
    .optional()
    .describe('Статистика для конкретной задачи'),

  postId: z.coerce
    .number()
    .int()
    .optional()
    .describe('Статистика для конкретного поста'),

  groupBy: z
    .enum(['sentiment', 'day', 'hour', 'depth', 'author'])
    .default('sentiment')
    .describe('Группировка статистики')
})
  .merge(DateRangeQuerySchema);

/**
 * Схема для получения топ авторов комментариев
 *
 * @example
 * GET /api/comments/top-authors?limit=10&orderBy=count
 */
export const GetTopAuthorsQuerySchema = z.object({
  limit: z.coerce
    .number()
    .int()
    .min(1)
    .max(100)
    .default(10)
    .describe('Количество авторов в топе'),

  orderBy: z
    .enum(['count', 'likes', 'avg_likes'])
    .default('count')
    .describe('Критерий сортировки'),

  taskId: z.coerce
    .number()
    .int()
    .positive()
    .optional()
    .describe('Топ для конкретной задачи')
});

// ============ Export Comments Schemas ============

/**
 * Схема для экспорта комментариев
 *
 * @example
 * GET /api/comments/export?format=csv&taskId=123&sentiment=positive
 */
export const ExportCommentsQuerySchema = GetCommentsQuerySchema.extend({
  format: z
    .enum(['json', 'csv', 'xlsx', 'txt'])
    .default('json')
    .describe('Формат экспорта'),

  includeFields: z
    .array(
      z.enum([
        'id',
        'text',
        'authorId',
        'authorName',
        'createdAt',
        'likes',
        'sentiment',
        'depth',
        'parentId',
        'postId',
        'taskId'
      ])
    )
    .optional()
    .describe('Поля для включения в экспорт')
});

// ============ Sentiment Analysis Schemas ============

/**
 * Схема для запуска анализа тональности
 *
 * @example
 * POST /api/comments/:id/analyze-sentiment
 */
export const AnalyzeSentimentParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для массового анализа тональности
 *
 * @example
 * POST /api/comments/batch-analyze
 * Body: { commentIds: [1, 2, 3] }
 */
export const BatchAnalyzeSentimentBodySchema = z.object({
  commentIds: z
    .array(z.number().int().positive())
    .min(1, 'Необходимо указать хотя бы один ID комментария')
    .max(1000, 'Максимум 1000 комментариев за раз')
    .describe('Массив ID комментариев для анализа'),

  force: z
    .boolean()
    .default(false)
    .describe('Переанализировать даже если уже есть результат')
});

// ============ Delete Comments Schemas ============

/**
 * Схема для удаления комментария
 *
 * @example
 * DELETE /api/comments/:id
 */
export const DeleteCommentParamSchema = createIdParamSchema('id', 'number');

/**
 * Схема для массового удаления комментариев
 *
 * @example
 * DELETE /api/comments
 * Body: { commentIds: [1, 2, 3] }
 */
export const BatchDeleteCommentsBodySchema = z.object({
  commentIds: z
    .array(z.number().int().positive())
    .min(1, 'Необходимо указать хотя бы один ID')
    .max(10000, 'Максимум 10000 комментариев за раз')
    .describe('Массив ID комментариев для удаления'),

  taskId: z.coerce
    .number()
    .int()
    .positive()
    .optional()
    .describe('Удалить все комментарии из задачи (альтернатива commentIds)')
})
  .refine(
    data => data.commentIds.length > 0 || data.taskId !== undefined,
    {
      message: 'Необходимо указать либо commentIds, либо taskId'
    }
  );

// ============ Search and Filter Schemas ============

/**
 * Схема для полнотекстового поиска по комментариям
 *
 * @example
 * POST /api/comments/search
 * Body: {
 *   query: "важная информация",
 *   filters: { sentiment: "positive" }
 * }
 */
export const SearchCommentsBodySchema = z.object({
  query: z
    .string()
    .min(1, 'Поисковый запрос не может быть пустым')
    .max(500, 'Максимальная длина запроса: 500 символов')
    .describe('Поисковый запрос'),

  filters: GetCommentsQuerySchema
    .omit({ search: true })
    .partial()
    .optional()
    .describe('Дополнительные фильтры'),

  highlightMatch: z
    .boolean()
    .default(true)
    .describe('Подсвечивать совпадения в тексте')
});

// ============ Auto-Generated Types ============

/**
 * Автогенерированные TypeScript типы из Zod схем
 */
export type GetCommentsQuery = z.infer<typeof GetCommentsQuerySchema>;
export type GetCommentByIdParam = z.infer<typeof GetCommentByIdParamSchema>;
export type GetCommentRepliesParam = z.infer<typeof GetCommentRepliesParamSchema>;
export type GetCommentRepliesQuery = z.infer<typeof GetCommentRepliesQuerySchema>;
export type GetCommentStatsQuery = z.infer<typeof GetCommentStatsQuerySchema>;
export type GetTopAuthorsQuery = z.infer<typeof GetTopAuthorsQuerySchema>;
export type ExportCommentsQuery = z.infer<typeof ExportCommentsQuerySchema>;
export type AnalyzeSentimentParam = z.infer<typeof AnalyzeSentimentParamSchema>;
export type BatchAnalyzeSentimentBody = z.infer<typeof BatchAnalyzeSentimentBodySchema>;
export type DeleteCommentParam = z.infer<typeof DeleteCommentParamSchema>;
export type BatchDeleteCommentsBody = z.infer<typeof BatchDeleteCommentsBodySchema>;
export type SearchCommentsBody = z.infer<typeof SearchCommentsBodySchema>;

// ============ Response Types (документация) ============

/**
 * Типы для ответов API (не валидируются, только для документации)
 */
export interface CommentListItem {
  id: number;
  text: string;
  authorId: number;
  authorName: string;
  authorPhoto?: string;
  createdAt: string;
  likes: number;
  sentiment?: 'positive' | 'negative' | 'neutral';
  depth: number;
  parentId?: number;
  postId: number;
  taskId: number;
  hasAttachments: boolean;
  attachmentsCount: number;
}

export interface CommentDetails extends CommentListItem {
  attachments?: Array<{
    type: string;
    url?: string;
    photoUrl?: string;
  }>;
  replies?: CommentListItem[];
  repliesCount: number;
}

export interface CommentStats {
  total: number;
  bySentiment: {
    positive: number;
    negative: number;
    neutral: number;
    unknown: number;
  };
  byDepth: Record<number, number>;
  avgTextLength: number;
  avgLikes: number;
  topAuthors: Array<{
    authorId: number;
    authorName: string;
    count: number;
    totalLikes: number;
  }>;
}

export interface TopAuthor {
  authorId: number;
  authorName: string;
  authorPhoto?: string;
  commentsCount: number;
  totalLikes: number;
  avgLikes: number;
}
