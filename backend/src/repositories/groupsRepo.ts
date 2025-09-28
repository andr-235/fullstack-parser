import { prisma } from '../config/prisma';
import { groups, Prisma, $Enums } from '@prisma/client';
import logger from '../utils/logger';

// Интерфейсы для запросов
interface GetGroupsParams {
  limit?: number;
  offset?: number;
  status?: string | undefined;
  search?: string | undefined;
  sortBy?: string;
  sortOrder?: string;
}

interface GroupsResponse {
  groups: groups[];
  total: number;
  pagination: {
    limit: number;
    offset: number;
    hasMore: boolean;
  };
}

interface GroupsStats {
  total: number;
  valid: number;
  invalid: number;
  duplicate: number;
}

interface CreateGroupInput {
  id?: number;
  name: string;
  status?: $Enums.GroupStatus;
}

class GroupsRepository {
  constructor() {
    // Prisma Client используется напрямую через импорт
  }

  /**
   * Создает группы в базе данных
   */
  async createGroups(groupsData: CreateGroupInput[], taskId: string): Promise<groups[]> {
    try {
      const createdGroups = await prisma.$transaction(
        groupsData.map(group =>
          prisma.groups.upsert({
            where: {
              id: group.id || 0  // fallback for groups without ID
            },
            update: {
              name: group.name,
              status: group.status || 'valid',
              uploaded_at: new Date()
            },
            create: {
              ...(group.id && { id: group.id }),
              name: group.name,
              status: group.status || 'valid',
              task_id: taskId,
              uploaded_at: new Date()
            }
          })
        )
      );

      logger.info('Groups created successfully', {
        taskId,
        count: createdGroups.length
      });

      return createdGroups;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to create groups', { taskId, error: errorMsg });
      throw new Error(`Failed to create groups: ${errorMsg}`);
    }
  }

  /**
   * Получает группы с фильтрацией
   */
  async getGroups(params: GetGroupsParams): Promise<GroupsResponse> {
    try {
      const {
        limit = 20,
        offset = 0,
        status = 'all',
        search = '',
        sortBy = 'uploaded_at',
        sortOrder = 'desc'
      } = params;

      // Строим условия WHERE
      const where: Prisma.groupsWhereInput = {};

      // Фильтр по статусу
      if (status !== 'all') {
        where.status = status as $Enums.GroupStatus;
      }

      // Поиск по ID или названию
      if (search) {
        const searchConditions = [];

        // Поиск по ID если это число
        if (!isNaN(Number(search))) {
          searchConditions.push({
            id: {
              equals: Number(search)
            }
          });
        }

        // Поиск по названию
        searchConditions.push({
          name: {
            contains: search,
            mode: 'insensitive' as const
          }
        });

        where.OR = searchConditions;
      }

      // Подготовка сортировки
      const prismaOrder = (sortOrder === 'asc' || sortOrder === 'ASC') ? Prisma.SortOrder.asc : Prisma.SortOrder.desc;
      const orderBy: Prisma.groupsOrderByWithRelationInput = {};
      if (sortBy === 'uploaded_at' || sortBy === 'uploadedAt') {
        orderBy.uploaded_at = prismaOrder;
      } else if (sortBy === 'name') {
        orderBy.name = prismaOrder;
      } else if (sortBy === 'status') {
        orderBy.status = prismaOrder;
      } else {
        orderBy.uploaded_at = Prisma.SortOrder.desc;
      }

      const [groups, total] = await prisma.$transaction([
        prisma.groups.findMany({
          where,
          take: parseInt(String(limit)),
          skip: parseInt(String(offset)),
          orderBy
        }),
        prisma.groups.count({ where })
      ]);

      return {
        groups,
        total,
        pagination: {
          limit: parseInt(String(limit)),
          offset: parseInt(String(offset)),
          hasMore: offset + groups.length < total
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get groups', { params, error: errorMsg });
      throw new Error(`Failed to get groups: ${errorMsg}`);
    }
  }

  /**
   * Получает группы по ID задачи (для обратной совместимости)
   */
  async getGroupsByTaskId(taskId: string, limit: number = 20, offset: number = 0): Promise<GroupsResponse> {
    try {
      const [groups, total] = await prisma.$transaction([
        prisma.groups.findMany({
          where: { task_id: taskId },
          take: parseInt(String(limit)),
          skip: parseInt(String(offset)),
          orderBy: { uploaded_at: 'desc' }
        }),
        prisma.groups.count({
          where: { task_id: taskId }
        })
      ]);

      return {
        groups,
        total,
        pagination: {
          limit: parseInt(String(limit)),
          offset: parseInt(String(offset)),
          hasMore: offset + groups.length < total
        }
      };
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get groups by task ID', { taskId, error: errorMsg });
      throw new Error(`Failed to get groups: ${errorMsg}`);
    }
  }

  /**
   * Получает группу по ID
   */
  async getGroupById(groupId: number): Promise<groups | null> {
    try {
      return await prisma.groups.findUnique({
        where: { id: groupId }
      });
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get group by ID', { groupId, error: errorMsg });
      throw new Error(`Failed to get group: ${errorMsg}`);
    }
  }

  /**
   * Обновляет статус группы
   */
  async updateGroupStatus(groupId: number, status: $Enums.GroupStatus): Promise<groups> {
    try {
      const updatedGroup = await prisma.groups.update({
        where: { id: groupId },
        data: { status }
      });

      return updatedGroup;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Record to update not found')) {
        throw new Error('Group not found');
      }
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update group status', { groupId, status, error: errorMsg });
      throw new Error(`Failed to update group status: ${errorMsg}`);
    }
  }

  /**
   * Удаляет группу по ID
   */
  async deleteGroup(groupId: number): Promise<boolean> {
    try {
      const deletedGroup = await prisma.groups.delete({
        where: { id: groupId }
      });

      logger.info('Group deleted successfully', { groupId, deleted: !!deletedGroup });
      return !!deletedGroup;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Record to delete does not exist')) {
        logger.info('Group not found for deletion', { groupId });
        return false;
      }
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete group', { groupId, error: errorMsg });
      throw new Error(`Failed to delete group: ${errorMsg}`);
    }
  }

  /**
   * Массовое удаление групп
   */
  async deleteGroups(groupIds: number[]): Promise<number> {
    try {
      const deleteResult = await prisma.groups.deleteMany({
        where: {
          id: {
            in: groupIds
          }
        }
      });

      logger.info('Groups deleted successfully', { groupIds, count: deleteResult.count });
      return deleteResult.count;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete groups', { groupIds, error: errorMsg });
      throw new Error(`Failed to delete groups: ${errorMsg}`);
    }
  }

  /**
   * Удаляет группы по ID задачи
   */
  async deleteGroupsByTaskId(taskId: string): Promise<number> {
    try {
      const deleteResult = await prisma.groups.deleteMany({
        where: { task_id: taskId }
      });

      logger.info('Groups deleted successfully', { taskId, count: deleteResult.count });
      return deleteResult.count;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete groups by task ID', { taskId, error: errorMsg });
      throw new Error(`Failed to delete groups: ${errorMsg}`);
    }
  }

  /**
   * Получает статистику по группам
   */
  async getGroupsStats(taskId?: string): Promise<GroupsStats> {
    try {
      const where: Prisma.groupsWhereInput = taskId ? { task_id: taskId } : {};

      const stats = await prisma.groups.groupBy({
        by: ['status'],
        where,
        _count: {
          id: true
        }
      });

      const result: GroupsStats = {
        total: 0,
        valid: 0,
        invalid: 0,
        duplicate: 0
      };

      stats.forEach((stat) => {
        const count = stat._count.id;
        result.total += count;
        if (stat.status === 'valid') result.valid = count;
        else if (stat.status === 'invalid') result.invalid = count;
        else if (stat.status === 'duplicate') result.duplicate = count;
      });

      return result;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get groups stats', { taskId, error: errorMsg });
      throw new Error(`Failed to get groups stats: ${errorMsg}`);
    }
  }

  /**
   * Проверяет существование группы
   */
  async groupExists(groupId: number): Promise<boolean> {
    try {
      const group = await prisma.groups.findUnique({
        where: { id: groupId },
        select: { id: true }
      });

      return !!group;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to check group existence', { groupId, error: errorMsg });
      return false;
    }
  }

  /**
   * Получает все уникальные ID групп
   */
  async getAllGroupIds(taskId?: string): Promise<number[]> {
    try {
      const where: Prisma.groupsWhereInput = taskId ? { task_id: taskId } : {};
      const groups = await prisma.groups.findMany({
        where,
        select: { id: true }
      });

      return groups.map(group => group.id).filter(id => id !== null) as number[];
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get group IDs', { taskId, error: errorMsg });
      throw new Error(`Failed to get group IDs: ${errorMsg}`);
    }
  }

  /**
   * Обновляет имя группы
   */
  async updateGroupName(groupId: number, name: string): Promise<groups> {
    try {
      const updatedGroup = await prisma.groups.update({
        where: { id: groupId },
        data: { name }
      });

      return updatedGroup;
    } catch (error) {
      if (error instanceof Error && error.message.includes('Record to update not found')) {
        throw new Error('Group not found');
      }
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update group name', { groupId, name, error: errorMsg });
      throw new Error(`Failed to update group name: ${errorMsg}`);
    }
  }
}

// Экспорт класса и экземпляра репозитория
export { GroupsRepository };
export default new GroupsRepository();

// Экспорт типов для совместимости
export type {
  GetGroupsParams,
  GroupsResponse,
  GroupsStats,
  CreateGroupInput
};