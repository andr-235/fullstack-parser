/**
 * @fileoverview GroupsUploadHandler - Обработчик загрузки и валидации групп
 *
 * Отвечает за:
 * - Парсинг файлов с группами
 * - Создание задач загрузки
 * - Валидацию через VK API
 * - Сохранение в БД
 */

import { v4 as uuidv4 } from 'uuid';
import { promises as fs } from 'fs';
import path from 'path';
import os from 'os';

import { FileParserFactory } from '@/utils/fileParser/FileParserFactory';
import vkIoService from '@/services/vkIoService';
import { GroupsRepository } from '@/repositories/groupsRepo';
import logger from '@/utils/logger';

import {
  GroupUploadTask,
  ParsedGroupInput,
  CreateGroupInput,
  VkGroupRaw
} from '@/domain/groups/types';
import {
  UploadGroupsRequestSchema,
  validateSchema
} from '@/domain/groups/schemas';
import {
  FileProcessingError,
  VkApiError,
  DatabaseError
} from '@/domain/groups/errors';
import { GroupMapper } from '@/domain/groups/mappers';

import { taskStorageService } from '@/infrastructure/storage/TaskStorageService';
import { createVkApiBatchProcessor } from '@/infrastructure/processing/BatchProcessor';

/**
 * Результат загрузки файла
 */
export interface UploadResult {
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

/**
 * Обработчик загрузки групп из файлов
 */
export class GroupsUploadHandler {
  constructor(private readonly groupsRepo: GroupsRepository) {}

  /**
   * Загружает группы из файла с асинхронной обработкой
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

      // Парсим файл
      const parser = FileParserFactory.create();
      const validationResult = await parser.validateFile(actualFilePath);

      if (!validationResult.isValid) {
        throw new FileProcessingError(
          validationResult.errors.join(', '),
          { errors: validationResult.errors }
        );
      }

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
          validGroups: 0,
          invalidGroups: parseResult.errors.length,
          duplicates: 0
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      const errorCode = error instanceof FileProcessingError ? error.code : 'UPLOAD_ERROR';

      logger.error('Upload groups failed', { filePath, error: errorMsg, errorCode });

      if (tempPath) {
        try {
          await fs.unlink(tempPath);
        } catch (unlinkError) {
          logger.warn('Failed to cleanup temp file', { tempPath });
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

      // ШАГ 2: Получаем информацию о группах через VK API
      const vkGroupsInfo = await this.fetchGroupsFromVkApi(groupIdentifiers);

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

      // ШАГ 4: Проверяем дубликаты и сохраняем в БД
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
   * Получает информацию о группах из VK API батчами
   */
  private async fetchGroupsFromVkApi(groupIdentifiers: Array<number | string>): Promise<VkGroupRaw[]> {
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

        // Преобразуем результаты VK API в VkGroupRaw
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

    return vkGroupsInfo;
  }

  /**
   * Обновляет статус задачи в Redis
   */
  private async updateTaskStatus(
    taskId: string,
    status: GroupUploadTask['status'],
    updates: Partial<GroupUploadTask> = {}
  ): Promise<void> {
    try {
      const task = await taskStorageService.getTask(taskId);
      if (!task) {
        logger.warn('Task not found for status update', { taskId, status });
        return;
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
}
