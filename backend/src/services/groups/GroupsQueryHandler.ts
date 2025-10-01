/**
 * @fileoverview GroupsQueryHandler - Обработчик запросов на получение групп
 *
 * Отвечает за:
 * - Получение списка групп с фильтрацией
 * - Получение статистики по группам
 * - Получение статуса задач загрузки
 */

import logger from '@/utils/logger';
import { GroupsRepository } from '@/repositories/groupsRepo';

import { GroupApiDto } from '@/domain/groups/types';
import {
  GetGroupsQuerySchema,
  validateSchema
} from '@/domain/groups/schemas';
import { GroupsDomainError } from '@/domain/groups/errors';
import { GroupMapper } from '@/domain/groups/mappers';

import { taskStorageService } from '@/infrastructure/storage/TaskStorageService';

/**
 * Параметры получения групп
 */
export interface GetGroupsParams {
  limit?: number;
  offset?: number;
  status?: string | undefined;
  search?: string | undefined;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

/**
 * Результат получения групп
 */
export interface GetGroupsResult {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

/**
 * Результат статуса задачи
 */
export interface TaskStatusResult {
  success: boolean;
  data?: {
    status: string;
    progress: {
      processed: number;
      total: number;
      percentage: number;
    };
    errors: string[];
  };
  error?: string;
  message?: string;
}

/**
 * Результат статистики
 */
export interface StatsResult {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

/**
 * Обработчик запросов на получение групп
 */
export class GroupsQueryHandler {
  constructor(private readonly groupsRepo: GroupsRepository) {}

  /**
   * Получает группы с фильтрацией
   * Использует GroupMapper для преобразования DB -> API
   */
  async getGroups(params: GetGroupsParams): Promise<GetGroupsResult> {
    try {
      // Валидация параметров через Zod
      const validatedParams = validateSchema(GetGroupsQuerySchema, params);

      const result = await this.groupsRepo.getGroups(validatedParams);

      // Преобразуем группы в формат API через GroupMapper
      const transformedResult = {
        ...result,
        groups: result.groups.map(group => GroupMapper.dbToApi(group))
      };

      return {
        success: true,
        data: transformedResult
      };
    } catch (error) {
      const errorMsg = error instanceof Error
        ? error.message
        : String(error);

      const errorCode = error instanceof GroupsDomainError
        ? error.code
        : 'GET_GROUPS_ERROR';

      logger.error('Get groups failed', { params, error: errorMsg });

      return {
        success: false,
        error: errorCode,
        message: errorMsg
      };
    }
  }

  /**
   * Получает статус задачи загрузки из Redis
   */
  async getUploadStatus(taskId: string): Promise<TaskStatusResult> {
    try {
      const task = await taskStorageService.getTask(taskId);

      if (!task) {
        return {
          success: false,
          error: 'TASK_NOT_FOUND',
          message: 'Upload task not found'
        };
      }

      const percentage = task.progress.total > 0
        ? (task.progress.processed / task.progress.total) * 100
        : 0;

      return {
        success: true,
        data: {
          status: task.status,
          progress: {
            processed: task.progress.processed,
            total: task.progress.total,
            percentage: Math.round(percentage * 100) / 100
          },
          errors: Array.from(task.errors)
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Get upload status failed', { taskId, error: errorMsg });

      return {
        success: false,
        error: 'GET_STATUS_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Получает статистику по группам
   */
  async getGroupsStats(taskId?: string): Promise<StatsResult> {
    try {
      const stats = await this.groupsRepo.getGroupsStats(taskId);

      return {
        success: true,
        data: stats
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Get groups stats failed', { taskId, error: errorMsg });

      return {
        success: false,
        error: 'GET_STATS_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Получает все задачи загрузки для мониторинга
   */
  async getAllUploadTasks() {
    try {
      const tasks = await taskStorageService.getAllTasks();
      return tasks;
    } catch (error) {
      logger.error('Get all upload tasks failed', {
        error: error instanceof Error ? error.message : String(error)
      });
      return [];
    }
  }
}
