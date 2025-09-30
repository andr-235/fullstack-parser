import { Router, Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import taskService from '@/services/taskService';
import { TaskStatus, TaskType, CreateTaskRequest } from '@/types/task';
import { ApiResponse, PaginationParams, PaginatedResponse } from '@/types/express';
import { ProgressCalculator } from '@/services/progressCalculator';
import {
  TaskCreateResponse,
  TaskProgressResponse,
  TaskListResponse
} from '@/types/api';
import {
  ValidationError,
  TaskError,
  ErrorUtils
} from '@/utils/errors';
import { validateBody, validateQuery, validateTaskIdParam, paginationSchema } from '@/middleware/validationMiddleware';

const router = Router();

// Validation schemas
const createTaskSchema = Joi.object({
  ownerId: Joi.number().integer().negative().required(),
  postId: Joi.number().integer().positive().required(),
  token: Joi.string().required()
});

const getTasksQuerySchema = paginationSchema.keys({
  status: Joi.string().valid('pending', 'processing', 'completed', 'failed').allow(null),
  type: Joi.string().valid('fetch_comments', 'process_groups', 'analyze_posts').allow(null)
});

// Типы для запросов
interface CreateTaskRequestBody {
  ownerId: number;
  postId: number;
  token: string;
}

interface GetTasksQuery extends PaginationParams {
  status?: TaskStatus;
  type?: TaskType;
}

/**
 * POST /api/tasks - Создает задачу на сбор комментариев из VK
 */
const createTask = async (req: Request<{}, ApiResponse, CreateTaskRequestBody>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  try {
    logger.info('Processing createTask request', {
      ownerId: req.body.ownerId,
      postId: req.body.postId,
      requestId
    });

    const { ownerId, postId, token } = req.body;
    const taskData: CreateTaskRequest = {
      type: 'fetch_comments',
      postUrls: [`${ownerId}_${postId}`],
      options: { token }
    };

    const { taskId } = await taskService.createTask(taskData);
    logger.info('Task created successfully', { taskId, status: 'created', requestId });

    res.status(201).success({
      taskId,
      status: 'created',
      type: taskData.type,
      createdAt: new Date().toISOString()
    }, 'Задача успешно создана');
  } catch (error) {
    const err = error as Error;
    logger.error('Error in createTask', {
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка создания задачи');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/tasks/:taskId - Получает детали задачи с прогрессом
 */
const getTask = async (req: Request<{ taskId: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    const taskStatus = await taskService.getTaskStatus(taskId);

    // Создаем метрики для расчета прогресса
    const metrics = ProgressCalculator.createMetricsFromTask(taskStatus);

    // Валидируем метрики для отладки
    const validationErrors = ProgressCalculator.validateMetrics(metrics);
    if (validationErrors.length > 0) {
      logger.warn('Progress metrics validation warnings', {
        taskId,
        errors: validationErrors,
        metrics,
        requestId
      });
    }

    // Рассчитываем точный прогресс
    const progressResult = ProgressCalculator.calculateProgress(metrics);

    logger.debug('Task progress calculated', {
      taskId,
      progressResult,
      metrics,
      requestId
    });

    // Возвращаем полную информацию о задаче с точным прогрессом
    res.success({
      taskId,
      status: taskStatus.status,
      type: taskStatus.type,
      createdAt: taskStatus.createdAt,
      updatedAt: taskStatus.updatedAt,
      progress: {
        ...progressResult,
        metrics
      }
    }, 'Информация о задаче получена');

  } catch (error) {
    // Обработка ошибки "задача не найдена"
    if (error instanceof Error && error.message.includes('not found')) {
      const taskError = TaskError.notFound(String(taskId));
      if (requestId) {
        taskError.setRequestId(requestId);
      }
      throw taskError;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getTask', {
      taskId,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения информации о задаче');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/tasks - Получает список задач с пагинацией и фильтрацией
 */
const getTasks = async (req: Request<{}, PaginatedResponse<any>, {}, GetTasksQuery>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  try {
    // Получаем валидированные query параметры из middleware
    const validatedQuery = (req as any).validatedQuery || req.query;
    const { page = 1, limit = 20, status, type } = validatedQuery;

    logger.info('Processing getTasks request', {
      page,
      limit,
      status,
      type,
      requestId
    });

    const { tasks, total } = await taskService.listTasks(page, limit, status, type);

    logger.info('Tasks listed successfully', {
      page,
      limit,
      status,
      type,
      total,
      requestId
    });

    const totalPages = Math.max(1, Math.ceil(total / limit));

    res.paginated(tasks, {
      page,
      limit,
      total,
      totalPages,
      hasNext: page < totalPages,
      hasPrev: page > 1
    });

  } catch (error) {
    // Общая обработка ошибок
    const err = error as Error;
    const validatedQuery = (req as any).validatedQuery || req.query;
    logger.error('Error in getTasks', {
      page: validatedQuery.page,
      limit: validatedQuery.limit,
      status: validatedQuery.status,
      type: validatedQuery.type,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения списка задач');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// Маршруты
router.post('/tasks', validateBody(createTaskSchema), createTask);
router.get('/tasks/:taskId', validateTaskIdParam, getTask);
router.get('/tasks', validateQuery(getTasksQuerySchema), getTasks);

export default router;