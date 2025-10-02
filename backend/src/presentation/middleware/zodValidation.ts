/**
 * @fileoverview Zod validation middleware для Express
 *
 * PRESENTATION LAYER
 * - Валидирует HTTP запросы через Zod схемы
 * - Интегрируется с существующим error handling
 * - Автоматическая генерация TypeScript типов
 */

import { Request, Response, NextFunction } from 'express';
import { z, ZodSchema, ZodError } from 'zod';
import logger from '@infrastructure/utils/logger';
import { ValidationError as AppValidationError } from '@infrastructure/utils/errors';

/**
 * Интерфейс для опций валидации
 */
export interface ZodValidationOptions {
  /**
   * Удалять неизвестные поля из объекта после валидации
   * @default true для body, false для query
   */
  stripUnknown?: boolean;

  /**
   * Преобразовывать типы (например, строки в числа)
   * @default true
   */
  coerce?: boolean;

  /**
   * Выбрасывать ошибку при первой проблеме или собирать все ошибки
   * @default false (собирать все ошибки)
   */
  abortEarly?: boolean;

  /**
   * Контекст для валидации (доступен в схеме через ctx)
   */
  context?: any;
}

/**
 * Преобразует ZodError в структурированный формат для API ответа
 */
function formatZodError(error: ZodError): AppValidationError {
  const validationErrors = error.issues.map(err => ({
    field: err.path.join('.') || 'root',
    message: err.message,
    value: err.code === 'invalid_type' ? undefined : err.code,
    code: err.code
  }));

  return new AppValidationError(
    'Validation failed',
    validationErrors
  );
}

/**
 * Создает middleware для валидации request body через Zod схему
 *
 * @param schema - Zod схема для валидации
 * @param options - Опции валидации
 * @returns Express middleware
 *
 * @example
 * ```typescript
 * const CreateUserSchema = z.object({
 *   email: z.string().email(),
 *   name: z.string().min(2)
 * });
 *
 * router.post('/users', validateBody(CreateUserSchema), createUserHandler);
 * ```
 */
export function validateBody<T extends ZodSchema>(
  schema: T,
  options: ZodValidationOptions = {}
): (req: Request, res: Response, next: NextFunction) => void {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      // Настройки по умолчанию для body
      const opts = {
        stripUnknown: true,
        ...options
      };

      // Парсим и валидируем body
      const result = schema.safeParse(req.body);

      if (!result.success) {
        logger.warn('Body validation failed', {
          errors: result.error.issues,
          body: req.body,
          requestId
        });

        const validationError = formatZodError(result.error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем провалидированные данные
      (req as any).validatedBody = result.data;
      req.body = result.data; // Также обновляем req.body для совместимости

      next();
    } catch (error) {
      next(error);
    }
  };
}

/**
 * Создает middleware для валидации query параметров через Zod схему
 *
 * @param schema - Zod схема для валидации
 * @param options - Опции валидации
 * @returns Express middleware
 *
 * @example
 * ```typescript
 * const GetUsersQuerySchema = z.object({
 *   page: z.coerce.number().int().min(1).default(1),
 *   limit: z.coerce.number().int().min(1).max(100).default(20)
 * });
 *
 * router.get('/users', validateQuery(GetUsersQuerySchema), getUsersHandler);
 * ```
 */
export function validateQuery<T extends ZodSchema>(
  schema: T,
  options: ZodValidationOptions = {}
): (req: Request, res: Response, next: NextFunction) => void {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      // Настройки по умолчанию для query
      const opts = {
        stripUnknown: false, // Для query обычно не удаляем неизвестные поля
        ...options
      };

      // Парсим и валидируем query
      const result = schema.safeParse(req.query);

      if (!result.success) {
        logger.warn('Query validation failed', {
          errors: result.error.issues,
          query: req.query,
          requestId
        });

        const validationError = formatZodError(result.error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем провалидированные данные
      (req as any).validatedQuery = result.data;
      req.query = result.data as any; // Также обновляем req.query

      next();
    } catch (error) {
      next(error);
    }
  };
}

/**
 * Создает middleware для валидации URL параметров через Zod схему
 *
 * @param schema - Zod схема для валидации
 * @param options - Опции валидации
 * @returns Express middleware
 *
 * @example
 * ```typescript
 * const UserIdParamSchema = z.object({
 *   id: z.coerce.number().int().positive()
 * });
 *
 * router.get('/users/:id', validateParams(UserIdParamSchema), getUserHandler);
 * ```
 */
export function validateParams<T extends ZodSchema>(
  schema: T,
  options: ZodValidationOptions = {}
): (req: Request, res: Response, next: NextFunction) => void {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      // Настройки по умолчанию для params
      const opts = {
        stripUnknown: true,
        ...options
      };

      // Парсим и валидируем params
      const result = schema.safeParse(req.params);

      if (!result.success) {
        logger.warn('Params validation failed', {
          errors: result.error.issues,
          params: req.params,
          requestId
        });

        const validationError = formatZodError(result.error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем провалидированные данные
      (req as any).validatedParams = result.data;
      req.params = result.data as any; // Также обновляем req.params

      next();
    } catch (error) {
      next(error);
    }
  };
}

/**
 * Создает универсальный middleware для валидации любой части запроса
 *
 * @param target - Часть запроса для валидации ('body' | 'query' | 'params')
 * @param schema - Zod схема для валидации
 * @param options - Опции валидации
 * @returns Express middleware
 */
export function validate<T extends ZodSchema>(
  target: 'body' | 'query' | 'params',
  schema: T,
  options: ZodValidationOptions = {}
): (req: Request, res: Response, next: NextFunction) => void {
  switch (target) {
    case 'body':
      return validateBody(schema, options);
    case 'query':
      return validateQuery(schema, options);
    case 'params':
      return validateParams(schema, options);
    default:
      throw new Error(`Unknown validation target: ${target}`);
  }
}

/**
 * Helper для получения провалидированных данных из request
 * Обеспечивает type safety при использовании в handlers
 */
export function getValidated<T = any>(
  req: Request,
  source: 'body' | 'query' | 'params'
): T {
  const key = `validated${source.charAt(0).toUpperCase() + source.slice(1)}`;
  return (req as any)[key] || req[source];
}

/**
 * Type-safe helper для создания валидационных middleware
 * с автоматическим выводом типов
 */
export type ValidatedRequest<
  TBody = any,
  TQuery = any,
  TParams = any
> = Request<TParams, any, TBody, TQuery>;

/**
 * Экспорт для удобного использования
 */
export default {
  validateBody,
  validateQuery,
  validateParams,
  validate,
  getValidated
};
