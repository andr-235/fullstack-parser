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
      
      // Log sample parsed data for debugging (without raw lines to avoid scope issues)
      logger.info('Sample parsed groups (first 5)', {
        sampleParsed: parseResult.groups.slice(0, 5).map(g => ({ id: g.id, name: g.name, url: g.url })),
        totalParsed: parseResult.groups.length,
        parseErrors: parseResult.errors.slice(0, 3) // first 3 errors if any
      });

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

      // Enhanced logging for validation step
      logger.info('Validation result', {
        totalInputGroups: groups.length,
        validGroupsCount: validGroups.length,
        invalidGroupsCount: invalidGroups.length,
        sampleValid: validGroups.slice(0, 3).map(g => ({ id: g.id, name: g.name, error: g.error })),
        sampleInvalid: invalidGroups.slice(0, 3).map(g => ({ id: g.id, name: g.name, error: g.error }))
      });

      // Получаем информацию о группах из VK API - СТРОГАЯ ПРОВЕРКА
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

      // Извлекаем VK ID из групп (положительные)
      const vkIds = validGroups
        .map(group => group.id)
        .filter((id): id is number => id !== undefined && id > 0);

      logger.info('Запрос информации о группах из VK API', {
        requestedVkIds: vkIds.length,
        sampleVkIds: vkIds.slice(0, 5)
      });

      if (vkIds.length === 0) {
        logger.warn('Нет валидных VK ID для проверки', { taskId });
        // Все группы невалидные
        this.updateTaskStatus(taskId, 'completed', {
          validGroups: 0,
          invalidGroups: groups.length + parseErrors.length,
          duplicates: 0,
          completedAt: new Date()
        });
        return;
      }

      // Обязательный запрос к VK API для проверки существования групп
      try {
        const vkGroupsInfo = await vkIoService.getGroupsInfo(vkIds);

        logger.info('Ответ от VK API получен', {
          requestedCount: vkIds.length,
          receivedCount: vkGroupsInfo.length,
          missingCount: vkIds.length - vkGroupsInfo.length
        });

        // Создаем Map для быстрого поиска
        const vkGroupsMap = new Map<number, typeof vkGroupsInfo[0]>(
          vkGroupsInfo.map(g => [g.id, g])
        );

        // Проверяем каждый запрошенный ID
        for (const vkId of vkIds) {
          const vkInfo = vkGroupsMap.get(vkId);

          if (vkInfo) {
            // Группа существует в VK
            enrichedGroups.push({
              vk_id: vkId,
              name: vkInfo.name || `Группа ${vkId}`,
              screen_name: vkInfo.screen_name || null,
              photo_50: vkInfo.photo_50 || null,
              members_count: vkInfo.members_count || null,
              is_closed: vkInfo.is_closed ? Number(vkInfo.is_closed) : 0,
              description: vkInfo.description || null
            });
          } else {
            // Группа НЕ существует в VK
            invalidGroups.push({
              id: vkId,
              name: validGroups.find(g => g.id === vkId)?.name || `Группа ${vkId}`,
              error: 'Group does not exist or is not accessible'
            });
            logger.info('Группа не найдена в VK', { vkId });
          }
        }

        logger.info('Валидация через VK API завершена', {
          existingGroups: enrichedGroups.length,
          notFoundGroups: vkIds.length - enrichedGroups.length
        });

      } catch (vkError) {
        const errorMsg = vkError instanceof Error ? vkError.message : String(vkError);
        logger.error('Критическая ошибка при запросе к VK API', {
          taskId,
          error: errorMsg
        });

        // НЕ сохраняем группы если VK API недоступен
        throw new Error(`Не удалось проверить группы через VK API: ${errorMsg}`);
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

      // Log groups to save
      logger.info('Groups ready for DB save', {
        groupsToSaveCount: groupsToSave.length,
        duplicatesCount: duplicates,
        sampleToSave: groupsToSave.slice(0, 3).map(g => ({ vk_id: g.vk_id, name: g.name })),
        sampleDuplicates: enrichedGroups.slice(0, 3).filter(g => !groupsToSave.some(s => s.vk_id === g.vk_id)).map(g => ({ vk_id: g.vk_id, name: g.name }))
      });

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
   * Удаляет все группы из БД
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