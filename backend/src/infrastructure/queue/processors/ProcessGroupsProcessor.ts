/**
 * @fileoverview ProcessGroupsProcessor - обработчик задач загрузки групп
 *
 * Processor для асинхронной обработки загруженных групп из файла.
 * Валидирует группы через VK API и сохраняет в БД.
 */

import { Job } from 'bullmq';
import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { IVkApiRepository } from '@domain/repositories/IVkApiRepository';
import { ITaskStorageRepository } from '@domain/repositories/ITaskStorageRepository';
import { Group, VkId, GroupStatus } from '@domain/index';
import { ParsedGroup } from '@domain/repositories/IFileParser';
import logger from '@infrastructure/utils/logger';

/**
 * Данные job'а для обработки групп
 */
export interface ProcessGroupsJobData {
  taskId: string;
  groups: readonly ParsedGroup[];
  errors: readonly string[];
}

/**
 * Результат обработки групп
 */
export interface ProcessGroupsJobResult {
  taskId: string;
  totalProcessed: number;
  validGroups: number;
  invalidGroups: number;
  duplicates: number;
  errors: readonly string[];
}

/**
 * Processor для обработки задач загрузки групп
 *
 * @description
 * Асинхронно обрабатывает загруженные группы:
 * 1. Валидирует через VK API
 * 2. Проверяет дубликаты
 * 3. Сохраняет в БД
 * 4. Обновляет прогресс
 */
export class ProcessGroupsProcessor {
  constructor(
    private readonly groupsRepository: IGroupsRepository,
    private readonly vkApiRepository: IVkApiRepository,
    private readonly taskStorageRepository: ITaskStorageRepository
  ) {}

  /**
   * Обрабатывает job загрузки групп
   */
  async process(job: Job<ProcessGroupsJobData>): Promise<ProcessGroupsJobResult> {
    const { taskId, groups, errors } = job.data;

    logger.info(`Processing groups job started`, {
      jobId: job.id,
      taskId,
      totalGroups: groups.length
    });

    try {
      // Шаг 1: Обновляем статус задачи
      await this.taskStorageRepository.updateTaskStatus(
        taskId,
        'processing',
        { startedAt: new Date() }
      );

      // Шаг 2: Извлекаем идентификаторы групп для VK API
      const groupIdentifiers = this.extractGroupIdentifiers(groups);

      if (groupIdentifiers.length === 0) {
        logger.warn(`No valid group identifiers found`, { taskId, jobId: job.id });

        await this.taskStorageRepository.updateTaskStatus(
          taskId,
          'completed',
          {
            completedAt: new Date()
          }
        );

        return {
          taskId,
          totalProcessed: 0,
          validGroups: 0,
          invalidGroups: 0,
          duplicates: 0,
          errors
        };
      }

      // Шаг 3: Получаем информацию о группах из VK API
      logger.info(`Fetching groups info from VK API`, {
        taskId,
        groupsCount: groupIdentifiers.length
      });

      const vkApiResult = await this.vkApiRepository.getGroupsInfo(groupIdentifiers);

      // Шаг 4: Обрабатываем успешные группы
      const groupsToSave: Group[] = [];
      let validCount = 0;
      let invalidCount = 0;
      let duplicatesCount = 0;
      const processingErrors: string[] = [...errors];

      for (const vkGroup of vkApiResult.successful) {
        try {
          // Проверяем дубликаты
          const vkId = VkId.create(vkGroup.id);
          const isDuplicate = await this.groupsRepository.exists(vkId);

          if (isDuplicate) {
            duplicatesCount++;
            logger.debug(`Duplicate group found`, { vkId: vkGroup.id, taskId });
            continue;
          }

          // Создаем Group Entity
          const group = Group.create({
            vkId,
            name: vkGroup.name,
            screenName: vkGroup.screenName,
            photo50: vkGroup.photo50,
            membersCount: vkGroup.membersCount,
            isClosed: vkGroup.isClosed,
            description: vkGroup.description,
            status: GroupStatus.valid(),
            taskId
          });

          groupsToSave.push(group);
          validCount++;
        } catch (error) {
          invalidCount++;
          const errorMsg = error instanceof Error ? error.message : String(error);
          processingErrors.push(`Group ${vkGroup.id}: ${errorMsg}`);
          logger.error(`Failed to create group entity`, {
            vkId: vkGroup.id,
            error: errorMsg
          });
        }
      }

      // Учитываем проваленные запросы к VK API
      for (const failed of vkApiResult.failed) {
        invalidCount++;
        processingErrors.push(`VK API failed for ${failed.identifier}: ${failed.error}`);
      }

      // Шаг 5: Сохраняем группы в БД
      if (groupsToSave.length > 0) {
        logger.info(`Saving groups to database`, {
          taskId,
          groupsCount: groupsToSave.length
        });

        for (let i = 0; i < groupsToSave.length; i++) {
          const group = groupsToSave[i];

          try {
            await this.groupsRepository.save(group);

            // Обновляем прогресс
            const progress = Math.round(((i + 1) / groupsToSave.length) * 100);
            await job.updateProgress(progress);

            await this.taskStorageRepository.updateTaskProgress(taskId, progress);

          } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            processingErrors.push(`Failed to save group ${group.vkId.value}: ${errorMsg}`);
            logger.error(`Failed to save group`, {
              vkId: group.vkId.value,
              error: errorMsg
            });
          }
        }
      }

      // Шаг 6: Завершаем задачу
      const result: ProcessGroupsJobResult = {
        taskId,
        totalProcessed: groups.length,
        validGroups: validCount,
        invalidGroups: invalidCount,
        duplicates: duplicatesCount,
        errors: processingErrors
      };

      await this.taskStorageRepository.updateTaskStatus(
        taskId,
        'completed',
        {
          completedAt: new Date()
        }
      );

      logger.info(`Processing groups job completed`, {
        jobId: job.id,
        taskId,
        ...result
      });

      return result;

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);

      logger.error(`Processing groups job failed`, {
        jobId: job.id,
        taskId,
        error: errorMsg
      });

      // Обновляем задачу как failed
      await this.taskStorageRepository.updateTaskStatus(
        taskId,
        'failed',
        {
          completedAt: new Date(),
          errors: [errorMsg]
        }
      );

      throw error;
    }
  }

  /**
   * Извлекает идентификаторы групп для VK API
   */
  private extractGroupIdentifiers(groups: readonly ParsedGroup[]): Array<VkId | string> {
    const identifiers: Array<VkId | string> = [];

    for (const group of groups) {
      if (group.id) {
        try {
          identifiers.push(VkId.create(group.id));
        } catch {
          // Игнорируем невалидные ID
          continue;
        }
      } else if (group.screenName) {
        identifiers.push(group.screenName);
      }
    }

    return identifiers;
  }
}
