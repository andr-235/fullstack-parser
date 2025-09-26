import { Group, GroupAttributes, GroupCreationAttributes, GroupStatus } from '../models/group';
import { Op } from 'sequelize';
import logger from '../utils/logger';

// Интерфейсы для запросов
interface GetGroupsParams {
  limit?: number;
  offset?: number;
  status?: string;
  search?: string;
  sortBy?: string;
  sortOrder?: string;
}

interface GroupsResponse {
  groups: Group[];
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
  status?: GroupStatus;
}

class GroupsRepository {
  private Group: typeof Group;

  constructor() {
    this.Group = Group;
  }

  /**
   * Создает группы в базе данных
   */
  async createGroups(groups: CreateGroupInput[], taskId: string): Promise<Group[]> {
    try {
      const groupsToCreate = groups.map(group => ({
        id: group.id,
        name: group.name,
        status: group.status || 'valid' as GroupStatus,
        taskId: taskId,
        uploadedAt: new Date()
      }));

      const createdGroups = await this.Group.bulkCreate(groupsToCreate as GroupCreationAttributes[], {
        ignoreDuplicates: true
      });

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
        sortBy = 'uploadedAt',
        sortOrder = 'desc'
      } = params;

      // Строим условия WHERE
      const where: Record<string, any> = {};

      // Фильтр по статусу
      if (status !== 'all') {
        where.status = status;
      }

      // Поиск по ID или названию
      if (search) {
        where[Op.or] = [
          { id: { [Op.like]: `%${search}%` } },
          { name: { [Op.like]: `%${search}%` } }
        ];
      }

      // Сортировка
      const order: [string, string][] = [[sortBy, sortOrder.toUpperCase()]];

      const { count, rows } = await this.Group.findAndCountAll({
        where,
        limit: parseInt(String(limit)),
        offset: parseInt(String(offset)),
        order
      });

      return {
        groups: rows,
        total: count,
        pagination: {
          limit: parseInt(String(limit)),
          offset: parseInt(String(offset)),
          hasMore: offset + rows.length < count
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
      const { count, rows } = await this.Group.findAndCountAll({
        where: { taskId },
        limit: parseInt(String(limit)),
        offset: parseInt(String(offset)),
        order: [['uploadedAt', 'DESC']]
      });

      return {
        groups: rows,
        total: count,
        pagination: {
          limit: parseInt(String(limit)),
          offset: parseInt(String(offset)),
          hasMore: offset + rows.length < count
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
  async getGroupById(groupId: number): Promise<Group | null> {
    try {
      return await this.Group.findByPk(groupId);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to get group by ID', { groupId, error: errorMsg });
      throw new Error(`Failed to get group: ${errorMsg}`);
    }
  }

  /**
   * Обновляет статус группы
   */
  async updateGroupStatus(groupId: number, status: GroupStatus): Promise<Group> {
    try {
      const [affectedRows] = await this.Group.update(
        { status },
        { where: { id: groupId } }
      );

      if (affectedRows === 0) {
        throw new Error('Group not found');
      }

      const updatedGroup = await this.getGroupById(groupId);
      if (!updatedGroup) {
        throw new Error('Group not found after update');
      }

      return updatedGroup;
    } catch (error) {
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
      const deletedCount = await this.Group.destroy({
        where: { id: groupId }
      });

      logger.info('Group deleted successfully', { groupId, deleted: deletedCount > 0 });
      return deletedCount > 0;
    } catch (error) {
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
      const deletedCount = await this.Group.destroy({
        where: { id: { [Op.in]: groupIds } }
      });

      logger.info('Groups deleted successfully', { groupIds, count: deletedCount });
      return deletedCount;
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
      const deletedCount = await this.Group.destroy({
        where: { taskId }
      });

      logger.info('Groups deleted successfully', { taskId, count: deletedCount });
      return deletedCount;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to delete groups by task ID', { taskId, error: errorMsg });
      throw new Error(`Failed to delete groups: ${errorMsg}`);
    }
  }

  /**
   * Получает статистику по группам
   */
  async getGroupsStats(taskId: string): Promise<GroupsStats> {
    try {
      const stats = await Group.findAll({
        where: { taskId },
        attributes: [
          'status',
          [Group.sequelize!.fn('COUNT', Group.sequelize!.col('id')), 'count']
        ],
        group: ['status'],
        raw: true
      }) as any[];

      const result: GroupsStats = {
        total: 0,
        valid: 0,
        invalid: 0,
        duplicate: 0
      };

      stats.forEach((stat: any) => {
        const count = parseInt(stat.count);
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
      const count = await this.Group.count({
        where: { id: groupId }
      });

      return count > 0;
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
      const where = taskId ? { taskId } : {};
      const groups = await this.Group.findAll({
        where,
        attributes: ['id'],
        raw: true
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
  async updateGroupName(groupId: number, name: string): Promise<Group> {
    try {
      const [affectedRows] = await this.Group.update(
        { name },
        { where: { id: groupId } }
      );

      if (affectedRows === 0) {
        throw new Error('Group not found');
      }

      const updatedGroup = await this.getGroupById(groupId);
      if (!updatedGroup) {
        throw new Error('Group not found after update');
      }

      return updatedGroup;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Failed to update group name', { groupId, name, error: errorMsg });
      throw new Error(`Failed to update group name: ${errorMsg}`);
    }
  }
}

export default new GroupsRepository();