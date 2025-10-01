/**
 * @fileoverview GroupsDeleteHandler - Обработчик удаления групп
 *
 * Отвечает за:
 * - Удаление отдельных групп
 * - Массовое удаление групп
 * - Удаление всех групп
 * - Очистку старых задач
 */

import logger from '@/utils/logger';
import { GroupsRepository } from '@/repositories/groupsRepo';
import { taskStorageService } from '@/infrastructure/storage/TaskStorageService';

/**
 * Результат удаления
 */
export interface DeleteResult {
  success: boolean;
  data?: {
    deletedCount: number;
    message: string;
  };
  error?: string;
  message?: string;
}

/**
 * Обработчик удаления групп
 */
export class GroupsDeleteHandler {
  constructor(private readonly groupsRepo: GroupsRepository) {}

  /**
   * Удаляет группу по ID
   */
  async deleteGroup(groupId: string): Promise<DeleteResult> {
    try {
      const result = await this.groupsRepo.deleteGroup(Number(groupId));

      if (result) {
        return {
          success: true,
          message: 'Group deleted successfully'
        };
      } else {
        return {
          success: false,
          error: 'GROUP_NOT_FOUND',
          message: 'Group not found'
        };
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Delete group failed', { groupId, error: errorMsg });

      return {
        success: false,
        error: 'DELETE_GROUP_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Массовое удаление групп
   */
  async deleteGroups(groupIds: number[]): Promise<DeleteResult> {
    try {
      const result = await this.groupsRepo.deleteGroups(groupIds);

      return {
        success: true,
        data: {
          deletedCount: result,
          message: `${result} groups deleted successfully`
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Delete groups failed', { groupIds, error: errorMsg });

      return {
        success: false,
        error: 'DELETE_GROUPS_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Удаляет все группы из БД
   * ВНИМАНИЕ: Опасная операция!
   */
  async deleteAllGroups(): Promise<DeleteResult> {
    try {
      logger.warn('Deleting all groups from database');
      const result = await this.groupsRepo.deleteAllGroups();

      return {
        success: true,
        data: {
          deletedCount: result,
          message: `All groups deleted successfully (${result} groups)`
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Delete all groups failed', { error: errorMsg });

      return {
        success: false,
        error: 'DELETE_ALL_GROUPS_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Очищает завершенные задачи старше определенного времени
   */
  async cleanupOldTasks(olderThanHours = 24): Promise<number> {
    try {
      const removedCount = await taskStorageService.cleanupOldTasks(olderThanHours);

      if (removedCount > 0) {
        logger.info('Cleaned up old upload tasks', { removedCount, olderThanHours });
      }

      return removedCount;
    } catch (error) {
      logger.error('Cleanup old tasks failed', {
        olderThanHours,
        error: error instanceof Error ? error.message : String(error)
      });
      return 0;
    }
  }
}
