/**
 * @fileoverview PrismaGroupsRepository - реализация IGroupsRepository
 *
 * Infrastructure adapter для работы с группами через Prisma ORM.
 * Реализует Domain интерфейс IGroupsRepository.
 */

import { prisma } from '@infrastructure/config/prisma';
import { Prisma, GroupStatus as PrismaGroupStatus } from '@prisma/client';
import {
  IGroupsRepository,
  FindGroupsOptions,
  FindGroupsResult,
  GroupsStatistics
} from '@domain/repositories/IGroupsRepository';
import { Group, GroupId, VkId, GroupStatus } from '@domain/index';
import logger from '@infrastructure/utils/logger';

/**
 * Prisma реализация IGroupsRepository
 *
 * @description
 * Адаптер между Domain Layer и Prisma ORM.
 * Преобразует Domain Entities в Prisma модели и обратно.
 */
export class PrismaGroupsRepository implements IGroupsRepository {
  /**
   * Сохраняет группу (создает или обновляет)
   */
  async save(group: Group): Promise<void> {
    const data = group.toPersistence();

    try {
      await prisma.groups.upsert({
        where: {
          vkId: data.vk_id
        },
        update: {
          name: data.name,
          screenName: data.screen_name,
          photo50: data.photo_50,
          membersCount: data.members_count,
          isClosed: data.is_closed,
          description: data.description,
          status: data.status as PrismaGroupStatus,
          uploadedAt: data.uploaded_at
        },
        create: {
          vkId: data.vk_id,
          name: data.name,
          screenName: data.screen_name,
          photo50: data.photo_50,
          membersCount: data.members_count,
          isClosed: data.is_closed,
          description: data.description,
          status: data.status as PrismaGroupStatus,
          taskId: data.task_id,
          uploadedAt: data.uploaded_at
        }
      });

      logger.debug('Group saved', { vkId: data.vk_id });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to save group', { vkId: data.vk_id, error: errorMsg });
      throw new Error(`Failed to save group: ${errorMsg}`);
    }
  }

  /**
   * Сохраняет несколько групп батчем
   */
  async saveMany(groups: readonly Group[]): Promise<void> {
    if (groups.length === 0) {
      return;
    }

    try {
      const operations = groups.map(group => {
        const data = group.toPersistence();
        return prisma.groups.upsert({
          where: {
            vkId: data.vk_id
          },
          update: {
            name: data.name,
            screenName: data.screen_name,
            photo50: data.photo_50,
            membersCount: data.members_count,
            isClosed: data.is_closed,
            description: data.description,
            status: data.status as PrismaGroupStatus,
            uploadedAt: data.uploaded_at
          },
          create: {
            vkId: data.vk_id,
            name: data.name,
            screenName: data.screen_name,
            photo50: data.photo_50,
            membersCount: data.members_count,
            isClosed: data.is_closed,
            description: data.description,
            status: data.status as PrismaGroupStatus,
            taskId: data.task_id,
            uploadedAt: data.uploaded_at
          }
        });
      });

      await prisma.$transaction(operations);

      logger.info('Groups saved in batch', { count: groups.length });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to save groups batch', { count: groups.length, error: errorMsg });
      throw new Error(`Failed to save groups: ${errorMsg}`);
    }
  }

  /**
   * Находит группу по внутреннему ID
   */
  async findById(id: GroupId): Promise<Group | null> {
    try {
      const prismaGroup = await prisma.groups.findUnique({
        where: { id: id.value }
      });

      if (!prismaGroup) {
        return null;
      }

      return this.toDomain(prismaGroup);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to find group by ID', { id: id.value, error: errorMsg });
      throw new Error(`Failed to find group: ${errorMsg}`);
    }
  }

  /**
   * Находит группу по VK ID
   */
  async findByVkId(vkId: VkId): Promise<Group | null> {
    try {
      const prismaGroup = await prisma.groups.findUnique({
        where: { vkId: vkId.value }
      });

      if (!prismaGroup) {
        return null;
      }

      return this.toDomain(prismaGroup);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to find group by VK ID', { vkId: vkId.value, error: errorMsg });
      throw new Error(`Failed to find group: ${errorMsg}`);
    }
  }

  /**
   * Находит несколько групп по VK IDs
   */
  async findByVkIds(vkIds: readonly VkId[]): Promise<readonly Group[]> {
    if (vkIds.length === 0) {
      return [];
    }

    try {
      const vkIdValues = vkIds.map(id => id.value);
      const prismaGroups = await prisma.groups.findMany({
        where: {
          vkId: {
            in: vkIdValues
          }
        }
      });

      return prismaGroups.map(g => this.toDomain(g));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to find groups by VK IDs', { count: vkIds.length, error: errorMsg });
      throw new Error(`Failed to find groups: ${errorMsg}`);
    }
  }

  /**
   * Находит группы с фильтрацией и пагинацией
   */
  async findAll(options?: FindGroupsOptions): Promise<FindGroupsResult> {
    try {
      const limit = options?.limit || 20;
      const offset = options?.offset || 0;

      // Строим WHERE условие
      const where: Prisma.groupsWhereInput = {};

      // Фильтр по статусу
      if (options?.status && options.status !== 'all') {
        where.status = options.status as PrismaGroupStatus;
      }

      // Фильтр по поиску
      if (options?.search) {
        const searchConditions: Prisma.groupsWhereInput[] = [];

        // Поиск по ID если число
        if (!isNaN(Number(options.search))) {
          searchConditions.push({
            id: { equals: Number(options.search) }
          });
        }

        // Поиск по названию
        searchConditions.push({
          name: {
            contains: options.search,
            mode: 'insensitive'
          }
        });

        where.OR = searchConditions;
      }

      // Фильтр по taskId
      if (options?.taskId) {
        where.task_id = options.taskId;
      }

      // Сортировка
      const orderBy = this.buildOrderBy(options?.sortBy, options?.sortOrder);

      // Выполняем запросы параллельно
      const [prismaGroups, total] = await Promise.all([
        prisma.groups.findMany({
          where,
          take: limit,
          skip: offset,
          orderBy
        }),
        prisma.groups.count({ where })
      ]);

      const groups = prismaGroups.map(g => this.toDomain(g));
      const hasMore = offset + groups.length < total;

      return {
        groups,
        total,
        hasMore
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to find all groups', { options, error: errorMsg });
      throw new Error(`Failed to find groups: ${errorMsg}`);
    }
  }

  /**
   * Проверяет существование группы по VK ID
   */
  async exists(vkId: VkId): Promise<boolean> {
    try {
      const count = await prisma.groups.count({
        where: { vkId: vkId.value }
      });

      return count > 0;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to check group existence', { vkId: vkId.value, error: errorMsg });
      return false;
    }
  }

  /**
   * Удаляет группу по ID
   */
  async delete(id: GroupId): Promise<boolean> {
    try {
      await prisma.groups.delete({
        where: { id: id.value }
      });

      logger.info('Group deleted', { id: id.value });
      return true;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Record to delete does not exist')) {
        logger.warn('Group not found for deletion', { id: id.value });
        return false;
      }

      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete group', { id: id.value, error: errorMsg });
      throw new Error(`Failed to delete group: ${errorMsg}`);
    }
  }

  /**
   * Массовое удаление групп
   */
  async deleteMany(ids: readonly GroupId[]): Promise<number> {
    if (ids.length === 0) {
      return 0;
    }

    try {
      const idValues = ids.map(id => id.value);
      const result = await prisma.groups.deleteMany({
        where: {
          id: { in: idValues }
        }
      });

      logger.info('Groups deleted', { count: result.count });
      return result.count;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete groups', { count: ids.length, error: errorMsg });
      throw new Error(`Failed to delete groups: ${errorMsg}`);
    }
  }

  /**
   * Удаляет все группы
   */
  async deleteAll(): Promise<number> {
    try {
      const result = await prisma.groups.deleteMany({});

      logger.warn('All groups deleted', { count: result.count });
      return result.count;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete all groups', { error: errorMsg });
      throw new Error(`Failed to delete all groups: ${errorMsg}`);
    }
  }

  /**
   * Удаляет группы по ID задачи
   */
  async deleteByTaskId(taskId: string): Promise<number> {
    try {
      const result = await prisma.groups.deleteMany({
        where: { taskId: taskId }
      });

      logger.info('Groups deleted by task ID', { taskId, count: result.count });
      return result.count;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete groups by task ID', { taskId, error: errorMsg });
      throw new Error(`Failed to delete groups: ${errorMsg}`);
    }
  }

  /**
   * Получает статистику по группам
   */
  async getStatistics(taskId?: string): Promise<GroupsStatistics> {
    try {
      const where: Prisma.groupsWhereInput = taskId ? { taskId: taskId } : {};

      const stats = await prisma.groups.groupBy({
        by: ['status'],
        where,
        _count: { id: true }
      });

      let total = 0;
      let valid = 0;
      let invalid = 0;
      let duplicate = 0;

      stats.forEach(stat => {
        const count = stat._count.id;
        total += count;

        if (stat.status === 'valid') valid = count;
        else if (stat.status === 'invalid') invalid = count;
        else if (stat.status === 'duplicate') duplicate = count;
      });

      return { total, valid, invalid, duplicate };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get groups statistics', { taskId, error: errorMsg });
      throw new Error(`Failed to get statistics: ${errorMsg}`);
    }
  }

  /**
   * Подсчитывает количество групп
   */
  async count(options?: Omit<FindGroupsOptions, 'limit' | 'offset' | 'sortBy' | 'sortOrder'>): Promise<number> {
    try {
      const where: Prisma.groupsWhereInput = {};

      if (options?.status && options.status !== 'all') {
        where.status = options.status as PrismaGroupStatus;
      }

      if (options?.search) {
        where.name = {
          contains: options.search,
          mode: 'insensitive'
        };
      }

      if (options?.taskId) {
        where.task_id = options.taskId;
      }

      return await prisma.groups.count({ where });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to count groups', { error: errorMsg });
      throw new Error(`Failed to count groups: ${errorMsg}`);
    }
  }

  // ============ Private Helpers ============

  /**
   * Преобразует Prisma модель в Domain Entity
   */
  private toDomain(prismaGroup: any): Group {
    return Group.restore({
      id: GroupId.create(prismaGroup.id),
      vkId: VkId.create(prismaGroup.vk_id),
      name: prismaGroup.name,
      screenName: prismaGroup.screen_name,
      photo50: prismaGroup.photo_50,
      membersCount: prismaGroup.members_count,
      isClosed: prismaGroup.is_closed as 0 | 1 | 2,
      description: prismaGroup.description,
      status: GroupStatus.fromPrisma(prismaGroup.status),
      taskId: prismaGroup.task_id,
      uploadedAt: prismaGroup.uploaded_at
    });
  }

  /**
   * Строит orderBy для Prisma
   */
  private buildOrderBy(
    sortBy?: string,
    sortOrder?: string
  ): Prisma.groupsOrderByWithRelationInput {
    const order = sortOrder === 'asc' ? Prisma.SortOrder.asc : Prisma.SortOrder.desc;

    switch (sortBy) {
      case 'id':
        return { id: order };
      case 'name':
        return { name: order };
      case 'members_count':
        return { membersCount: order };
      case 'status':
        return { status: order };
      case 'vk_id':
        return { vkId: order };
      case 'uploaded_at':
      default:
        return { uploadedAt: order };
    }
  }
}
