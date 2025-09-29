import { Request, Response, NextFunction } from 'express';
import logger from '@/utils/logger';
import { ValidationError } from '@/utils/errors';

/**
 * Middleware для валидации group ID в параметрах запроса
 */
export const validateGroupId = (req: Request, res: Response, next: NextFunction): void => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    const groupId = Number(req.params.groupId);

    if (isNaN(groupId) || groupId <= 0) {
      logger.warn('Invalid group ID provided', {
        groupId: req.params.groupId,
        requestId
      });

      const validationError = new ValidationError('Invalid group ID format', [
        {
          field: 'groupId',
          message: 'Group ID must be a valid positive number',
          value: req.params.groupId
        }
      ]);

      if (requestId) {
        validationError.setRequestId(requestId);
      }

      throw validationError;
    }

    // Добавляем валидированный groupId к объекту запроса для дальнейшего использования
    (req as any).validatedGroupId = groupId;

    next();
  } catch (error) {
    next(error);
  }
};

/**
 * Middleware для валидации опционального group ID в query параметрах
 */
export const validateOptionalGroupId = (paramName: string = 'groupId') => {
  return (req: Request, res: Response, next: NextFunction): void => {
    const requestId = (req as any).requestId || (req as any).id;

    try {
      const groupIdParam = req.query[paramName];

      if (groupIdParam !== undefined) {
        const groupId = Number(groupIdParam);

        if (isNaN(groupId) || groupId <= 0) {
          logger.warn('Invalid optional group ID provided', {
            [paramName]: groupIdParam,
            requestId
          });

          const validationError = new ValidationError(`Invalid ${paramName} format`, [
            {
              field: paramName,
              message: `${paramName} must be a valid positive number`,
              value: groupIdParam
            }
          ]);

          if (requestId) {
            validationError.setRequestId(requestId);
          }

          throw validationError;
        }

        // Добавляем валидированный groupId к объекту запроса
        (req as any)[`validated${paramName.charAt(0).toUpperCase() + paramName.slice(1)}`] = groupId;
      }

      next();
    } catch (error) {
      next(error);
    }
  };
};

export default validateGroupId;