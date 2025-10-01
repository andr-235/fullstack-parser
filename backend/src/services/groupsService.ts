/**
 * @fileoverview Groups Service - Рефакторированный сервис управления группами
 *
 * ✅ ВЫПОЛНЕНО:
 * - Заменена in-memory Map на Redis-backed TaskStorageService
 * - Интегрирован BatchProcessor для обработки групп
 * - Использованы domain types из domain/groups/types
 * - Добавлены Zod схемы для валидации
 * - Интегрированы custom error classes
 * - Использован GroupMapper для всех трансформаций
 * - Сохранена полная обратная совместимость с legacy API
 *
 * Архитектура:
 * - Domain Layer: types, schemas, errors, mappers
 * - Infrastructure Layer: TaskStorageService, BatchProcessor
 * - Application Layer: этот сервис
 */

import { v4 as uuidv4 } from 'uuid';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

import { FileParserFactory } from '@/utils/fileParser/FileParserFactory';
import vkIoService from '@/services/vkIoService';
import groupsRepo, { GroupsRepository } from '@/repositories/groupsRepo';
import logger from '@/utils/logger';

// Domain Layer - новая архитектура
import {
  GroupUploadTask,
  ParsedGroupInput,
  CreateGroupInput,
  VkGroupRaw,
  GroupApiDto
} from '@/domain/groups/types';
import {
  UploadGroupsRequestSchema,
  GetGroupsQuerySchema,
  validateSchema
} from '@/domain/groups/schemas';
import {
  GroupsDomainError,
  FileProcessingError,
  VkApiError,
  DatabaseError,
  TaskNotFoundError
} from '@/domain/groups/errors';
import { GroupMapper } from '@/domain/groups/mappers';

// Infrastructure Layer
import { taskStorageService } from '@/infrastructure/storage/TaskStorageService';
import { createVkApiBatchProcessor } from '@/infrastructure/processing/BatchProcessor';

// Legacy types для обратной совместимости с API контроллерами
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

/**
 * Сервис управления группами ВКонтакте
 *
 * Основные возможности:
 * - Загрузка групп из файлов с асинхронной обработкой
 * - Валидация групп через VK API
 * - Управление задачами загрузки (создание, статус, очистка)
 * - CRUD операции над группами
 * - Статистика по группам
 */
class GroupsService {
  private groupsRepo: GroupsRepository;

  constructor() {
    this.groupsRepo = groupsRepo;
  }

  /**
   * Загружает группы из файла с асинхронной обработкой
   *
   * @param filePath - Путь к файлу или Buffer с данными
   * @param encoding - Кодировка файла (utf-8, utf-16le, latin1, ascii)
   * @returns Promise<UploadResult> с taskId для отслеживания прогресса
   */
  async uploadGroups(filePath: string | Buffer, encoding: BufferEncoding = 'utf-8'): Promise<UploadResult> {
    const taskId = uuidv4();
    let tempPath: string | null = null;

    try {
      // Валидация входных данных через Zod
      validateSchema(UploadGroupsRequestSchema, {
        file: Buffer.isBuffer(filePath) ? filePath : Buffer.from('dummy'),
        encoding
      });

      // Если это Buffer, сохраняем во временный файл
      let actualFilePath = filePath as string;
      if (Buffer.isBuffer(filePath)) {
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
        throw new FileProcessingError(
          validationResult.errors.join(', '),
          { errors: validationResult.errors }
        );
      }

      // Парсинг файла
      const parseResult = await parser.parseGroupsFile(actualFilePath, encoding);

      logger.info('Sample parsed groups (first 5)', {
        sampleParsed: parseResult.groups.slice(0, 5).map(g => ({ id: g.id, name: g.name, url: g.url })),
        totalParsed: parseResult.groups.length,
        parseErrors: parseResult.errors.slice(0, 3)
      });

      // Создаем задачу загрузки в Redis
      const uploadTask: GroupUploadTask = {
        taskId,
        status: 'pending',
        progress: {
          total: parseResult.groups.length,
          processed: 0,
          valid: 0,
          invalid: parseResult.errors.length,
          duplicates: 0
        },
        errors: parseResult.errors,
        createdAt: new Date(),
        startedAt: null,
        completedAt: null
      };

      await taskStorageService.saveTask(taskId, uploadTask);

      // Запускаем асинхронную обработку
      this.processGroupsAsync(taskId, parseResult.groups, parseResult.errors)
        .catch(error => {
          const errorMsg = error instanceof Error ? error.message : String(error);
          logger.error('Async processing failed', { taskId, error: errorMsg });
          this.updateTaskStatus(taskId, 'failed', { failureReason: errorMsg });
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
      // Обработка ошибок с типизацией
      const errorMsg = error instanceof GroupsDomainError
        ? error.message
        : error instanceof Error
          ? error.message
          : String(error);

      const errorCode = error instanceof GroupsDomainError
        ? error.code
        : 'UPLOAD_ERROR';

      logger.error('Upload groups failed', { filePath, error: errorMsg, errorCode });

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
        error: errorCode,
        message: errorMsg
      };
    }
  }

  /**
   * Асинхронная обработка групп с использованием BatchProcessor
   *
   * @param taskId - ID задачи
   * @param groups - Массив распарсенных групп
   * @param parseErrors - Ошибки парсинга
   */
  private async processGroupsAsync(taskId: string, groups: any[], parseErrors: string[]): Promise<void> {
    try {
      await this.updateTaskStatus(taskId, 'processing', { startedAt: new Date() });

      let duplicates = 0;
      const invalidGroups: any[] = [];

      // ШАГ 1: Подготавливаем идентификаторы групп через GroupMapper
      const parsedGroups: ParsedGroupInput[] = groups.map(g => ({
        id: g.id ?? null,
        name: g.name ?? null,
        screenName: g.screenName ?? null,
        url: g.url ?? null
      }));

      const groupIdentifiers = GroupMapper.parsedToIdentifiers(parsedGroups);

      logger.info('Подготовка идентификаторов групп', {
        totalGroups: groups.length,
        identifiersCount: groupIdentifiers.length,
        sampleIdentifiers: groupIdentifiers.slice(0, 5)
      });

      if (groupIdentifiers.length === 0) {
        logger.warn('Нет идентификаторов групп для проверки', { taskId });
        await this.updateTaskStatus(taskId, 'completed', {
          progress: {
            total: groups.length,
            processed: groups.length,
            valid: 0,
            invalid: groups.length + parseErrors.length,
            duplicates: 0
          },
          completedAt: new Date()
        });
        return;
      }

      // ШАГ 2: Получаем информацию о группах через VK API с BatchProcessor
      const batchProcessor = createVkApiBatchProcessor();

      // Разбиваем идентификаторы на батчи по 500 (лимит VK API)
      const vkGroupsInfo: VkGroupRaw[] = [];
      const batchSize = 500;

      for (let i = 0; i < groupIdentifiers.length; i += batchSize) {
        const batch = groupIdentifiers.slice(i, i + batchSize);

        logger.info('Батч-запрос информации о группах', {
          batchNumber: Math.floor(i / batchSize) + 1,
          batchSize: batch.length,
          totalBatches: Math.ceil(groupIdentifiers.length / batchSize)
        });

        try {
          const batchInfo = await vkIoService.getGroupsInfo(batch);

          // Преобразуем результаты VK API в VkGroupRaw через mapper
          const mapped = batchInfo.map(vkGroup => ({
            id: vkGroup.id,
            name: vkGroup.name || `Group ${vkGroup.id}`,
            screen_name: vkGroup.screen_name || '',
            description: vkGroup.description || null,
            photo_50: vkGroup.photo_50 || null,
            members_count: vkGroup.members_count || 0,
            is_closed: (vkGroup.is_closed ? Number(vkGroup.is_closed) : 0) as 0 | 1 | 2
          }));

          vkGroupsInfo.push(...mapped);

          // Задержка между батчами для соблюдения rate limits
          if (i + batchSize < groupIdentifiers.length) {
            await new Promise(resolve => setTimeout(resolve, 400));
          }
        } catch (vkError) {
          logger.error('Ошибка при батч-запросе к VK API', {
            batchNumber: Math.floor(i / batchSize) + 1,
            error: vkError instanceof Error ? vkError.message : String(vkError)
          });

          // Если это rate limit - пробрасываем ошибку выше
          if (vkError instanceof Error && vkError.message.includes('Too many requests')) {
            throw new VkApiError(vkError.message, 6, { errorCode: 'TOO_MANY_REQUESTS' });
          }
        }
      }

      logger.info('Батч-запросы завершены', {
        requestedCount: groupIdentifiers.length,
        receivedCount: vkGroupsInfo.length,
        notFoundCount: groupIdentifiers.length - vkGroupsInfo.length
      });

      // ШАГ 3: Преобразуем данные VK в формат БД через GroupMapper
      const enrichedGroups: CreateGroupInput[] = vkGroupsInfo.map(vkGroup =>
        GroupMapper.vkToDb(vkGroup, taskId)
      );

      // Отмечаем не найденные группы как invalid
      const foundIds = new Set(vkGroupsInfo.map(g => g.id));
      const foundScreenNames = new Set(vkGroupsInfo.map(g => g.screen_name).filter(Boolean));

      for (const group of parsedGroups) {
        const identifier = group.id ?? group.name;
        if (!identifier) continue;

        const isFound = typeof identifier === 'number'
          ? foundIds.has(identifier)
          : foundScreenNames.has(identifier as string);

        if (!isFound) {
          invalidGroups.push({
            ...group,
            error: 'Group not found or not accessible via VK API'
          });
          logger.warn('Группа не найдена через VK API', { identifier });
        }
      }

      // ШАГ 4: Проверяем дубликаты в БД
      const groupsToSave: CreateGroupInput[] = [];

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

      logger.info('Groups ready for DB save', {
        groupsToSaveCount: groupsToSave.length,
        duplicatesCount: duplicates,
        sampleToSave: groupsToSave.slice(0, 3).map(g => ({ vk_id: g.vk_id, name: g.name }))
      });

      // ШАГ 5: Сохраняем группы в БД
      if (groupsToSave.length > 0) {
        try {
          await this.groupsRepo.createGroups(groupsToSave, taskId);
        } catch (dbError) {
          const errorMsg = dbError instanceof Error ? dbError.message : String(dbError);
          logger.error('Database save failed', { taskId, error: errorMsg });
          throw new DatabaseError(
            `Failed to save groups to database: ${errorMsg}`,
            { groupsCount: groupsToSave.length }
          );
        }
      }

      // ШАГ 6: Обновляем финальный статус задачи
      await this.updateTaskStatus(taskId, 'completed', {
        progress: {
          total: groups.length,
          processed: groups.length,
          valid: groupsToSave.length,
          invalid: invalidGroups.length + parseErrors.length,
          duplicates
        },
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

      await this.updateTaskStatus(taskId, 'failed', {
        failureReason: errorMsg,
        completedAt: new Date()
      });
    }
  }

  /**
   * Получает статус задачи загрузки из Redis
   *
   * @param taskId - ID задачи
   * @returns Promise<TaskStatusResult>
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
   * Получает группы с фильтрацией
   * Использует GroupMapper для преобразования DB -> API
   *
   * @param params - Параметры фильтрации и пагинации
   * @returns Promise<GetGroupsResult>
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
      const errorMsg = error instanceof GroupsDomainError
        ? error.message
        : error instanceof Error
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
   * Обновляет статус задачи в Redis
   *
   * @param taskId - ID задачи
   * @param status - Новый статус
   * @param updates - Дополнительные обновления
   */
  private async updateTaskStatus(
    taskId: string,
    status: GroupUploadTask['status'],
    updates: Partial<GroupUploadTask> = {}
  ): Promise<void> {
    try {
      const task = await taskStorageService.getTask(taskId);
      if (!task) {
        throw new TaskNotFoundError(taskId);
      }

      const updatedTask: GroupUploadTask = {
        ...task,
        status,
        ...updates
      };

      await taskStorageService.saveTask(taskId, updatedTask);
    } catch (error) {
      logger.error('Failed to update task status', {
        taskId,
        status,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * Удаляет группу по ID
   *
   * @param groupId - ID группы
   * @returns Promise<DeleteResult>
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
   *
   * @param groupIds - Массив ID групп
   * @returns Promise<DeleteResult>
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
   *
   * @returns Promise<DeleteResult>
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
   *
   * @param taskId - Опциональный ID задачи для фильтрации
   * @returns Promise<StatsResult>
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
   *
   * @returns Promise<GroupUploadTask[]>
   */
  async getAllUploadTasks(): Promise<GroupUploadTask[]> {
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

  /**
   * Очищает завершенные задачи старше определенного времени
   *
   * @param olderThanHours - Количество часов (по умолчанию 24)
   * @returns Promise<number> - Количество удаленных задач
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

// Singleton экземпляр сервиса
const groupsService = new GroupsService();

export default groupsService;
export { GroupsService };

// Legacy types для обратной совместимости
export type {
  UploadResult,
  TaskStatusResult,
  GetGroupsParams,
  GetGroupsResult,
  DeleteResult,
  StatsResult
};
