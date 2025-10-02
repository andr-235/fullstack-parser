/**
 * @fileoverview Центральный экспорт validation schemas
 *
 * PRESENTATION LAYER
 * - Схемы валидации для всех API endpoints
 * - Автогенерированные TypeScript типы
 */

// Schemas
export * from './schemas';

/**
 * @example
 * Использование:
 *
 * ```typescript
 * // Импорт схем из validation
 * import {
 *   GetGroupsQuerySchema,
 *   CreateTaskBodySchema,
 *   type GetGroupsQuery,
 *   type CreateTaskBody
 * } from '@presentation/validation';
 *
 * // Импорт middleware из presentation/middleware
 * import { validateQuery, validateBody } from '@presentation/middleware/zodValidation';
 * ```
 */
