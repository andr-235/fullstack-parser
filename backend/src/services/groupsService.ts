import { v4 as uuidv4 } from 'uuid';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

import FileParser from '@/utils/fileParser';
import VKValidator from '@/utils/vkValidator';
import vkIoService from '@/services/vkIoService';
import groupsRepo, { GroupsRepository } from '@/repositories/groupsRepo';
import logger from '@/utils/logger';
import { ProcessedGroup } from '@/types/common';

interface UploadTask {
  taskId: string;
  status: 'created' | 'processing' | 'completed' | 'failed';
  totalGroups: number;
  validGroups: number;
  invalidGroups: number;
  duplicates: number;
  errors: string[];
  createdAt: Date;
  startedAt: Date | null;
  completedAt: Date | null;
  error?: string;
}

interface UploadResult {
  success: boolean;
  data?: {
    taskId: string;
    totalGroups: number;
    validGroups: number;
    invalidGroups: number;
    duplicates: number;
  };
  error?: string;
  message?: string;
}

interface TaskStatusResult {
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

interface GetGroupsParams {
  limit?: number;
  offset?: number;
  status?: string | undefined;
  search?: string | undefined;
  sortBy?: string;
  sortOrder?: 'ASC' | 'DESC' | 'asc' | 'desc';
}

interface GetGroupsResult {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

interface DeleteResult {
  success: boolean;
  data?: {
    deletedCount: number;
    message: string;
  };
  error?: string;
  message?: string;
}

interface StatsResult {
  success: boolean;
  data?: any;
  error?: string;
  message?: string;
}

class GroupsService {
  private vkValidator: VKValidator | null = null;
  private uploadTasks = new Map<string, UploadTask>(); // Хранение задач загрузки
  private groupsRepo: GroupsRepository;

  constructor() {
    this.groupsRepo = groupsRepo;
  }

  /**
   * Инициализирует VK валидатор
   */
  initializeVKValidator(vkToken: string): void {
    this.vkValidator = new VKValidator({ accessToken: vkToken });
  }

  /**
   * Загружает группы из файла
   */
  async uploadGroups(filePath: string | Buffer, encoding: BufferEncoding = 'utf-8'): Promise<UploadResult> {
    const taskId = uuidv4();
    let tempPath: string | null = null;

    try {
      // Если это Buffer, сохраняем во временный файл
      let actualFilePath = filePath as string;
      if (Buffer.isBuffer(filePath)) {
        // Создаем папку для временных файлов
        const tempDir = path.join(os.tmpdir(), 'vk-uploads');
        await fs.mkdir(tempDir, { recursive: true });

        tempPath = path.join(tempDir, `temp-${Date.now()}-${Math.random().toString(36).substr(2, 9)}.txt`);
        await fs.writeFile(tempPath, filePath);
        actualFilePath = tempPath;
      }

      // Валидация файла
      const validationResult = await FileParser.validateFile(actualFilePath);
      if (!validationResult.isValid) {
        throw new Error(validationResult.errors.join(', '));
      }

      // Парсинг файла
      const parseResult = await FileParser.parseGroupsFile(actualFilePath, encoding);

      // Создаем задачу загрузки
      const uploadTask: UploadTask = {
        taskId,
        status: 'created',
        totalGroups: parseResult.groups.length,
        validGroups: 0,
        invalidGroups: 0,
        duplicates: 0,
        errors: parseResult.errors,
        createdAt: new Date(),
        startedAt: null,
        completedAt: null
      };

      this.uploadTasks.set(taskId, uploadTask);

      // Запускаем асинхронную обработку
      this.processGroupsAsync(taskId, parseResult.groups, parseResult.errors)
        .catch(error => {
          const errorMsg = error instanceof Error ? error.message : String(error);
          logger.error('Async processing failed', { taskId, error: errorMsg });
          this.updateTaskStatus(taskId, 'failed', { error: errorMsg });
        });

      // Удаляем временный файл если был создан
      if (tempPath) {
        await fs.unlink(tempPath);
      }

      return {
        success: true,
        data: {
          taskId,
          totalGroups: parseResult.groups.length,
          validGroups: 0, // Будет обновлено асинхронно
          invalidGroups: parseResult.errors.length,
          duplicates: 0
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Upload groups failed', { filePath, error: errorMsg });

      // Удаляем временный файл если был создан
      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (unlinkError) {
          const unlinkErrorMsg = unlinkError instanceof Error ? unlinkError.message : String(unlinkError);
          logger.warn('Failed to cleanup temp file', { tempPath, error: unlinkErrorMsg });
        }
      }

      return {
        success: false,
        error: 'UPLOAD_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Асинхронная обработка групп
   */
  private async processGroupsAsync(taskId: string, groups: ProcessedGroup[], parseErrors: string[]): Promise<void> {
    try {
      this.updateTaskStatus(taskId, 'processing', { startedAt: new Date() });

      let validGroups: ProcessedGroup[] = [];
      let invalidGroups: ProcessedGroup[] = [];
      let duplicates = 0;

      // Если есть VK валидатор, валидируем группы
      if (this.vkValidator) {
        const validationResult = await this.vkValidator.validateGroups(groups);
        validGroups = validationResult.validGroups;
        invalidGroups = validationResult.invalidGroups;
      } else {
        // Без VK валидации все группы считаем валидными
        validGroups = groups.map(group => ({
          ...group,
          error: group.error || ''
        }));
      }

      // Получаем информацию о группах из VK API
      let enrichedGroups: Array<{
        vk_id: number;
        name: string | null;
        screen_name: string | null;
        photo_50: string | null;
        members_count: number | null;
        is_closed: number;
        description: string | null;
        error?: string;
      }> = [];

      if (this.vkValidator) {
        try {
          // Извлекаем VK ID из групп
          const vkIds = validGroups
            .map(group => group.id)
            .filter((id): id is number => id !== undefined && id > 0);

          if (vkIds.length > 0) {
            // Получаем информацию о группах через VK API
            const vkGroupsInfo = await vkIoService.getGroupsInfo(vkIds);

            enrichedGroups = vkIds.map(vkId => {
              const vkInfo = vkGroupsInfo.find(info => info.id === vkId);
              return {
                vk_id: vkId,
                name: vkInfo?.name || `Группа ${vkId}`,
                screen_name: vkInfo?.screen_name || null,
                photo_50: vkInfo?.photo_50 || null,
                members_count: vkInfo?.members_count || null,
                is_closed: Number(vkInfo?.is_closed) || 0,
                description: vkInfo?.description || null
              };
            });
          }
        } catch (vkError) {
          const errorMsg = vkError instanceof Error ? vkError.message : String(vkError);
          logger.warn('Failed to get groups info from VK API, using fallback data', {
            taskId,
            error: errorMsg
          });

          // Fallback: создаем группы с базовой информацией
          enrichedGroups = validGroups
            .filter(group => group.id && group.id > 0)
            .map(group => ({
              vk_id: group.id!,
              name: group.name || `Группа ${group.id}`,
              screen_name: null,
              photo_50: null,
              members_count: null,
              is_closed: 0,
              description: null
            }));
        }
      } else {
        // Без VK валидатора создаем группы с базовой информацией
        enrichedGroups = validGroups
          .filter(group => group.id && group.id > 0)
          .map(group => ({
            vk_id: group.id!,
            name: group.name || `Группа ${group.id}`,
            screen_name: null,
            photo_50: null,
            members_count: null,
            is_closed: 0,
            description: null
          }));
      }

      // Проверяем дубликаты в БД по VK ID
      const groupsToSave = [];
      for (const group of enrichedGroups) {
        const exists = await this.groupsRepo.groupExistsByVkId(group.vk_id);
        if (exists) {
          duplicates++;
          invalidGroups.push({
            id: group.vk_id,
            name: group.name || '',
            error: 'Group already exists in database'
          });
        } else {
          groupsToSave.push(group);
        }
      }

      // Сохраняем группы в БД
      if (groupsToSave.length > 0) {
        await this.groupsRepo.createGroups(groupsToSave, taskId);
      }

      // Обновляем статистику задачи
      this.updateTaskStatus(taskId, 'completed', {
        validGroups: groupsToSave.length,
        invalidGroups: invalidGroups.length + parseErrors.length,
        duplicates,
        completedAt: new Date()
      });

      logger.info('Groups processing completed', {
        taskId,
        validGroups: groupsToSave.length,
        invalidGroups: invalidGroups.length,
        duplicates
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Groups processing failed', { taskId, error: errorMsg });
      this.updateTaskStatus(taskId, 'failed', {
        error: errorMsg,
        completedAt: new Date()
      });
    }
  }

  /**
   * Получает статус задачи загрузки
   */
  getUploadStatus(taskId: string): TaskStatusResult {
    const task = this.uploadTasks.get(taskId);
    if (!task) {
      return {
        success: false,
        error: 'TASK_NOT_FOUND',
        message: 'Upload task not found'
      };
    }

    const progress = task.totalGroups > 0
      ? (task.validGroups + task.invalidGroups) / task.totalGroups * 100
      : 0;

    return {
      success: true,
      data: {
        status: task.status,
        progress: {
          processed: task.validGroups + task.invalidGroups,
          total: task.totalGroups,
          percentage: Math.round(progress * 100) / 100
        },
        errors: task.errors || []
      }
    };
  }

  /**
   * Преобразует группу из формата БД в формат API (snake_case -> camelCase)
   */
  private transformGroupToApiFormat(group: any): any {
    return {
      id: group.id,
      name: group.name,
      status: group.status,
      uploadedAt: group.uploaded_at,
      taskId: group.task_id
    };
  }

  /**
   * Получает группы с фильтрацией
   */
  async getGroups(params: GetGroupsParams): Promise<GetGroupsResult> {
    try {
      const result = await this.groupsRepo.getGroups(params);

      // Преобразуем группы в формат camelCase для frontend
      const transformedResult = {
        ...result,
        groups: result.groups.map(group => this.transformGroupToApiFormat(group))
      };

      return {
        success: true,
        data: transformedResult
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Get groups failed', { params, error: errorMsg });
      return {
        success: false,
        error: 'GET_GROUPS_ERROR',
        message: errorMsg
      };
    }
  }

  /**
   * Обновляет статус задачи
   */
  private updateTaskStatus(taskId: string, status: UploadTask['status'], updates: Partial<UploadTask> = {}): void {
    const task = this.uploadTasks.get(taskId);
    if (task) {
      Object.assign(task, { status, ...updates });
      this.uploadTasks.set(taskId, task);
    }
  }

  /**
   * Удаляет группу
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
   * Получает задачи загрузки для мониторинга
   */
  getAllUploadTasks(): UploadTask[] {
    return Array.from(this.uploadTasks.values());
  }

  /**
   * Очищает завершенные задачи старше определенного времени
   */
  cleanupOldTasks(olderThanHours = 24): number {
    const cutoffTime = new Date();
    cutoffTime.setHours(cutoffTime.getHours() - olderThanHours);

    let removedCount = 0;

    for (const [taskId, task] of this.uploadTasks) {
      if ((task.status === 'completed' || task.status === 'failed') &&
          task.completedAt &&
          task.completedAt < cutoffTime) {
        this.uploadTasks.delete(taskId);
        removedCount++;
      }
    }

    if (removedCount > 0) {
      logger.info('Cleaned up old upload tasks', { removedCount, cutoffTime });
    }

    return removedCount;
  }
}

const groupsService = new GroupsService();
export default groupsService;
export { GroupsService };
export type {
  UploadTask,
  UploadResult,
  TaskStatusResult,
  GetGroupsParams,
  GetGroupsResult,
  DeleteResult,
  StatsResult
};