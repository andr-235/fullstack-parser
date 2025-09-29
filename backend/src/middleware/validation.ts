import { Request, Response, NextFunction } from 'express';
import { AppValidationError } from '@/utils/errors';
import { ErrorCodes } from '@/types/express';
import { GetGroupsRequest } from '@/types/api';

// Константы
const MAX_PAGINATION_LIMIT = 10000;
const MIN_PAGINATION_LIMIT = 1;
const DEFAULT_PAGE = 1;
const DEFAULT_LIMIT = 20;

/**
 * Middleware для валидации пагинации
 */
export const validatePagination = (req: Request, res: Response, next: NextFunction): void => {
  const page = Number(req.query.page);
  const limit = Number(req.query.limit);

  if (isNaN(page) || page < 1) {
    throw new AppValidationError('Номер страницы должен быть положительным числом', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'page',
      value: req.query.page,
      constraint: 'positive integer'
    });
  }

  if (isNaN(limit) || limit < MIN_PAGINATION_LIMIT || limit > MAX_PAGINATION_LIMIT) {
    throw new AppValidationError('Лимит должен быть от 1 до 10000', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'limit',
      value: req.query.limit,
      constraint: `${MIN_PAGINATION_LIMIT} <= limit <= ${MAX_PAGINATION_LIMIT}`
    });
  }

  // Добавляем validated params в req для использования в controller
  (req as any).validatedPagination = {
    page,
    limit,
    offset: (page - 1) * limit
  };

  next();
};

/**
 * Middleware для валидации ID группы
 */
export const validateGroupId = (req: Request, res: Response, next: NextFunction): void => {
  const groupId = Number(req.params.groupId);

  if (isNaN(groupId) || groupId <= 0) {
    throw new AppValidationError('ID группы должен быть положительным числом', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'groupId',
      value: req.params.groupId,
      constraint: 'positive number'
    });
  }

  (req as any).validatedGroupId = groupId;

  next();
};

/**
 * Middleware для валидации batch delete body
 */
export const validateBatchDelete = (req: Request, res: Response, next: NextFunction): void => {
  const { groupIds } = req.body;

  if (!groupIds || !Array.isArray(groupIds)) {
    throw new AppValidationError('groupIds должен быть массивом', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'groupIds',
      value: groupIds,
      constraint: 'array'
    });
  }

  if (groupIds.length === 0) {
    throw new AppValidationError('Массив groupIds не может быть пустым', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'groupIds',
      constraint: 'non-empty array'
    });
  }

  const validGroupIds = groupIds.map(id => Number(id)).filter(id => !isNaN(id) && id > 0);

  if (validGroupIds.length !== groupIds.length) {
    throw new AppValidationError('Все ID групп должны быть положительными числами', {
      code: ErrorCodes.INVALID_PARAMETER,
      field: 'groupIds',
      value: groupIds,
      constraint: 'positive numbers array'
    });
  }

  (req as any).validatedGroupIds = validGroupIds;

  next();
};