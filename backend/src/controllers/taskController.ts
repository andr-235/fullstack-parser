import { Router, Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import taskService from '@/services/taskService';
import { queueService } from '@/services/queueService';
import vkIoService from '@/services/vkIoService';
import dbRepo from '@/repositories/dbRepo';
import { TaskStatus, TaskType, CreateTaskRequest } from '@/types/task';
import { ApiResponse, PaginationParams, PaginatedResponse, ErrorCodes } from '@/types/express';
import { ProgressCalculator } from '@/services/progressCalculator';
import {
  TaskCreateResponse,
  TaskProgressResponse,
  TaskListResponse
} from '@/types/api';
import {
  ValidationError,
  TaskError,
  VkApiError,
  NotFoundError,
  RateLimitError,
  ErrorUtils
} from '@/utils/errors';

const router = Router();

// Validation schema for task creation
const taskSchema = Joi.object({
  ownerId: Joi.number().integer().negative().required(),
  postId: Joi.number().integer().positive().required(),
  token: Joi.string().required()
});

// Validation schema for VK collect task creation
const vkCollectSchema = Joi.object({
  groups: Joi.array().items(
    Joi.alternatives().try(
      Joi.number().integer().positive(),
      Joi.string().pattern(/^\d+$/).custom((value: string) => parseInt(value)),
      Joi.object({
        id: Joi.alternatives().try(
          Joi.number().integer().positive(),
          Joi.string().pattern(/^\d+$/).custom((value: string) => parseInt(value))
        ).required(),
        name: Joi.string().required()
      })
    )
  ).min(1).required()
});

interface CreateTaskRequestBody {
  ownerId: number;
  postId: number;
  token: string;
}

interface VkCollectGroup {
  id?: number;
  name?: string;
}

interface VkCollectRequestBody {
  groups: (number | string | VkCollectGroup)[];
}

interface GetTasksQuery extends PaginationParams {
  status?: TaskStatus;
  type?: TaskType;
}

interface GetResultsQuery {
  groupId?: string;
  postId?: string;
}

/**
 * Создает задачу на сбор комментариев из VK.
 */
const createTask = async (req: Request<{}, ApiResponse, CreateTaskRequestBody>, res: Response): Promise<void> => {
  const requestId = (req as any).id;
  try {
    logger.info('Processing createTask request', {
      ownerId: req.body.ownerId,
      postId: req.body.postId,
      id: requestId
    });

    const { error, value } = taskSchema.validate(req.body);
    if (error) {
      logger.warn('Validation error in createTask', {
        details: error.details[0]?.message || 'Validation failed',
        id: requestId
      });

      const validationErrors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message,
        value: detail.context?.value
      }));

      res.validationError(validationErrors);
      return;
    }

    const { ownerId, postId, token } = value;
    const taskData: CreateTaskRequest = {
      type: 'fetch_comments',
      postUrls: [`${ownerId}_${postId}`],
      options: { token }
    };

    const { taskId } = await taskService.createTask(taskData);
    logger.info('Task created successfully', { taskId, status: 'created', id: requestId });

    res.status(201).success({
      taskId,
      status: 'created',
      type: taskData.type,
      createdAt: new Date().toISOString()
    }, 'Задача успешно создана');
  } catch (err) {
    const error = err as Error;
    if (error.name === 'ValidationError') {
      logger.warn('Validation error in createTask', {
        message: error.message,
        id: requestId
      });
      res.error(error.message, 400);
      return;
    }
    logger.error('Error in createTask', {
      error: error.stack,
      id: requestId
    });
    res.error('Ошибка создания задачи', 500);
  }
};

/**
 * Создает задачу на сбор постов и комментариев из VK групп через очередь BullMQ.
 */
const createVkCollectTask = async (req: Request<{}, ApiResponse, VkCollectRequestBody>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).id;
  try {
    logger.info('Processing createVkCollectTask request', {
      groupsCount: req.body.groups?.length,
      id: requestId
    });

    const { error, value } = vkCollectSchema.validate(req.body);
    if (error) {
      const validationError = ValidationError.fromJoi(error).setRequestId(requestId);
      logger.warn('Validation error in createVkCollectTask', {
        details: validationError.details,
        id: requestId
      });
      throw validationError;
    }

    const { groups } = value;

    // Нормализуем группы - убираем дубли и приводим к нужному формату
    const uniqueGroupIds: number[] = [];
    const seenIds = new Set<number>();

    for (const group of groups) {
      let groupId: number;

      if (typeof group === 'object' && group.id) {
        groupId = Number(group.id);
      } else {
        groupId = Number(group);
      }

      if (!isNaN(groupId) && !seenIds.has(groupId)) {
        seenIds.add(groupId);
        uniqueGroupIds.push(groupId);
      }
    }

    let groupsWithNames: { id: number; name: string }[] = [];

    try {
      // Получаем информацию о группах из VK API
      const groupsInfo = await vkIoService.getGroupsInfo(uniqueGroupIds);

      // Создаем map для быстрого поиска
      const groupInfoMap = new Map(groupsInfo.map(g => [g.id, g]));

      groupsWithNames = uniqueGroupIds.map(id => {
        const info = groupInfoMap.get(id);
        return {
          id,
          name: info ? info.name : `Группа ${id}`
        };
      });

      logger.info('Groups info fetched from VK API', {
        requested: uniqueGroupIds.length,
        found: groupsInfo.length,
        id: requestId
      });
    } catch (vkError) {
      const errorMsg = vkError instanceof Error ? vkError.message : String(vkError);
      logger.warn('Failed to fetch groups info from VK API, using fallback names', {
        error: errorMsg,
        groupIds: uniqueGroupIds,
        id: requestId
      });

      // Fallback: используем ID как имена
      groupsWithNames = uniqueGroupIds.map(id => ({
        id,
        name: `Группа ${id}`
      }));
    }

    // Create task in database
    const taskData: CreateTaskRequest = {
      type: 'fetch_comments',
      groupIds: uniqueGroupIds,
      options: {}
    };

    const { taskId } = await taskService.createTask(taskData);

    // Add job to BullMQ via QueueService (type-safe wrapper)
    try {
      // QueueService expects job data without taskId (it will be appended internally)
      const vkGroups = groupsWithNames.map(g => ({ vkId: String(g.id), name: g.name }));

      await queueService.addVkCollectJob(
        {
          type: 'fetch_comments',
          metadata: {
            groups: vkGroups,
            options: {}
          }
        },
        taskId
      );
    } catch (queueErr) {
      const errorMsg = queueErr instanceof Error ? queueErr.message : String(queueErr);
      logger.warn('Failed to enqueue VK collect job, task will still be created', {
        taskId,
        error: errorMsg,
        id: requestId
      });
    }

    logger.info('VK collect task created', {
      taskId,
      originalGroupsCount: groups.length,
      uniqueGroupsCount: groupsWithNames.length,
      id: requestId
    });

    res.status(201).success({
      taskId,
      status: 'created',
      type: taskData.type,
      groupsCount: groupsWithNames.length,
      createdAt: new Date().toISOString()
    }, 'Задача сбора VK комментариев создана');

  } catch (error) {
    // Обработка VK API ошибок
    if (error instanceof VkApiError) {
      logger.warn('VK API error in createVkCollectTask', {
        error: error.message,
        code: error.code,
        details: error.details,
        id: requestId
      });
      throw error;
    }

    // Обработка валидационных ошибок
    if (error instanceof ValidationError) {
      throw error;
    }

    // Общая ошибка
    const err = error as Error;
    logger.error('Error in createVkCollectTask', {
      error: err.message,
      stack: err.stack,
      id: requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка создания задачи VK').setRequestId(requestId);
    throw appError;
  }
};

/**
 * POST /api/collect/:taskId - Start collect
 */
const postCollect = async (req: Request<{ taskId: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).id;
  try {
    const taskId = Number(req.params.taskId);
    logger.info('Processing postCollect request', { taskId, id: requestId });

    if (isNaN(taskId)) {
      throw new ValidationError('Invalid task ID format', [
        {
          field: 'taskId',
          message: 'Task ID must be a valid number',
          value: req.params.taskId
        }
      ]).setRequestId(requestId);
    }

    const task = await taskService.getTaskById(taskId);
    if (!task) {
      logger.warn('Task not found in postCollect', { taskId, id: requestId });
      throw TaskError.notFound(String(taskId)).setRequestId(requestId);
    }

    const { status, startedAt } = await taskService.startCollect(taskId);
    logger.info('Collect started', { taskId, status, startedAt, id: requestId });

    res.status(202).json({
      success: true,
      data: { taskId, status: 'pending', startedAt }
    });
  } catch (error) {
    // Обработка rate limit ошибок
    if (error instanceof Error && error.message.includes('rate limit')) {
      logger.warn('Rate limit in postCollect', { taskId: req.params.taskId, id: requestId });
      throw new RateLimitError('Rate limit exceeded for VK API').setRequestId(requestId);
    }

    // Передаем уже обработанные AppError дальше
    if (error instanceof ValidationError || error instanceof TaskError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in postCollect', {
      taskId: req.params.taskId,
      error: err.message,
      stack: err.stack,
      id: requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка запуска сбора данных').setRequestId(requestId);
    throw appError;
  }
};

/**
 * GET /api/tasks/:taskId - Get task details
 */
const getTask = async (req: Request<{ taskId: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).id;
  try {
    const taskId = Number(req.params.taskId);
    if (isNaN(taskId)) {
      logger.warn('Invalid task ID provided', { taskId: req.params.taskId, id: requestId });
      throw new ValidationError('Invalid task ID format', [
        {
          field: 'taskId',
          message: 'Task ID must be a valid number',
          value: req.params.taskId
        }
      ]).setRequestId(requestId);
    }

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
        id: requestId
      });
    }

    // Рассчитываем точный прогресс
    const progressResult = ProgressCalculator.calculateProgress(metrics);

    logger.debug('Task progress calculated', {
      taskId,
      progressResult,
      metrics,
      id: requestId
    });

    // Возвращаем полную информацию о задаче с точным прогрессом
    res.json({
      success: true,
      data: {
        id: taskId,
        status: taskStatus.status,
        type: taskStatus.type,
        priority: taskStatus.priority,
        progress: {
          processed: progressResult.processed,
          total: progressResult.total,
          percentage: progressResult.percentage,
          phase: progressResult.phase,
          phases: progressResult.phases
        },
        metrics: {
          posts: taskStatus.metrics?.posts || 0,
          comments: taskStatus.metrics?.comments || 0,
          errors: taskStatus.metrics?.errors || 0
        },
        errors: taskStatus.errors || [],
        groups: taskStatus.groups,
        parameters: taskStatus.parameters,
        result: taskStatus.result,
        error: taskStatus.error,
        executionTime: taskStatus.executionTime,
        startedAt: taskStatus.startedAt,
        finishedAt: taskStatus.finishedAt,
        completedAt: taskStatus.finishedAt, // Alias для совместимости с frontend
        createdBy: taskStatus.createdBy,
        createdAt: taskStatus.createdAt,
        updatedAt: taskStatus.updatedAt
      }
    });
  } catch (error) {
    // Обработка ошибки "задача не найдена"
    if (error instanceof Error && error.message.includes('not found')) {
      logger.warn('Task not found', { taskId: req.params.taskId, id: requestId });
      throw TaskError.notFound(req.params.taskId).setRequestId(requestId);
    }

    // Передаем уже обработанные ошибки дальше
    if (error instanceof ValidationError || error instanceof TaskError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getTask', {
      taskId: req.params.taskId,
      error: err.message,
      stack: err.stack,
      id: requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения информации о задаче').setRequestId(requestId);
    throw appError;
  }
};

/**
 * Получает список задач с пагинацией и фильтрами.
 */
const getTasks = async (req: Request<{}, PaginatedResponse<any>, {}, GetTasksQuery>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).id;
  try {
    logger.info('Processing getTasks request', {
      page: req.query.page,
      limit: req.query.limit,
      status: req.query.status,
      type: req.query.type,
      id: requestId
    });

    // Validation schema for query params
    const querySchema = Joi.object({
      page: Joi.number().integer().min(1).default(1),
      limit: Joi.number().integer().min(1).max(100).default(10),
      status: Joi.string().valid('pending', 'processing', 'completed', 'failed').allow(null),
      type: Joi.string().valid('fetch_comments', 'process_groups', 'analyze_posts').allow(null)
    });

    const { error, value } = querySchema.validate(req.query);
    if (error) {
      const validationError = ValidationError.fromJoi(error).setRequestId(requestId);
      logger.warn('Validation error in getTasks', {
        details: validationError.details,
        id: requestId
      });
      throw validationError;
    }

  const { page = 1, limit = 20, status, type } = value as { page?: number; limit?: number; status?: any; type?: any };
  const { tasks, total } = await taskService.listTasks(page, limit, status, type);

    logger.info('Tasks listed successfully', {
      page,
      limit,
      status,
      type,
      total,
      id: requestId
    });

    const totalPages = Math.max(1, Math.ceil(total / limit));
    const response: PaginatedResponse<any> = {
      success: true,
      timestamp: new Date().toISOString(),
      data: tasks,
      pagination: {
        page,
        limit,
        total,
        totalPages,
        hasNext: page < totalPages,
        hasPrev: page > 1
      }
    };

    res.json({
      success: true,
      ...response
    });
  } catch (error) {
    // Передаем валидационные ошибки дальше
    if (error instanceof ValidationError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getTasks', {
      page: req.query.page,
      limit: req.query.limit,
      status: req.query.status,
      type: req.query.type,
      error: err.message,
      stack: err.stack,
      id: requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения списка задач').setRequestId(requestId);
    throw appError;
  }
};

/**
 * GET /api/results/:taskId - Get results
 */
const getResults = async (req: Request<{ taskId: string }, {}, {}, GetResultsQuery>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).id;
  try {
    const taskId = Number(req.params.taskId);
    if (isNaN(taskId)) {
      throw new ValidationError('Invalid task ID format', [
        {
          field: 'taskId',
          message: 'Task ID must be a valid number',
          value: req.params.taskId
        }
      ]).setRequestId(requestId);
    }

    const groupId = req.query.groupId ? Number(req.query.groupId) : undefined;
    const postId = req.query.postId ? Number(req.query.postId) : undefined;

    const results = await dbRepo.getResults(taskId, groupId, postId);
    res.json({
      success: true,
      data: results
    });
  } catch (error) {
    // Обработка ошибки "результаты не найдены"
    if (error instanceof Error && error.message.includes('not found')) {
      throw new NotFoundError('Task results', req.params.taskId).setRequestId(requestId);
    }

    // Передаем валидационные ошибки дальше
    if (error instanceof ValidationError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in getResults', {
      taskId: req.params.taskId,
      groupId: req.query.groupId,
      postId: req.query.postId,
      error: err.message,
      stack: err.stack,
      id: requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка получения результатов задачи').setRequestId(requestId);
    throw appError;
  }
};

// Routes
router.post('/tasks', createTask);
router.post('/tasks/collect', createVkCollectTask);
router.post('/collect/:taskId', postCollect);
router.get('/tasks/:taskId', getTask);
router.get('/tasks', getTasks);
router.get('/results/:taskId', getResults);

export default router;