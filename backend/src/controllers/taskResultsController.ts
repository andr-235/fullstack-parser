import { Router, Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import dbRepo from '@/repositories/dbRepo';
import {
  ValidationError,
  NotFoundError,
  ErrorUtils
} from '@/utils/errors';
import { validateQuery, validateTaskIdParam } from '@/middleware/validationMiddleware';

const router = Router();

// Validation schema for results query
const getResultsQuerySchema = Joi.object({
  groupId: Joi.number().integer().positive().optional(),
  postId: Joi.number().integer().positive().optional(),
  limit: Joi.number().integer().min(1).max(1000).default(100),
  offset: Joi.number().integer().min(0).default(0)
});

// Типы для запросов
interface GetResultsQuery {
  groupId?: number;
  postId?: number;
  limit?: number;
  offset?: number;
}

/**
 * GET /api/results/:taskId - Получает результаты выполнения задачи
 */
const getResults = async (req: Request<{ taskId: string }, {}, {}, GetResultsQuery>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    logger.info('Processing getResults request', {
      taskId,
      groupId: req.query.groupId,
      postId: req.query.postId,
      limit: req.query.limit,
      offset: req.query.offset,
      requestId
    });

    const { groupId, postId, limit = 100, offset = 0 } = req.query;

    const results = await dbRepo.getResults(taskId, groupId, postId);

    logger.info('Results retrieved successfully', {
      taskId,
      totalComments: results.totalComments,
      postsCount: results.posts.length,
      groupId,
      postId,
      requestId
    });

    res.success({
      taskId,
      posts: results.posts,
      totalComments: results.totalComments,
      postsCount: results.posts.length,
      pagination: {
        limit,
        offset,
        total: results.totalComments,
        hasMore: offset + limit < results.totalComments
      },
      filters: {
        groupId,
        postId
      }
    }, 'Результаты задачи получены');

  } catch (error) {
    // Обработка ошибки "результаты не найдены"
    if (error instanceof Error && (error.message.includes('not found') || error.message.includes('Task not found'))) {
      const notFoundError = new NotFoundError('Task results', String(taskId));
      if (requestId) {
        notFoundError.setRequestId(requestId);
      }
      throw notFoundError;
    }

    // Передаем валидационные ошибки дальше
    if (error instanceof ValidationError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getResults', {
      taskId,
      groupId: req.query.groupId,
      postId: req.query.postId,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения результатов задачи');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/results/:taskId/summary - Получает сводную информацию о результатах задачи
 */
const getResultsSummary = async (req: Request<{ taskId: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    logger.info('Processing getResultsSummary request', { taskId, requestId });

    // Получаем результаты для создания сводки
    const results = await dbRepo.getResults(taskId);

    if (!results || results.posts.length === 0) {
      const notFoundError = new NotFoundError('Task results summary', String(taskId));
      if (requestId) {
        notFoundError.setRequestId(requestId);
      }
      throw notFoundError;
    }

    // Создаем сводку на основе результатов
    const summary = {
      totalComments: results.totalComments,
      totalPosts: results.posts.length,
      totalGroups: new Set(results.posts.map(post => post.group_id)).size,
      averageCommentsPerPost: results.posts.length > 0
        ? Math.round((results.totalComments / results.posts.length) * 100) / 100
        : 0,
      generatedAt: new Date().toISOString()
    };

    logger.info('Results summary retrieved successfully', {
      taskId,
      totalComments: summary.totalComments,
      totalGroups: summary.totalGroups,
      totalPosts: summary.totalPosts,
      requestId
    });

    res.success({
      taskId,
      summary
    }, 'Сводка результатов задачи получена');

  } catch (error) {
    // Обработка ошибок NotFound
    if (error instanceof NotFoundError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getResultsSummary', {
      taskId,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения сводки результатов задачи');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/results/:taskId/export - Экспортирует результаты задачи в различных форматах
 */
const exportResults = async (req: Request<{ taskId: string }, {}, {}, { format?: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    logger.info('Processing exportResults request', {
      taskId,
      format: req.query.format,
      requestId
    });

    const format = req.query.format || 'json';

    if (!['json', 'csv', 'xlsx'].includes(format)) {
      const validationError = new ValidationError('Invalid export format', [
        {
          field: 'format',
          message: 'Format must be one of: json, csv, xlsx',
          value: format
        }
      ]);
      if (requestId) {
        validationError.setRequestId(requestId);
      }
      throw validationError;
    }

    // Получаем все результаты для экспорта
    const results = await dbRepo.getResults(taskId);

    if (!results || results.posts.length === 0) {
      const notFoundError = new NotFoundError('Task results for export', String(taskId));
      if (requestId) {
        notFoundError.setRequestId(requestId);
      }
      throw notFoundError;
    }

    logger.info('Results export prepared', {
      taskId,
      format,
      postsCount: results.posts.length,
      totalComments: results.totalComments,
      requestId
    });

    // Устанавливаем заголовки для экспорта
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `task_${taskId}_results_${timestamp}`;

    switch (format) {
      case 'json':
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}.json"`);
        res.json({
          taskId,
          posts: results.posts,
          totalComments: results.totalComments,
          exportedAt: new Date().toISOString()
        });
        break;

      case 'csv':
        // TODO: Implement CSV export
        res.setHeader('Content-Type', 'text/csv');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}.csv"`);
        res.error('CSV export not implemented yet', 501);
        break;

      case 'xlsx':
        // TODO: Implement XLSX export
        res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        res.setHeader('Content-Disposition', `attachment; filename="${filename}.xlsx"`);
        res.error('XLSX export not implemented yet', 501);
        break;
    }

  } catch (error) {
    // Передаем специфичные ошибки дальше
    if (error instanceof ValidationError || error instanceof NotFoundError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in exportResults', {
      taskId,
      format: req.query.format,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка экспорта результатов задачи');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// Маршруты
router.get('/results/:taskId', validateTaskIdParam, validateQuery(getResultsQuerySchema), getResults as any);
router.get('/results/:taskId/summary', validateTaskIdParam, getResultsSummary);
router.get('/results/:taskId/export', validateTaskIdParam, exportResults);

export default router;