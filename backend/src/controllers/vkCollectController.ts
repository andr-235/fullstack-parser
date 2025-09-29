import { Router, Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import logger from '@/utils/logger';
import taskService from '@/services/taskService';
import { queueService } from '@/services/queueService';
import vkIoService from '@/services/vkIoService';
import { CreateTaskRequest } from '@/types/task';
import { ApiResponse } from '@/types/express';
import {
  ValidationError,
  TaskError,
  VkApiError,
  RateLimitError,
  ErrorUtils
} from '@/utils/errors';
import { validateBody } from '@/middleware/validationMiddleware';
import validateTaskId from '@/middleware/validateTaskId';

const router = Router();

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

// Типы для VK collect
interface VkCollectGroup {
  id?: number;
  name?: string;
}

interface VkCollectRequestBody {
  groups: (number | string | VkCollectGroup)[];
}

/**
 * POST /api/vk/collect - Создает задачу на сбор постов и комментариев из VK групп через очередь BullMQ
 */
const createVkCollectTask = async (req: Request<{}, ApiResponse, VkCollectRequestBody>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  try {
    logger.info('Processing createVkCollectTask request', {
      groupsCount: req.body.groups?.length,
      requestId
    });

    const { groups } = req.body;

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
        requestId
      });
    } catch (vkError) {
      const errorMsg = vkError instanceof Error ? vkError.message : String(vkError);
      logger.warn('Failed to fetch groups info from VK API, using fallback names', {
        error: errorMsg,
        groupIds: uniqueGroupIds,
        requestId
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
        requestId
      });
    }

    logger.info('VK collect task created', {
      taskId,
      originalGroupsCount: groups.length,
      uniqueGroupsCount: groupsWithNames.length,
      requestId
    });

    res.status(201).success({
      taskId,
      status: 'created',
      type: taskData.type,
      groupsCount: groupsWithNames.length,
      groups: groupsWithNames,
      createdAt: new Date().toISOString()
    }, 'Задача сбора VK комментариев создана');

  } catch (error) {
    // Обработка VK API ошибок
    if (error instanceof VkApiError) {
      logger.warn('VK API error in createVkCollectTask', {
        error: error.message,
        code: error.code,
        details: error.details,
        requestId
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
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка создания задачи VK');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * POST /api/vk/collect/:taskId/start - Запускает сбор данных для существующей задачи
 */
const startCollect = async (req: Request<{ taskId: string }>, res: Response, next: NextFunction): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    logger.info('Processing startCollect request', { taskId, requestId });

    const task = await taskService.getTaskById(taskId);
    if (!task) {
      logger.warn('Task not found in startCollect', { taskId, requestId });
      const taskError = TaskError.notFound(String(taskId));
      if (requestId) {
        taskError.setRequestId(requestId);
      }
      throw taskError;
    }

    const { status, startedAt } = await taskService.startCollect(taskId);
    logger.info('Collect started', { taskId, status, startedAt, requestId });

    res.status(202).success({
      taskId,
      status: 'pending',
      startedAt
    }, 'Сбор данных запущен');

  } catch (error) {
    // Обработка rate limit ошибок
    if (error instanceof Error && error.message.includes('rate limit')) {
      logger.warn('Rate limit in startCollect', { taskId: req.params.taskId, requestId });
      const rateLimitError = new RateLimitError('Rate limit exceeded for VK API');
      if (requestId) {
        rateLimitError.setRequestId(requestId);
      }
      throw rateLimitError;
    }

    // Передаем уже обработанные AppError дальше
    if (error instanceof ValidationError || error instanceof TaskError) {
      throw error;
    }

    // Общая обработка ошибок
    const err = error as Error;
    logger.error('Error in startCollect', {
      taskId: req.params.taskId,
      error: err.message,
      stack: err.stack,
      requestId
    });

    const appError = ErrorUtils.toAppError(err, 'Ошибка запуска сбора данных');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// Маршруты
router.post('/vk/collect', validateBody(vkCollectSchema), createVkCollectTask);
router.post('/vk/collect/:taskId/start', validateTaskId, startCollect);

export default router;