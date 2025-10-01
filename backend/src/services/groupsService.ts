import { v4 as uuidv4 } from 'uuid';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

import { FileParserFactory } from '@/utils/fileParser/FileParserFactory';
import vkIoService, { ProcessedGroup as VkProcessedGroup } from '@/services/vkIoService';
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
  private uploadTasks = new Map<string, UploadTask>(); // Хранение задач загрузки
  private groupsRepo: GroupsRepository;

  constructor() {
    this.groupsRepo = groupsRepo;
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

      // Создаем парсер
      const parser = FileParserFactory.create();

      // Валидация файла
      const validationResult = await parser.validateFile(actualFilePath);
      if (!validationResult.isValid) {
        throw new Error(validationResult.errors.join(', '));
      }

      // Парсинг файла
      const parseResult = await parser.parseGroupsFile(actualFilePath, encoding);
      
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
      const invalidGroups: ProcessedGroup[] = [];
      let duplicates = 0;

      // ШАГ 1: Подготавливаем идентификаторы групп (ID или screen_names)
      const groupIdentifiers: Array<number | string> = groups.map(g => {
        // Если есть ID - используем его, иначе используем screen_name
        return g.id || g.name!;
      }).filter(id => id !== undefined);

      logger.info('Подготовка идентификаторов групп', {
        totalGroups: groups.length,
        identifiersCount: groupIdentifiers.length,
        sampleIdentifiers: groupIdentifiers.slice(0, 5)
      });

      // Все группы считаем потенциально валидными
      validGroups = groups.map(group => ({
        ...group,
        error: group.error || ''
      }));

      // Enhanced logging for validation step
      logger.info('Validation result', {
        totalInputGroups: groups.length,
        validGroupsCount: validGroups.length,
        invalidGroupsCount: invalidGroups.length,
        sampleValid: validGroups.slice(0, 3).map(g => ({
          id: g.id,
          name: g.name,
          screenName: (g as any).screenName,
          error: g.error
        })),
        sampleInvalid: invalidGroups.slice(0, 3).map(g => ({ id: g.id, name: g.name, error: g.error }))
      });

      // ШАГ 2: Получаем полную информацию о группах из VK API (батч-запрос)
      const enrichedGroups: Array<{
        vk_id: number;
        name: string | null;
        screen_name: string | null;
        photo_50: string | null;
        members_count: number | null;
        is_closed: number;
        description: string | null;
        error?: string;
      }> = [];

      logger.info('Запрос информации о группах из VK API', {
        totalIdentifiers: groupIdentifiers.length,
        sampleIdentifiers: groupIdentifiers.slice(0, 5)
      });

      if (groupIdentifiers.length === 0) {
        logger.warn('Нет идентификаторов групп для проверки', { taskId });
        this.updateTaskStatus(taskId, 'completed', {
          validGroups: 0,
          invalidGroups: groups.length + parseErrors.length,
          duplicates: 0,
          completedAt: new Date()
        });
        return;
      }

      // Батч-запрос к VK API для получения полной информации о всех группах
      try {
        // Разбиваем на батчи по 500 групп (лимит VK API)
        const batchSize = 500;
        const vkGroupsInfo: VkProcessedGroup[] = [];

        for (let i = 0; i < groupIdentifiers.length; i += batchSize) {
          const batch = groupIdentifiers.slice(i, i + batchSize);
          logger.info('Батч-запрос информации о группах', {
            batchNumber: Math.floor(i / batchSize) + 1,
            batchSize: batch.length,
            totalBatches: Math.ceil(groupIdentifiers.length / batchSize)
          });

          const batchInfo = await vkIoService.getGroupsInfo(batch);
          vkGroupsInfo.push(...batchInfo);

          // Небольшая задержка между батчами
          if (i + batchSize < groupIdentifiers.length) {
            await new Promise(resolve => setTimeout(resolve, 400));
          }
        }

        logger.info('Батч-запросы завершены', {
          requestedCount: groupIdentifiers.length,
          receivedCount: vkGroupsInfo.length,
          notFoundCount: groupIdentifiers.length - vkGroupsInfo.length
        });

        // Преобразуем полученную информацию в формат для БД
        for (const vkInfo of vkGroupsInfo) {
          enrichedGroups.push({
            vk_id: vkInfo.id,
            name: vkInfo.name || `Группа ${vkInfo.id}`,
            screen_name: vkInfo.screen_name || null,
            photo_50: vkInfo.photo_50 || null,
            members_count: vkInfo.members_count || null,
            is_closed: vkInfo.is_closed ? Number(vkInfo.is_closed) : 0,
            description: vkInfo.description || null
          });
        }

        // Группы, которые не были найдены через VK API - добавляем в invalidGroups
        const foundIds = new Set(vkGroupsInfo.map(g => g.id));
        const foundScreenNames = new Set(vkGroupsInfo.map(g => g.screen_name).filter(Boolean));

        for (const group of validGroups) {
          const identifier = group.id || group.name;
          const isFound = typeof identifier === 'number'
            ? foundIds.has(identifier)
            : foundScreenNames.has(identifier as string);

          if (!isFound) {
            invalidGroups.push({
              ...group,
              error: 'Group not found or not accessible via VK API'
            });
            logger.warn('Группа не найдена через VK API', {
              identifier
            });
          }
        }

        logger.info('Валидация через VK API завершена', {
          totalGroups: enrichedGroups.length,
          invalidGroups: invalidGroups.length,
          sampleGroups: enrichedGroups.slice(0, 3).map(g => ({
            vk_id: g.vk_id,
            name: g.name,
            screen_name: g.screen_name,
            photo_50: g.photo_50?.substring(0, 50),
            members_count: g.members_count,
            is_closed: g.is_closed
          }))
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
      vkId: group.vk_id,
      name: group.name,
      screenName: group.screen_name,
      photo50: group.photo_50,
      membersCount: group.members_count,
      isClosed: group.is_closed,
      description: group.description,
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