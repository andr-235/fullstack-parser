import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import { ValidationError } from '@/utils/errors';

/**
 * Интерфейс для опций валидации
 */
interface ValidationOptions {
  stripUnknown?: boolean;
  abortEarly?: boolean;
  allowUnknown?: boolean;
  context?: any;
}

/**
 * Создает middleware для валидации тела запроса с помощью Joi схемы
 */
export const validateBody = (schema: Joi.ObjectSchema, options: ValidationOptions = {}) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      const validationOptions = {
        abortEarly: false,
        stripUnknown: true,
        ...options
      };

      const { error, value } = schema.validate(req.body, validationOptions);

      if (error) {
        logger.warn('Body validation error', {
          details: error.details.map(d => ({
            field: d.path.join('.'),
            message: d.message,
            value: d.context?.value
          })),
          requestId
        });

        const validationError = ValidationError.fromJoi(error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем валидированные body параметры
      (req as any).validatedBody = value;
      next();
    } catch (error) {
      next(error);
    }
  };
};

/**
 * Создает middleware для валидации query параметров с помощью Joi схемы
 */
export const validateQuery = (schema: Joi.ObjectSchema, options: ValidationOptions = {}) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      const validationOptions = {
        abortEarly: false,
        stripUnknown: false,
        allowUnknown: true,
        ...options
      };

      const { error, value } = schema.validate(req.query, validationOptions);

      if (error) {
        logger.warn('Query validation error', {
          details: error.details.map(d => ({
            field: d.path.join('.'),
            message: d.message,
            value: d.context?.value
          })),
          requestId
        });

        const validationError = ValidationError.fromJoi(error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем валидированные query параметры
      (req as any).validatedQuery = value;
      next();
    } catch (error) {
      next(error);
    }
  };
};

/**
 * Создает middleware для валидации параметров маршрута с помощью Joi схемы
 */
export const validateParams = (schema: Joi.ObjectSchema, options: ValidationOptions = {}) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      const validationOptions = {
        abortEarly: false,
        stripUnknown: true,
        ...options
      };

      const { error, value } = schema.validate(req.params, validationOptions);

      if (error) {
        logger.warn('Params validation error', {
          details: error.details.map(d => ({
            field: d.path.join('.'),
            message: d.message,
            value: d.context?.value
          })),
          requestId
        });

        const validationError = ValidationError.fromJoi(error);
        if (requestId) {
          validationError.setRequestId(requestId);
        }

        throw validationError;
      }

      // Сохраняем валидированные params
      (req as any).validatedParams = value;
      next();
    } catch (error) {
      next(error);
    }
  };
};

// Общие Joi схемы для переиспользования

/**
 * Схема для валидации пагинации
 */
export const paginationSchema = Joi.object({
  page: Joi.number().integer().min(1).default(1),
  limit: Joi.number().integer().min(1).max(10000).default(20)
}).options({ convert: true });

/**
 * Схема для валидации ID в параметрах
 */
export const idParamSchema = Joi.object({
  id: Joi.number().integer().positive().required()
});

/**
 * Схема для валидации task ID в параметрах
 */
export const taskIdParamSchema = Joi.object({
  taskId: Joi.number().integer().positive().required()
});

/**
 * Схема для валидации group ID в параметрах
 */
export const groupIdParamSchema = Joi.object({
  groupId: Joi.number().integer().positive().required()
});

/**
 * Middleware для валидации пагинации в query параметрах
 */
export const validatePagination = validateQuery(paginationSchema);

/**
 * Готовые middleware для валидации ID в параметрах маршрута
 */
export const validateTaskIdParam = validateParams(taskIdParamSchema);
export const validateGroupIdParam = validateParams(groupIdParamSchema);
export const validateIdParam = validateParams(idParamSchema);

/**
 * Middleware для валидации опционального group ID в query параметрах
 */
export const validateOptionalGroupId = (paramName: string = 'groupId') => {
  const schema = Joi.object({
    [paramName]: Joi.number().integer().positive().optional()
  });
  return validateQuery(schema);
};

export default {
  validateBody,
  validateQuery,
  validateParams,
  validatePagination,
  validateTaskIdParam,
  validateGroupIdParam,
  validateIdParam,
  validateOptionalGroupId,
  paginationSchema,
  idParamSchema,
  taskIdParamSchema,
  groupIdParamSchema
};