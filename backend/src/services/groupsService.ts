/**
 * @fileoverview Groups Service - Рефакторированный сервис управления группами
 *
 * ✅ ВЫПОЛНЕНО:
 * - Разделен на специализированные handler'ы (Upload, Query, Delete)
 * - Сокращен с 750 до 100 строк
 * - Сохранена полная обратная совместимость с API
 * - Используется Dependency Injection pattern
 *
 * Архитектура:
 * - Domain Layer: types, schemas, errors, mappers
 * - Infrastructure Layer: TaskStorageService, BatchProcessor
 * - Service Layer: специализированные handler'ы
 * - Application Layer: этот фасад
 */

import groupsRepo from '@/repositories/groupsRepo';

// Handler'ы для разделения ответственности
import { GroupsUploadHandler, UploadResult } from './groups/GroupsUploadHandler';
import { GroupsQueryHandler, GetGroupsParams, GetGroupsResult, TaskStatusResult, StatsResult } from './groups/GroupsQueryHandler';
import { GroupsDeleteHandler, DeleteResult } from './groups/GroupsDeleteHandler';

/**
 * Сервис управления группами ВКонтакте
 *
 * Фасад над специализированными handler'ами:
 * - GroupsUploadHandler - загрузка и валидация групп
 * - GroupsQueryHandler - получение групп и статистики
 * - GroupsDeleteHandler - удаление групп и очистка задач
 */
class GroupsService {
  private uploadHandler: GroupsUploadHandler;
  private queryHandler: GroupsQueryHandler;
  private deleteHandler: GroupsDeleteHandler;

  constructor() {
    // Инициализируем handler'ы с Dependency Injection
    this.uploadHandler = new GroupsUploadHandler(groupsRepo);
    this.queryHandler = new GroupsQueryHandler(groupsRepo);
    this.deleteHandler = new GroupsDeleteHandler(groupsRepo);
  }

  // ============ Upload Operations ============

  /**
   * Загружает группы из файла с асинхронной обработкой
   *
   * @param filePath - Путь к файлу или Buffer с данными
   * @param encoding - Кодировка файла (utf-8, utf-16le, latin1, ascii)
   * @returns Promise<UploadResult> с taskId для отслеживания прогресса
   */
  async uploadGroups(filePath: string | Buffer, encoding: BufferEncoding = 'utf-8'): Promise<UploadResult> {
    return this.uploadHandler.uploadGroups(filePath, encoding);
  }

  // ============ Query Operations ============

  /**
   * Получает статус задачи загрузки из Redis
   */
  async getUploadStatus(taskId: string): Promise<TaskStatusResult> {
    return this.queryHandler.getUploadStatus(taskId);
  }

  /**
   * Получает группы с фильтрацией
   */
  async getGroups(params: GetGroupsParams): Promise<GetGroupsResult> {
    return this.queryHandler.getGroups(params);
  }

  /**
   * Получает статистику по группам
   */
  async getGroupsStats(taskId?: string): Promise<StatsResult> {
    return this.queryHandler.getGroupsStats(taskId);
  }

  /**
   * Получает все задачи загрузки для мониторинга
   */
  async getAllUploadTasks() {
    return this.queryHandler.getAllUploadTasks();
  }

  // ============ Delete Operations ============

  /**
   * Удаляет группу по ID
   */
  async deleteGroup(groupId: string): Promise<DeleteResult> {
    return this.deleteHandler.deleteGroup(groupId);
  }

  /**
   * Массовое удаление групп
   */
  async deleteGroups(groupIds: number[]): Promise<DeleteResult> {
    return this.deleteHandler.deleteGroups(groupIds);
  }

  /**
   * Удаляет все группы из БД
   * ВНИМАНИЕ: Опасная операция!
   */
  async deleteAllGroups(): Promise<DeleteResult> {
    return this.deleteHandler.deleteAllGroups();
  }

  /**
   * Очищает завершенные задачи старше определенного времени
   */
  async cleanupOldTasks(olderThanHours = 24): Promise<number> {
    return this.deleteHandler.cleanupOldTasks(olderThanHours);
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
