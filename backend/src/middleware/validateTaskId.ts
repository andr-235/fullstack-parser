import { Request, Response, NextFunction } from 'express';
import logger from '@/utils/logger';
import { ValidationError } from '@/utils/errors';

/**
 * Middleware для валидации task ID в параметрах запроса
 */
export const validateTaskId = (req: Request, res: Response, next: NextFunction): void => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    const taskId = Number(req.params.taskId);

    if (isNaN(taskId) || taskId <= 0) {
      logger.warn('Invalid task ID provided', {
        taskId: req.params.taskId,
        requestId
      });

      const validationError = new ValidationError('Invalid task ID format', [
        {
          field: 'taskId',
          message: 'Task ID must be a valid positive number',
          value: req.params.taskId
        }
      ]);

      if (requestId) {
        validationError.setRequestId(requestId);
      }

      throw validationError;
    }

    // Добавляем валидированный taskId к объекту запроса для дальнейшего использования
    (req as any).validatedTaskId = taskId;

    next();
  } catch (error) {
    next(error);
  }
};

export default validateTaskId;