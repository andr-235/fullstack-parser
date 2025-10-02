/**
 * @fileoverview UploadGroupsUseCase - Use Case загрузки групп
 *
 * USE CASE ПРИНЦИПЫ:
 * - Содержит бизнес-логику приложения
 * - Оркеструет Domain Entities и Repository
 * - Не зависит от Infrastructure деталей
 * - Использует Dependency Injection
 */

import { IGroupsRepository } from '@domain/repositories/IGroupsRepository';
import { IVkApiRepository } from '@domain/repositories/IVkApiRepository';
import { ITaskStorageRepository } from '@domain/repositories/ITaskStorageRepository';
import { IQueueRepository } from '@domain/repositories/IQueueRepository';
import {
  IFileParser,
  ParsedGroup,
  FileParseResult
} from '@domain/repositories/IFileParser';
import { Group, GroupUploadTask, VkId, GroupStatus, GroupId } from '@domain/index';
import { UploadGroupsInput, UploadGroupsOutput } from '@application/dto/UploadGroupsDto';
import { QUEUE_NAMES } from '@infrastructure/config/queue';

/**
 * Use Case: Загрузка групп из файла
 *
 * @description
 * Оркеструет процесс загрузки групп:
 * 1. Валидирует и парсит файл
 * 2. Создает задачу в хранилище
 * 3. Валидирует группы через VK API
 * 4. Проверяет дубликаты
 * 5. Сохраняет валидные группы в БД
 * 6. Обновляет прогресс задачи
 *
 * @example
 * ```typescript
 * const useCase = new UploadGroupsUseCase(
 *   groupsRepo,
 *   vkApiRepo,
 *   taskStorageRepo,
 *   fileParser
 * );
 *
 * const result = await useCase.execute({
 *   file: buffer,
 *   encoding: 'utf-8',
 *   fileName: 'groups.txt'
 * });
 * ```
 */
export class UploadGroupsUseCase {
  constructor(
    private readonly groupsRepository: IGroupsRepository,
    private readonly vkApiRepository: IVkApiRepository,
    private readonly taskStorageRepository: ITaskStorageRepository,
    private readonly fileParser: IFileParser,
    private readonly queueRepository: IQueueRepository
  ) {}

  /**
   * Выполняет Use Case
   */
  async execute(input: UploadGroupsInput): Promise<UploadGroupsOutput> {
    // Шаг 1: Валидация файла
    const validation = await this.fileParser.validateFile(input.file);
    if (!validation.isValid) {
      throw new Error(`File validation failed: ${validation.errors.join(', ')}`);
    }

    // Шаг 2: Парсинг файла
    const parseResult = await this.fileParser.parseGroupsFile(input.file, input.encoding);

    // Шаг 3: Создание задачи загрузки
    const task = GroupUploadTask.createNew({
      total: parseResult.groups.length,
      fileName: input.fileName,
      fileSize: input.file.length
    });

    // Добавляем ошибки парсинга в задачу
    parseResult.errors.forEach(error => task.addError(error));

    // Сохраняем задачу в хранилище
    await this.taskStorageRepository.saveTask(
      task.id.value,
      task.toPersistence()
    );

    // Шаг 4: Добавляем задачу в очередь для асинхронной обработки
    const jobId = await this.queueRepository.addJob(
      QUEUE_NAMES.PROCESS_GROUPS,
      'process-groups',
      {
        taskId: task.id.value,
        groups: parseResult.groups,
        errors: parseResult.errors
      },
      {
        priority: 5,
        attempts: 3,
        removeOnComplete: 100,
        removeOnFail: 50
      }
    );

    // Шаг 5: Возвращаем результат немедленно
    return {
      taskId: task.id.value,
      totalGroups: parseResult.groups.length,
      message: `Загрузка ${parseResult.groups.length} групп добавлена в очередь. Задача: ${task.id.toShort()}, Job: ${jobId}`
    };
  }

  // ПРИМЕЧАНИЕ: Старая логика processGroupsAsync перенесена в ProcessGroupsProcessor
  // Обработка теперь происходит асинхронно через BullMQ очередь
}
