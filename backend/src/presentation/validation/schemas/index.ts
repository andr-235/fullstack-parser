/**
 * @fileoverview Центральный экспорт всех validation схем
 *
 * PRESENTATION LAYER
 * - Единая точка импорта для всех схем валидации
 * - Организовано по доменам (common, groups, tasks, comments)
 */

// ============ Common Schemas ============
export * from './common.schemas';

// ============ Groups Schemas ============
export * from './groups.schemas';

// ============ Tasks Schemas ============
export * from './tasks.schemas';

// ============ Comments Schemas ============
export * from './comments.schemas';

/**
 * @example
 * Использование в контроллерах:
 *
 * ```typescript
 * import {
 *   GetGroupsQuerySchema,
 *   validateQuery,
 *   type GetGroupsQuery
 * } from '@presentation/validation/schemas';
 *
 * router.get('/', validateQuery(GetGroupsQuerySchema), handler);
 *
 * function handler(req: Request, res: Response) {
 *   const query = req.query as GetGroupsQuery;
 *   // query теперь типизирован и провалидирован
 * }
 * ```
 */
