/**
 * @fileoverview Интерфейс репозитория групп (Domain Layer)
 *
 * Определяет контракт для работы с группами без привязки к конкретной реализации.
 * Реализация находится в Infrastructure Layer.
 *
 * ПРИНЦИП DEPENDENCY INVERSION:
 * - Domain определяет ЧТО нужно (интерфейс)
 * - Infrastructure определяет КАК это делается (реализация)
 */

import { Group } from '@domain/entities/Group';
import { GroupId } from '@domain/value-objects/GroupId';
import { VkId } from '@domain/value-objects/VkId';
import { GroupStatus } from '@prisma/client';

/**
 * Параметры фильтрации при получении групп
 */
export interface FindGroupsOptions {
  readonly limit?: number;
  readonly offset?: number;
  readonly status?: GroupStatus | 'all';
  readonly search?: string;
  readonly sortBy?: 'uploaded_at' | 'name' | 'members_count' | 'status';
  readonly sortOrder?: 'asc' | 'desc';
  readonly taskId?: string;
}

/**
 * Результат получения групп с пагинацией
 */
export interface FindGroupsResult {
  readonly groups: readonly Group[];
  readonly total: number;
  readonly hasMore: boolean;
}

/**
 * Статистика по группам
 */
export interface GroupsStatistics {
  readonly total: number;
  readonly valid: number;
  readonly invalid: number;
  readonly duplicate: number;
}

/**
 * Интерфейс репозитория для работы с группами
 *
 * @description
 * Определяет все операции для работы с группами в системе.
 * Не содержит деталей реализации (SQL, Prisma и т.д.)
 *
 * @example
 * ```typescript
 * class PrismaGroupsRepository implements IGroupsRepository {
 *   async save(group: Group): Promise<void> {
 *     // Prisma implementation
 *   }
 * }
 * ```
 */
export interface IGroupsRepository {
  /**
   * Сохраняет группу в хранилище
   * Если группа существует - обновляет, если нет - создает (upsert)
   */
  save(group: Group): Promise<void>;

  /**
   * Сохраняет несколько групп одновременно (batch operation)
   */
  saveMany(groups: readonly Group[]): Promise<void>;

  /**
   * Находит группу по внутреннему ID
   */
  findById(id: GroupId): Promise<Group | null>;

  /**
   * Находит группу по VK ID
   */
  findByVkId(vkId: VkId): Promise<Group | null>;

  /**
   * Находит несколько групп по VK IDs
   */
  findByVkIds(vkIds: readonly VkId[]): Promise<readonly Group[]>;

  /**
   * Находит группы с фильтрацией и пагинацией
   */
  findAll(options?: FindGroupsOptions): Promise<FindGroupsResult>;

  /**
   * Проверяет существование группы по VK ID
   */
  exists(vkId: VkId): Promise<boolean>;

  /**
   * Удаляет группу по ID
   * @returns true если группа была удалена, false если не найдена
   */
  delete(id: GroupId): Promise<boolean>;

  /**
   * Массовое удаление групп
   * @returns количество удаленных групп
   */
  deleteMany(ids: readonly GroupId[]): Promise<number>;

  /**
   * Удаляет все группы (ОПАСНАЯ ОПЕРАЦИЯ!)
   * @returns количество удаленных групп
   */
  deleteAll(): Promise<number>;

  /**
   * Удаляет группы по ID задачи загрузки
   * @returns количество удаленных групп
   */
  deleteByTaskId(taskId: string): Promise<number>;

  /**
   * Получает статистику по группам
   */
  getStatistics(taskId?: string): Promise<GroupsStatistics>;

  /**
   * Подсчитывает количество групп
   */
  count(options?: Omit<FindGroupsOptions, 'limit' | 'offset' | 'sortBy' | 'sortOrder'>): Promise<number>;
}
