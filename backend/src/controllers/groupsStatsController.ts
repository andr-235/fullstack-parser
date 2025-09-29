import express, { Request, Response } from 'express';
import Joi from 'joi';
import groupsService from '@/services/groupsService';
import logger from '@/utils/logger';
import { GroupsStatsResponse } from '@/types/api';
import {
  ValidationError,
  NotFoundError,
  ErrorUtils
} from '@/utils/errors';
import { validateParams, taskIdParamSchema } from '@/middleware/validationMiddleware';
import validateTaskId from '@/middleware/validateTaskId';

const router = express.Router();

/**
 * GET /api/stats/groups - Получение общей статистики по группам
 */
const getGroupsStats = async (req: Request, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.info('Processing getGroupsStats request', { requestId });

    const result = await groupsService.getGroupsStats();

    if (result.success) {
      logger.info('Groups stats retrieved successfully', {
        statsData: result.data,
        requestId
      });
      res.success(result.data, 'Статистика по группам получена');
    } else {
      logger.warn('Failed to get groups stats', {
        error: result.error,
        message: result.message,
        requestId
      });
      res.error(result.message || 'Ошибка получения статистики групп', 500, {
        details: result.error
      });
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения статистики групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/stats/groups/:taskId - Получение статистики по группам для конкретной задачи
 */
const getGroupsStatsByTask = async (req: Request<{ taskId: string }>, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;
  const taskId = (req as any).validatedTaskId; // Получаем из middleware

  try {
    logger.info('Processing getGroupsStatsByTask request', {
      taskId,
      requestId
    });

    const result = await groupsService.getGroupsStats(String(taskId));

    if (result.success) {
      logger.info('Groups stats by task retrieved successfully', {
        taskId,
        statsData: result.data,
        requestId
      });
      res.success(result.data, `Статистика по группам для задачи ${taskId} получена`);
    } else {
      // Если задача не найдена или нет статистики для неё
      if (result.message?.includes('not found') || result.message?.includes('No stats found')) {
        const notFoundError = new NotFoundError('Groups stats for task', String(taskId));
        if (requestId) {
          notFoundError.setRequestId(requestId);
        }
        throw notFoundError;
      }

      logger.warn('Failed to get groups stats by task', {
        taskId,
        error: result.error,
        message: result.message,
        requestId
      });
      res.error(result.message || 'Ошибка получения статистики групп по задаче', 500, {
        taskId,
        details: result.error
      });
    }

  } catch (error) {
    // Передаем NotFoundError дальше
    if (error instanceof NotFoundError) {
      throw error;
    }

    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups stats by task controller error', {
      taskId,
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения статистики групп по задаче');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/stats/groups/summary - Получение сводной статистики по всем группам
 */
const getGroupsSummary = async (req: Request, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.info('Processing getGroupsSummary request', { requestId });

    // Получаем общую статистику
    const statsResult = await groupsService.getGroupsStats();

    if (statsResult.success && statsResult.data) {
      // Формируем сводку на основе статистики
      const summary = {
        totalGroups: statsResult.data.totalGroups || 0,
        activeGroups: statsResult.data.activeGroups || 0,
        inactiveGroups: statsResult.data.inactiveGroups || 0,
        groupsWithComments: statsResult.data.groupsWithComments || 0,
        totalComments: statsResult.data.totalComments || 0,
        averageCommentsPerGroup: statsResult.data.totalGroups > 0
          ? Math.round((statsResult.data.totalComments || 0) / statsResult.data.totalGroups * 100) / 100
          : 0,
        lastUpdated: new Date().toISOString()
      };

      logger.info('Groups summary calculated successfully', {
        summary,
        requestId
      });

      res.success(summary, 'Сводная статистика по группам получена');
    } else {
      logger.warn('Failed to get groups summary', {
        error: statsResult.error,
        message: statsResult.message,
        requestId
      });
      res.error(statsResult.message || 'Ошибка получения сводной статистики групп', 500, {
        details: statsResult.error
      });
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups summary controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения сводной статистики групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

/**
 * GET /api/stats/groups/activity - Получение статистики активности групп
 */
const getGroupsActivity = async (req: Request, res: Response): Promise<void> => {
  const requestId = (req as any).requestId || (req as any).id;

  try {
    logger.info('Processing getGroupsActivity request', { requestId });

    // Получаем данные для анализа активности
    const result = await groupsService.getGroupsStats();

    if (result.success && result.data) {
      // Формируем статистику активности
      const activity = {
        mostActiveGroups: result.data.mostActiveGroups || [],
        leastActiveGroups: result.data.leastActiveGroups || [],
        recentlyAddedGroups: result.data.recentlyAddedGroups || [],
        groupsActivityTrend: result.data.groupsActivityTrend || {},
        activityScore: {
          high: result.data.highActivityGroups || 0,
          medium: result.data.mediumActivityGroups || 0,
          low: result.data.lowActivityGroups || 0,
          none: result.data.inactiveGroups || 0
        },
        generatedAt: new Date().toISOString()
      };

      logger.info('Groups activity stats calculated successfully', {
        highActivity: activity.activityScore.high,
        mediumActivity: activity.activityScore.medium,
        lowActivity: activity.activityScore.low,
        requestId
      });

      res.success(activity, 'Статистика активности групп получена');
    } else {
      logger.warn('Failed to get groups activity', {
        error: result.error,
        message: result.message,
        requestId
      });
      res.error(result.message || 'Ошибка получения статистики активности групп', 500, {
        details: result.error
      });
    }

  } catch (error) {
    const errorMsg = error instanceof Error ? error.message : String(error);
    logger.error('Get groups activity controller error', {
      error: errorMsg,
      requestId
    });

    const appError = ErrorUtils.toAppError(error as Error, 'Ошибка получения статистики активности групп');
    if (requestId) {
      appError.setRequestId(requestId);
    }
    throw appError;
  }
};

// Маршруты
router.get('/stats/groups', getGroupsStats);
router.get('/stats/groups/summary', getGroupsSummary);
router.get('/stats/groups/activity', getGroupsActivity);
router.get('/stats/groups/:taskId', validateTaskId, getGroupsStatsByTask);

export default router;