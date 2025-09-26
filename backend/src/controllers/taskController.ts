import { Router, Request, Response } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import taskService from '@/services/taskService';
import vkService from '@/services/vkService';
import { VkApiRepository } from '@/repositories/vkApi';
import { TaskStatus, TaskType, CreateTaskRequest } from '@/types/task';
import { ApiResponse, PaginationParams, PaginatedResponse } from '@/types/express';

const router = Router();
const vkApi = new VkApiRepository();

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
  const requestId = req.id;
  try {
    logger.info('Processing createTask request', {
      ownerId: req.body.ownerId,
      postId: req.body.postId,
      id: requestId
    });

    const { error, value } = taskSchema.validate(req.body);
    if (error) {
      logger.warn('Validation error in createTask', {
        details: error.details[0].message,
        id: requestId
      });
      res.status(400).json({
        success: false,
        error: error.details[0].message
      });
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

    res.status(201).json({
      success: true,
      data: { taskId, status: 'created' }
    });
  } catch (err) {
    const error = err as Error;
    if (error.name === 'ValidationError') {
      logger.warn('Validation error in createTask', {
        message: error.message,
        id: requestId
      });
      res.status(400).json({
        success: false,
        error: error.message
      });
      return;
    }
    logger.error('Error in createTask', {
      error: error.stack,
      id: requestId
    });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

/**
 * Создает задачу на сбор постов и комментариев из VK групп через очередь BullMQ.
 */
const createVkCollectTask = async (req: Request<{}, ApiResponse, VkCollectRequestBody>, res: Response): Promise<void> => {
  const requestId = req.id;
  try {
    logger.info('Processing createVkCollectTask request', {
      groupsCount: req.body.groups?.length,
      id: requestId
    });

    const { error, value } = vkCollectSchema.validate(req.body);
    if (error) {
      logger.warn('Validation error in createVkCollectTask', {
        details: error.details[0].message,
        id: requestId
      });
      res.status(400).json({
        success: false,
        error: error.details[0].message
      });
      return;
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
      const groupsInfo = await vkApi.getGroupsInfo(uniqueGroupIds);

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

    // TODO: Add job to BullMQ queue when queue is migrated to TypeScript
    // await queue.add('vk-collect', { taskId }, {
    //   delay: 1000,
    //   attempts: 3,
    //   backoff: {
    //     type: 'exponential',
    //     delay: 5000,
    //   },
    //   removeOnComplete: 100,
    //   removeOnFail: 50
    // });

    logger.info('VK collect task created', {
      taskId,
      originalGroupsCount: groups.length,
      uniqueGroupsCount: groupsWithNames.length,
      id: requestId
    });

    res.status(201).json({
      success: true,
      data: { taskId, status: 'created' }
    });

  } catch (err) {
    const error = err as Error;
    logger.error('Error in createVkCollectTask', {
      error: error.stack,
      id: requestId
    });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

/**
 * POST /api/collect/:taskId - Start collect
 */
const postCollect = async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  const requestId = req.id;
  try {
    const taskId = Number(req.params.taskId);
    logger.info('Processing postCollect request', { taskId, id: requestId });

    if (isNaN(taskId)) {
      res.status(400).json({
        success: false,
        error: 'Invalid task ID'
      });
      return;
    }

    const task = await taskService.getTaskById(taskId);
    if (!task) {
      logger.warn('Task not found in postCollect', { taskId, id: requestId });
      res.status(404).json({
        success: false,
        error: 'Task not found'
      });
      return;
    }

    const { status, startedAt } = await taskService.startCollect(taskId);
    logger.info('Collect started', { taskId, status, startedAt, id: requestId });

    res.status(202).json({
      success: true,
      data: { taskId, status: 'pending', startedAt }
    });
  } catch (err) {
    const error = err as Error;
    if (error.message.includes('rate limit')) {
      logger.warn('Rate limit in postCollect', { taskId: req.params.taskId, id: requestId });
      res.status(429).json({
        success: false,
        error: 'Rate limit exceeded'
      });
      return;
    }
    if (error.name === 'ValidationError') {
      logger.warn('Validation error in postCollect', { message: error.message, id: requestId });
      res.status(400).json({
        success: false,
        error: error.message
      });
      return;
    }
    logger.error('Error in postCollect', {
      taskId: req.params.taskId,
      error: error.stack,
      id: requestId
    });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

/**
 * GET /api/tasks/:taskId - Get task status
 */
const getTask = async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  try {
    const taskId = Number(req.params.taskId);
    if (isNaN(taskId)) {
      res.status(400).json({
        success: false,
        error: 'Invalid task ID'
      });
      return;
    }

    const taskStatus = await taskService.getTaskStatus(taskId);
    res.json({
      success: true,
      data: {
        status: taskStatus.status,
        progress: taskStatus.progress,
        errors: taskStatus.errors || []
      }
    });
  } catch (err) {
    const error = err as Error;
    if (error.message.includes('not found')) {
      res.status(404).json({
        success: false,
        error: 'Task not found'
      });
      return;
    }
    logger.error('Error in getTask', { taskId: req.params.taskId, error: error.message });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

/**
 * Получает список задач с пагинацией и фильтрами.
 */
const getTasks = async (req: Request<{}, PaginatedResponse<any>, {}, GetTasksQuery>, res: Response): Promise<void> => {
  const requestId = req.id;
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
      logger.warn('Validation error in getTasks', {
        details: error.details[0].message,
        id: requestId
      });
      res.status(400).json({
        success: false,
        error: error.details[0].message
      });
      return;
    }

    const { page, limit, status, type } = value;
    const { tasks, total } = await taskService.listTasks(page, limit, status, type);

    logger.info('Tasks listed successfully', {
      page,
      limit,
      status,
      type,
      total,
      id: requestId
    });

    const response: PaginatedResponse<any> = {
      data: tasks,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit)
      }
    };

    res.json({
      success: true,
      ...response
    });
  } catch (err) {
    const error = err as Error;
    if (error.name === 'ValidationError') {
      logger.warn('Validation error in getTasks', {
        message: error.message,
        id: requestId
      });
      res.status(400).json({
        success: false,
        error: error.message
      });
      return;
    }
    logger.error('Error in getTasks', {
      page: req.query.page,
      limit: req.query.limit,
      status: req.query.status,
      type: req.query.type,
      error: error.message,
      id: requestId
    });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
  }
};

/**
 * GET /api/results/:taskId - Get results
 */
const getResults = async (req: Request<{ taskId: string }, {}, {}, GetResultsQuery>, res: Response): Promise<void> => {
  try {
    const taskId = Number(req.params.taskId);
    if (isNaN(taskId)) {
      res.status(400).json({
        success: false,
        error: 'Invalid task ID'
      });
      return;
    }

    const groupId = req.query.groupId ? Number(req.query.groupId) : undefined;
    const postId = req.query.postId ? Number(req.query.postId) : undefined;

    const results = await vkService.getResults(taskId, groupId, postId);
    res.json({
      success: true,
      data: results
    });
  } catch (err) {
    const error = err as Error;
    if (error.message.includes('not found')) {
      res.status(404).json({
        success: false,
        error: 'Results not found'
      });
      return;
    }
    logger.error('Error in getResults', {
      taskId: req.params.taskId,
      groupId: req.query.groupId,
      postId: req.query.postId,
      error: error.message
    });
    res.status(500).json({
      success: false,
      error: 'Internal server error'
    });
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